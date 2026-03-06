
## 1. core/schema.py

"""
数据结构定义模块
定义生物芯片设计的所有数据模型
"""
from pydantic import BaseModel, Field


class ComponentInstance(BaseModel):
    """元件实例"""
    inst_id: str = Field(description="格式：U+3~6位数字")
    lib_id: str = Field(description="来自元件库的id")
    role: str = Field(description="角色")
    domain: str = Field(description="功能域")
    phase: str = Field(description="阶段")
    ports_liquid: str = Field(default="")
    ports_air: str = Field(default="")
    ports_act: str = Field(default="")
    ports_thermal: str = Field(default="")
    ports_magnetic: str = Field(default="")
    reagent_name: str = Field(default="")
    reagent_volume_uL: str = Field(default="0")
    reagent_state: str = Field(default="empty")
    param_override: str = Field(default="")


class Connection(BaseModel):
    """连接关系"""
    edge_id: str = Field(description="格式：E+3~6位数字")
    from_inst: str = Field(description="源ID")
    from_port: str = Field(description="源端口")
    to_inst: str = Field(description="目标ID")
    to_port: str = Field(description="目标端口")
    channel: str = Field(description="通道类型")
    domain: str = Field(description="连接域")
    phase: str = Field(description="连接阶段")


class OperationStep(BaseModel):
    """操作步骤"""
    step_id: int = Field(description="步骤ID")
    action: str = Field(description="动作类型")
    target_inst: str = Field(description="目标ID")
    target_port: str = Field(default="")
    value: str = Field(default="")
    duration_s: int = Field(description="持续时间")
    depends_on: str = Field(default="")
    domain: str = Field(description="操作域")
    phase: str = Field(description="操作阶段")


class BioChipDesign(BaseModel):
    """生物芯片完整设计"""
    reasoning: str = Field(description="设计/审查的思路说明")
    instances: list[ComponentInstance]
    connections: list[Connection]
    plan: list[OperationStep]
