# server.py
import os
import json
import time
import uuid
import threading
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from core import create_compiler
from core.schema import BioChipDesign
from draw.renderer import draw_chip


# -----------------------------
# In-memory stores (MVP)
# -----------------------------
EXECUTOR = ThreadPoolExecutor(max_workers=4)
STORE_LOCK = threading.Lock()

JOBS: Dict[str, Dict[str, Any]] = {}
COMPILES: Dict[str, Dict[str, Any]] = {}

HISTORY_DIR = Path(os.getenv("HISTORY_DIR", "./history"))
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def make_history_dirname(compile_id: str) -> str:
    local_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{local_ts}_{compile_id}"


def write_text_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json_file(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def persist_compile_artifacts(
    compile_id: str,
    protocol_text: str,
    draft_data: dict,
    final_data: dict,
    stats: dict,
    evidence: List[dict],
    trace: List[dict],
    created_at: str,
) -> dict:
    """
    宽松模式：
    - protocol / draft / final 一定保存
    - draw_chip 失败不会让整个 compile 失败
    - 失败信息写入 meta.json 和返回结果
    """
    folder_name = make_history_dirname(compile_id)
    run_dir = HISTORY_DIR / folder_name
    run_dir.mkdir(parents=True, exist_ok=True)

    protocol_path = run_dir / "protocol.txt"
    draft_path = run_dir / "draft.json"
    final_path = run_dir / "final.json"
    scheme_path = run_dir / "scheme.png"
    meta_path = run_dir / "meta.json"

    # 1) 保存协议文本和 JSON
    write_text_file(protocol_path, protocol_text)
    write_json_file(draft_path, draft_data)
    write_json_file(final_path, final_data)

    # 2) 宽松模式绘图
    draw_ok = True
    draw_error = None
    try:
        draw_chip(final_data, str(scheme_path))
    except Exception as e:
        draw_ok = False
        draw_error = str(e)

    # 3) 保存 meta 信息
    meta = {
        "compile_id": compile_id,
        "created_at": created_at,
        "history_dir": str(run_dir),
        "folder_name": folder_name,
        "paths": {
            "protocol": str(protocol_path),
            "draft": str(draft_path),
            "final": str(final_path),
            "scheme": str(scheme_path) if draw_ok else None,
            "meta": str(meta_path),
        },
        "draw": {
            "ok": draw_ok,
            "error": draw_error,
        },
        "stats": stats,
        "evidence": evidence,
        "trace": trace,
    }
    write_json_file(meta_path, meta)

    return {
        "history_dir": str(run_dir),
        "folder_name": folder_name,
        "files": {
            "protocol": str(protocol_path),
            "draft": str(draft_path),
            "final": str(final_path),
            "scheme": str(scheme_path) if draw_ok else None,
            "meta": str(meta_path),
        },
        "draw": {
            "ok": draw_ok,
            "error": draw_error,
        }
    }


# -----------------------------
# Request / Response schemas
# -----------------------------
class ModelsConfig(BaseModel):
    chat_model: str = "DeepSeek-V3.2"
    embed_model: str = "GLM-Embedding-2"
    temperature: float = 0.0


class CompilePaths(BaseModel):
    compiler_prompt_path: str = "./data/compiler_prompt.md"
    verifier_prompt_path: str = "./data/verifier_prompt.md"
    db_path: str = "./chroma_db"


class CompileOptions(BaseModel):
    k: int = 4
    return_draft: bool = True
    trace: bool = True


class CompileRequest(BaseModel):
    protocol_text: str = Field(min_length=1)
    models: ModelsConfig = ModelsConfig()
    paths: CompilePaths = CompilePaths()
    options: CompileOptions = CompileOptions()


class DrawRequest(BaseModel):
    chip_data: Dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    type: str
    status: str
    progress: Dict[str, Any]
    timestamps: Dict[str, Any]
    result_ref: Optional[Dict[str, str]] = None
    error: Optional[Dict[str, Any]] = None


class CompileResultResponse(BaseModel):
    compile_id: str
    protocol_text: str
    draft: dict
    final: dict
    stats: dict
    diff: dict
    evidence: List[dict] = []
    trace: List[dict] = []
    artifacts: Optional[dict] = None
    created_at: Optional[str] = None
    status: Optional[str] = None


class HistoryItem(BaseModel):
    compile_id: str
    created_at: str
    status: str
    protocol_preview: str
    duration_ms: int


class HistoryListResponse(BaseModel):
    items: List[HistoryItem]


# -----------------------------
# Core runner
# -----------------------------
def run_compile_job(job_id: str, req: CompileRequest):
    start_ts = time.time()

    def set_progress(stage: str, msg: str, pct: int):
        with STORE_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            job["progress"] = {"stage": stage, "message": msg, "percent": pct}
            job["updated_at"] = now_iso()

    def is_cancelled() -> bool:
        with STORE_LOCK:
            return bool(JOBS.get(job_id, {}).get("cancelled", False))

    try:
        with STORE_LOCK:
            JOBS[job_id]["status"] = "running"
            JOBS[job_id]["started_at"] = now_iso()

        set_progress("rag", "Retrieving knowledge (RAG)...", 10)
        if is_cancelled():
            raise RuntimeError("JOB_CANCELLED")

        api_base = os.getenv("API_BASE")
        api_key = os.getenv("API_KEY")
        if not api_base or not api_key:
            raise RuntimeError("CONFIG_MISSING: API_BASE/API_KEY")

        compiler = create_compiler(
            api_base=api_base,
            api_key=api_key,
            chat_model=req.models.chat_model,
            embed_model=req.models.embed_model,
            db_path=req.paths.db_path,
            compiler_prompt_path=req.paths.compiler_prompt_path,
            verifier_prompt_path=req.paths.verifier_prompt_path,
            temperature=req.models.temperature,
        )

        # Step 0: retrieve context (and collect evidence)
        context_str, doc_count = compiler.retrieve_knowledge(req.protocol_text)

        evidence: List[dict] = []
        for block in context_str.split("\n\n--- Ref "):
            if not block.strip():
                continue
            b = block if block.startswith("--- Ref ") else ("--- Ref " + block)
            lines = b.splitlines()
            header = lines[0].strip()
            snippet = "\n".join(lines[1:])[:400]
            evidence.append({
                "source": header.replace("--- ", "").replace(" ---", ""),
                "score": 1.0,
                "snippet": snippet,
                "location": "knowledge_base"
            })

        set_progress("generator", "Generating draft design (Generator)...", 40)
        if is_cancelled():
            raise RuntimeError("JOB_CANCELLED")

        draft_design, gen_time = compiler.generate_draft(req.protocol_text, context_str)

        set_progress("verifier", "Verifying and refining (Verifier)...", 75)
        if is_cancelled():
            raise RuntimeError("JOB_CANCELLED")

        final_design, ver_time = compiler.verify_and_refine(draft_design, context_str)

        set_progress("done", "Completed", 100)

        compile_id = new_id("compile")
        created_at = now_iso()
        duration_ms = int((time.time() - start_ts) * 1000)

        draft_data = draft_design.model_dump()
        final_data = final_design.model_dump()

        # -----------------------------
        # Diff computation (MVP)
        # -----------------------------
        draft_inst_ids = {x.get("inst_id") for x in draft_data.get("instances", [])}
        final_inst_ids = {x.get("inst_id") for x in final_data.get("instances", [])}

        draft_edge_ids = {x.get("edge_id") for x in draft_data.get("connections", [])}
        final_edge_ids = {x.get("edge_id") for x in final_data.get("connections", [])}

        instances_added = sorted(list(final_inst_ids - draft_inst_ids))
        instances_removed = sorted(list(draft_inst_ids - final_inst_ids))

        connections_added = sorted(list(final_edge_ids - draft_edge_ids))
        connections_removed = sorted(list(draft_edge_ids - final_edge_ids))

        stats = {
            "doc_count": doc_count,
            "gen_time": gen_time,
            "ver_time": ver_time,
            "draft_instances": len(draft_design.instances),
            "final_instances": len(final_design.instances),
            "draft_connections": len(draft_design.connections),
            "final_connections": len(final_design.connections),
            "duration_ms": duration_ms
        }

        trace = [
            {"stage": "rag", "doc_count": doc_count},
            {"stage": "generator", "elapsed": gen_time},
            {"stage": "verifier", "elapsed": ver_time},
        ]

        # -----------------------------
        # Persist artifacts (lenient mode)
        # -----------------------------
        artifact_info = persist_compile_artifacts(
            compile_id=compile_id,
            protocol_text=req.protocol_text,
            draft_data=draft_data,
            final_data=final_data,
            stats=stats,
            evidence=evidence,
            trace=trace,
            created_at=created_at,
        )

        result = {
            "compile_id": compile_id,
            "protocol_text": req.protocol_text,
            "draft": draft_data,
            "final": final_data,
            "stats": stats,
            "diff": {
                "instances_added": instances_added,
                "instances_removed": instances_removed,
                "connections_added": connections_added,
                "connections_removed": connections_removed,
                "draft_reasoning_preview": (draft_design.reasoning or "")[:200],
                "final_reasoning_preview": (final_design.reasoning or "")[:200],
            },
            "evidence": evidence,
            "trace": trace,
            "artifacts": artifact_info,
            "created_at": created_at,
            "status": "succeeded",
        }

        with STORE_LOCK:
            COMPILES[compile_id] = result
            JOBS[job_id]["status"] = "succeeded"
            JOBS[job_id]["finished_at"] = now_iso()
            JOBS[job_id]["result_ref"] = {"kind": "compile", "id": compile_id}

    except Exception as e:
        code = "INTERNAL_ERROR"
        msg = str(e)

        if msg == "JOB_CANCELLED":
            code = "JOB_CANCELLED"
            msg = "Job cancelled by user"
        elif msg.startswith("CONFIG_MISSING"):
            code = "CONFIG_MISSING"
        elif "validation" in msg.lower():
            code = "LLM_STRUCTURED_OUTPUT_ERROR"

        with STORE_LOCK:
            if job_id in JOBS:
                JOBS[job_id]["status"] = "failed" if code != "JOB_CANCELLED" else "cancelled"
                JOBS[job_id]["finished_at"] = now_iso()
                JOBS[job_id]["error"] = {"code": code, "message": msg}


# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="MicroChip Designer API", version="0.1.0")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "biochip-agent", "version": "0.1.0", "time": now_iso()}


@app.get("/api/v1/meta/models")
def meta_models():
    chat = os.getenv("llm_model_name", "DeepSeek-V3.2")
    emb = os.getenv("embedding_model_name", "GLM-Embedding-2")
    temp = float(os.getenv("temperature", "0.0"))

    return {
        "chat_models": [chat],
        "embedding_models": [emb],
        "defaults": {
            "chat_model": chat,
            "embedding_model": emb,
            "temperature": temp
        }
    }


@app.post("/api/v1/compile", response_model=JobResponse)
def create_compile(req: CompileRequest):
    if not req.models.chat_model:
        req.models.chat_model = os.getenv("llm_model_name", "DeepSeek-V3.2")
    if not req.models.embed_model:
        req.models.embed_model = os.getenv("embedding_model_name", "GLM-Embedding-2")
    if req.models.temperature is None:
        req.models.temperature = float(os.getenv("temperature", "0.0"))

    job_id = new_id("job")
    with STORE_LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "type": "compile",
            "status": "queued",
            "progress": {"stage": "queued", "message": "Queued", "percent": 0},
            "created_at": now_iso(),
            "started_at": None,
            "finished_at": None,
            "updated_at": now_iso(),
            "cancelled": False,
            "result_ref": None,
            "error": None,
            "request": req.model_dump(),
        }

    EXECUTOR.submit(run_compile_job, job_id, req)
    return JobResponse(job_id=job_id, status="queued")


@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str):
    with STORE_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        resp = {
            "job_id": job["job_id"],
            "type": job["type"],
            "status": job["status"],
            "progress": job["progress"],
            "timestamps": {
                "created_at": job["created_at"],
                "started_at": job["started_at"],
                "finished_at": job["finished_at"],
                "updated_at": job["updated_at"],
            },
            "result_ref": job.get("result_ref"),
            "error": job.get("error"),
        }
        return resp


@app.post("/api/v1/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    with STORE_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job["cancelled"] = True
        job["updated_at"] = now_iso()
    return {"job_id": job_id, "status": "cancelling"}


@app.get("/api/v1/compile/{compile_id}/result", response_model=CompileResultResponse)
def get_compile_result(compile_id: str):
    with STORE_LOCK:
        data = COMPILES.get(compile_id)
        if not data:
            raise HTTPException(status_code=404, detail="Compile result not found")
        return data


@app.get("/api/v1/history", response_model=HistoryListResponse)
def list_history():
    with STORE_LOCK:
        items: List[HistoryItem] = []
        for compile_id, data in sorted(COMPILES.items(), key=lambda kv: kv[1].get("created_at", ""), reverse=True):
            protocol = data.get("protocol_text", "")
            preview = protocol.strip().replace("\n", " ")[:80]
            items.append(HistoryItem(
                compile_id=compile_id,
                created_at=data.get("created_at", ""),
                status=data.get("status", "succeeded"),
                protocol_preview=preview,
                duration_ms=int(data.get("stats", {}).get("duration_ms", 0)),
            ))
        return {"items": items}


@app.get("/api/v1/history/{compile_id}", response_model=CompileResultResponse)
def history_detail(compile_id: str):
    return get_compile_result(compile_id)


@app.post("/api/v1/draw")
def draw_layout(req: DrawRequest):
    """
    输入：chip_data JSON
    输出：PNG 文件
    这是即时绘图接口，不写入 history
    """
    temp_dir = HISTORY_DIR / "_tmp_draw"
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_path = temp_dir / f"{new_id('layout')}.png"

    try:
        draw_chip(req.chip_data, str(out_path))
        return FileResponse(
            str(out_path),
            media_type="image/png",
            filename="microfluidic_layout.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DRAW_FAILED: {e}")


@app.get("/api/v1/compile/{compile_id}/layout.png")
def draw_layout_from_compile(compile_id: str):
    """
    优先返回历史目录里已保存的 scheme.png
    如果不存在，则尝试基于 final JSON 即时生成一张临时图
    """
    with STORE_LOCK:
        data = COMPILES.get(compile_id)
        if not data:
            raise HTTPException(status_code=404, detail="Compile result not found")

    artifacts = data.get("artifacts") or {}
    files = artifacts.get("files") or {}
    scheme_path = files.get("scheme")

    if scheme_path and os.path.exists(scheme_path):
        return FileResponse(
            scheme_path,
            media_type="image/png",
            filename="microfluidic_layout.png"
        )

    final_data = data.get("final", {})
    temp_dir = HISTORY_DIR / "_tmp_draw"
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_path = temp_dir / f"{compile_id}.png"

    try:
        draw_chip(final_data, str(out_path))
        return FileResponse(
            str(out_path),
            media_type="image/png",
            filename="microfluidic_layout.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DRAW_FAILED: {e}")


# 最后再挂载静态站点到根路径
if os.path.isdir("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/index.html")
