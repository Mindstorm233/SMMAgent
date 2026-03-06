# IR知识库

## 元件库文字说明与JSON表示

### （一）基元（Primitives-P）

#### P1 — OUT（预存-按需输出单元）

- **用途**：把试剂预先密封存储在管内，需要时通过按压触发一次性释放并推送到下游，语义上类似“预充电电容/电流源”。
- **关键参数（mm）**：适配 `d=4/6`；外径约束 `D≥6/8`；长度 `H=40–60`；结构尺寸 `A=0.5, B=0.5, C≥1.2`。
- **材料/工艺要点**：依赖被动胶塞密封；推荐胶塞硬度 `45 Shore A`，干涉配合 `0.4 mm`（兼顾低驱动力和密封防漏）。
- **接口信息**：液体入口 `0`；液体输出 `1`；气口 `0`。
- **外部执行/环境需求**：需要外部执行器（自上而下按压/推进活塞）触发释放；无特定环境控制要求。
- **推荐搭配**：常与 `IN/OUT`（转移/合并）、`ON–OFF`（路由门控）、`Air Vent`（空气补偿）一起用。
- **操作步骤**：
  1. **存储态**：底部胶塞封闭，试剂密封在腔内；
  2. **释放态**：按压推动/解除胶塞密封，试剂被推送到下游。
- **注意事项**：困气会引起瞬态压力/流量尖峰，影响计量与稳定性，必要时配合空气补偿/排气设计。
- **JSON表示**：

```json
{
    "id": "P1",
    "category": "primitive",
    "name": "OUT",
    "element_type": "1D foundational unit",
    "element_properties": "preloaded storage + on-demand discharge; capacitor/current-source-like semantic",
    "primary_purpose": "store reagent in-tube and release once on actuation to downstream",
    "parameters_mm": "d=4/6; D>=6/8; H=40-60; A=0.5; B=0.5; C>=1.2",
    "parameters_material_process": "passive rubber plug; recommended hardness=45 Shore A; interference fit=0.4",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "one downstream liquid outlet; reagent preloaded in chamber",
    "external_actuation_required": "yes; vertical press/plunger displacement to trigger plug release and push liquid",
    "external_environment_control_required": "no specific; depends on downstream domain",
    "recommended_with_other_elements": "commonly paired with IN/OUT (merging, metering, mixing), ON-OFF valve (routing), air compensation/vent when needed",
    "operation_steps": "State0: sealed storage by passive plug; State1: press to move/trigger plug and push liquid out to downstream",
    "notes": "shared constraints: sealing vs actuation-force tradeoff; minimize entrapped air to avoid transient spikes"
}
```

------

#### P2 — Sequential OUT（级联顺序输出单元）

- **用途**：多个 OUT 级联，实现多种试剂**按顺序依次释放**，用于多步流程按顺序加样。
- **关键参数（mm）**：`d=4/6; D≥6/8; H=40–60; A=0.5; B=0.5; C≥1.2; h≥20`（h 为级联/行程相关约束）。
- **接口信息**：液体入口 `0`；液体输出 `1`；气口 `0`（内部有多段储液）。
- **外部执行/环境需求**：需要外部按压，行程推进触发下一段释放；无特定环境控制。
- **推荐搭配**：常用于 `M4（大体积合并）` 之前，或作为“多试剂有序加样源”；复杂链路建议加 `Air Vent` 稳定释放。
- **操作步骤**：初态所有段封存 → 第一次按压释放第 1 段 → 继续按压依次释放第 2 段…直到最后一段。
- **注意事项**：顺序由几何与行程编码，需避免困气带来的突发高流速。
- **JSON表示**：

```json
{
    "id": "P2",
    "category": "primitive",
    "name": "Sequential OUT",
    "element_type": "1D foundational unit",
    "element_properties": "cascaded OUT units with sequential release behavior",
    "primary_purpose": "sequentially release multiple preloaded reagents in a defined order",
    "parameters_mm": "d=4/6; D>=6/8; H=40-60; A=0.5; B=0.5; C>=1.2; h>=20",
    "parameters_material_process": "passive rubber plug(s) per stage",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "single downstream outlet; multiple internal staged reservoirs",
    "external_actuation_required": "yes; continued press/stroke advances through stages",
    "external_environment_control_required": "no specific; depends on downstream domain",
    "recommended_with_other_elements": "often used before merging/mixing domains; combine with air compensation to stabilize discharge",
    "operation_steps": "State0: all stages sealed; Step1: first press releases stage1; Step2: continued press/extra stroke releases stage2... until final stage",
    "notes": "order is encoded by geometry/stroke; avoid entrapped air for stable sequential delivery"
}
```

------

#### P3 — IN（单向输入/吸入单元）

- **用途**：将外部样本/试剂引入管内，强调压力平衡以实现顺畅吸入；语义接近“单向输入”。
- **关键参数（mm）**：`d=4/6; D≥6/8; H=40–60; A≥0.7; B=2; L=9.5`。
- **接口信息**：液体入口 `1`；液体输出 `0`；气口 `1`（用于均压/排气）。
- **外部执行/环境需求**：需要外部按压（轻压对齐沟槽/通道、再压锁定）；环境无特定要求。
- **推荐搭配**：常与 `ON–OFF` 做路由选择；与 `IN/OUT` 或 `OUT` 做转移链；建议配合排气/空气补偿策略。
- **操作步骤**：
  1. 初态活塞封闭通路；
  2. 轻压对齐环形槽与入口通道，同时打开气路均压 → 液体进入；
  3. 继续下压错位重新封闭，实现吸入后锁定。
- **注意事项**：气体管理直接影响吸入稳定性与重复性。
- **JSON表示**：

```json
{
    "id": "P3",
    "category": "primitive",
    "name": "IN",
    "element_type": "1D foundational unit",
    "element_properties": "unidirectional intake with pressure equalization via air path",
    "primary_purpose": "introduce external sample/reagent into tube in a controlled manner (one-way intake)",
    "parameters_mm": "d=4/6; D>=6/8; H=40-60; A>=0.7; B=2; L=9.5",
    "parameters_material_process": "piston alignment with microchannels; air vent path for pressure balance",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 0,
    "interface_air_port_count": 1,
    "interface_notes": "one upstream inlet; includes air path/vent to prevent blockage and enable smooth intake",
    "external_actuation_required": "yes; slight press to align annular groove with inlet/transfer microchannel then lock",
    "external_environment_control_required": "no specific",
    "recommended_with_other_elements": "often paired with OUT or IN/OUT for transfer; pair with ON-OFF for routing; ensure air vent/compensation present",
    "operation_steps": "Step0: piston blocks paths; Step1: slight press aligns groove to open intake and air path for pressure balance; Step2: further press offsets alignment to seal/lock captured liquid",
    "notes": "air management is critical for repeatability"
}
```

------

#### P4 — IN–OUT（吸入+输出耦合转移单元）

- **用途**：同一单元完成“先吸入、再推送输出/转移到下游”，适合取样后再进入反应/纯化。
- **关键参数（mm）**：`d=4/6; D≥6/8; H=40–60; A≥0.7; B=2; C≥0.7; L=9.5`。
- **接口信息**：液体入口 `1`；液体输出 `1`；气口 `1`。
- **外部执行/环境需求**：需要外部按压分阶段执行（吸入→锁定→继续按压输出）；环境无特定要求。
- **推荐搭配**：是计量/合并/路由的核心积木，常上游接 `OUT`，下游接 `M4/M5` 或混匀模块。
- **操作步骤**：
  1. 第一阶段按 IN 逻辑吸入并锁定液柱；
  2. 继续按压推动液柱并带动底部结构联动；
  3. 触发释放/输出到下游。
- **注意事项**：困气与密封/摩擦会影响输出的瞬态与体积一致性。
- **JSON表示**：

```json
{
    "id": "P4",
    "category": "primitive",
    "name": "IN-OUT",
    "element_type": "1D foundational unit",
    "element_properties": "bidirectional transfer (intake then push-out) depending on actuation sequence; DIAC-like semantic",
    "primary_purpose": "aspirate liquid then later dispense/transfer it downstream within one unit",
    "parameters_mm": "d=4/6; D>=6/8; H=40-60; A>=0.7; B=2; C>=0.7; L=9.5",
    "parameters_material_process": "piston + passive plug coupling for push-out stage",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "one inlet + one outlet; includes air/pressure equalization path",
    "external_actuation_required": "yes; staged press for intake then continued press for output",
    "external_environment_control_required": "no specific; depends on downstream domain",
    "recommended_with_other_elements": "core building block for metering/aliquoting and merging; pair with OUT upstream; pair with mixing domain downstream",
    "operation_steps": "Stage1 (intake): press as IN to aspirate and lock; Stage2 (dispense): continue pressing to push liquid column and move passive plug; trigger OUT-like release to downstream",
    "notes": "entrapped air affects transient behavior and volumetric repeatability"
}
```

------

#### P5 — ON–OFF Valve（开关阀/数字门控单元）

- **用途**：提供明确的“开/关”门控，用于隔离、防回流、分支选择、多步流程门控，并可堆叠实现多次开关循环。
- **关键参数（mm）**：`d=4; D≥6; H=40–60; A=0.5; B≥0.7; C=2.6`。
- **接口信息**：液体入口 `1`；液体输出 `1`；气口 `0`。
- **外部执行/环境需求**：需要按压到特定位置实现 ON，再进一步按压实现 OFF；环境无特定要求。
- **推荐搭配**：与 `IN/OUT` 搭配实现复杂路由；与 `Sub-inlet/Sub-outlet` 构建分支；配合 `Air Vent` 改善瞬态。
- **操作步骤**：OFF（堵断）→ 按压对齐沟槽连通（ON）→ 继续按压沟槽越过通道再断开（OFF）→ 堆叠可重复循环。
- **注意事项**：对几何对齐和密封要求高，驱动力和漏液风险需折中。
- **JSON表示**：

```json
{
    "id": "P5",
    "category": "primitive",
    "name": "ON-OFF Valve",
    "element_type": "1D foundational unit",
    "element_properties": "digital gating; multiple cycles possible by stacked geometry",
    "primary_purpose": "selectively connect/isolate channels to route, isolate, prevent backflow, and enable multi-step sequencing",
    "parameters_mm": "d=4; D>=6; H=40-60; A=0.5; B>=0.7; C=2.6",
    "parameters_material_process": "piston groove alignment implements ON; offset implements OFF",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "two liquid ports with switchable connectivity",
    "external_actuation_required": "yes; press to first position for ON, further press to return OFF; can stack for repeated toggling",
    "external_environment_control_required": "no specific",
    "recommended_with_other_elements": "commonly paired with IN/OUT + OUT for metering and routing; supports multi-branch designs with sub-inlets/sub-outlets",
    "operation_steps": "OFF: piston blocks; ON: press to align groove with both channels; OFF again: further press moves groove past channels; optional stacked sections for multiple ON/OFF cycles",
    "notes": "gating reliability depends on sealing and alignment tolerances"
}
```

------

#### P6 — Micro-reagent Storage（单腔侧壁微试剂存储）

- **用途**：侧壁微腔预存微量试剂，通过活塞序列选择性释放到主流路，实现高价值试剂节省。
- **关键参数（mm）**：`d=4; D≥6; H=40–60; A=0.3; B=7; C=2.6; L=6; h=0.5`。
- **接口信息**：主流液体入口 `1`、出口 `1`；内部通过微端口与微腔耦合；气口在 JSON 中为 0（实际常需气体管理配合系统）。
- **外部执行/环境需求**：需要按压控制活塞位置；**微量存储对温度敏感**，长期储存建议低温（例如 4°C）。
- **推荐搭配**：常配合 `OUT（载液/冲洗）` 与 `IN/OUT` 做串行洗脱合并（对应 M5）；建议加 `Air Vent` 抑制气泡。
- **操作步骤**：微腔预装封存 → 活塞到位打开接口 → 载液流过洗脱微试剂并带入主流 → 活塞移位重新封闭。
- **注意事项**：微体积在常温/高湿条件下可能出现明显蒸发损失，需考虑冷链或短期使用。
- **JSON表示**：

```json
{
    "id": "P6",
    "category": "primitive_extension",
    "name": "Micro-reagent Storage (Single Chamber)",
    "element_type": "1D extension unit",
    "element_properties": "side-wall microchamber storage for micro-volume reagent; selectable release by piston positioning",
    "primary_purpose": "store and release micro-volume reagents into main flow with minimal consumption",
    "parameters_mm": "d=4; D>=6; H=40-60; A=0.3; B=7; C=2.6; L=6; h=0.5",
    "parameters_material_process": "multiple pistons segment main channel; microchamber has inlet/outlet ports; seal via film/geometry",
    "volume_range_uL": "micro-volume (example chamber volume scale: ~20 uL class discussed for evaporation behavior)",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "main-flow passes by microchamber; microchamber interfaces to main channel via dedicated microports",
    "external_actuation_required": "yes; piston sequence selects chamber access and releases stored reagent",
    "external_environment_control_required": "recommended for long storage: 4C for volatile/evaporation-sensitive micro-volumes",
    "recommended_with_other_elements": "typically used with OUT (carrier flow) and IN/OUT units for serial elution/merging; pair with air compensation to avoid bubbles",
    "operation_steps": "Step0: microchamber sealed and preloaded; Step1: position pistons to open microchamber interface; Step2: drive carrier flow to elute micro-reagent into main stream; Step3: re-seal by piston displacement",
    "notes": "micro-volume evaporation can be significant at 23C/65C; prefer cold-chain or short-term use"
}
```

------

#### P7 — Micro-reagent Storage（并联多腔侧壁微试剂存储）

- **用途**：并联多个微腔，支持从多个微量试剂中选择/组合释放，适合多试剂微量配方。
- **关键参数（mm）**：`d=4; D≥6; H=40–60; A=1; B=7; C=1.3; L=6; h=0.5`。
- **接口信息**：主流入口 `1`、出口 `1`；内部存在多个微腔接口；气口同上。
- **外部执行/环境需求**：需要活塞/门控策略选择微腔；建议低温储存以减少蒸发。
- **推荐搭配**：配合 `ON–OFF` 实现并联选择；与 `OUT/IN-OUT` 组成微量定量/合并链路。
- **操作步骤**：并联微腔预装封存 → 选择性打开某个/多个微腔 → 载液洗脱 → 关闭并继续下游。
- **注意事项**：并联结构更容易出现分支串扰与困气，需要良好气体补偿设计。
- **JSON表示**：

```json
{
    "id": "P7",
    "category": "primitive_extension",
    "name": "Micro-reagent Storage (Parallel Chambers)",
    "element_type": "1D extension unit",
    "element_properties": "multiple side-wall microchambers in parallel for selectable reagent set",
    "primary_purpose": "enable multi-reagent micro-volume storage with parallel selection/release patterns",
    "parameters_mm": "d=4; D>=6; H=40-60; A=1; B=7; C=1.3; L=6; h=0.5",
    "parameters_material_process": "segmented main channel + multiple microchambers; port sealing via film/geometry",
    "volume_range_uL": "micro-volume class",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "shared main inlet/outlet; multiple microchamber microports",
    "external_actuation_required": "yes; piston sequence selects which microchamber connects",
    "external_environment_control_required": "recommended 4C for long-term storage of micro-volumes",
    "recommended_with_other_elements": "use with ON-OFF valve for selecting parallel branches; use with OUT carrier and IN/OUT transfer units",
    "operation_steps": "Step0: chambers preloaded and sealed; Step1: actuate to open selected chamber(s); Step2: carrier flow elutes reagent(s) into main stream; Step3: close and proceed",
    "notes": "parallel selection increases routing complexity; ensure air management to prevent cross-talk"
}
```

------

#### P8 — Micro-reagent Storage（串联多腔侧壁微试剂存储）

- **用途**：微腔串联布置，载液沿路径逐个洗脱，实现多个微量试剂的累加合并，是 M5 的关键基础。
- **关键参数（mm）**：`d=4; D≥6; H=40–60; A=3.6; B=5; C=2.6; L=5; h=0.5`。
- **接口信息**：主流入口 `1`、出口 `1`；内部串行微腔接口；气口同上。
- **外部执行/环境需求**：需要活塞序列控制；建议温控/低温储存。
- **推荐搭配**：与 `OUT`（载液源）+ 下游混匀（M7）组合常见；强烈建议 `Air Vent`。
- **操作步骤**：预装封存 → 打开串联路径 → 载液依次洗脱各微腔 → 汇总从出口输出 → 重新封闭。
- **注意事项**：对气泡非常敏感，困气会放大瞬态并破坏合并一致性。
- **JSON表示**：

```json
{
    "id": "P8",
    "category": "primitive_extension",
    "name": "Micro-reagent Storage (Serial Chambers)",
    "element_type": "1D extension unit",
    "element_properties": "microchambers arranged in series; supports serial elution and cumulative merging",
    "primary_purpose": "enable sequential wash/elution through multiple microchambers for cumulative reagent merging",
    "parameters_mm": "d=4; D>=6; H=40-60; A=3.6; B=5; C=2.6; L=5; h=0.5",
    "parameters_material_process": "series microchambers along main path; piston gating per section",
    "volume_range_uL": "micro-volume class",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "main flow traverses serial microchamber interfaces",
    "external_actuation_required": "yes; piston sequencing controls serial access",
    "external_environment_control_required": "recommended 4C for long-term micro-volume stability",
    "recommended_with_other_elements": "directly enables few-to->10 uL merging macro module; pair with OUT carrier and mixing module downstream",
    "operation_steps": "Step0: chambers sealed and preloaded; Step1: open series path; Step2: carrier flow passes and sequentially elutes each chamber; Step3: collect merged stream at outlet; Step4: re-seal",
    "notes": "serial design is sensitive to trapped air; use air compensation/vent strategies"
}
```

------

### （二）宏模块（Macro Modules-M）

#### M1 — 高流量定量吸取/分装（0–500 µL）

- **用途**：在 0–500 µL 量程内做高精度计量与分配，适合较大体积加样。
- **关键指标**：量程 `0–500 µL`；整体误差上限（通用）可按 `≤1%` 计；文中对某些区间报告更高精度（例如 100–500 µL 更优）。
- **接口信息**：液体入口 `1`、出口 `1`、气口 `1`（计量稳定依赖气体管理）。
- **外部执行/环境需求**：需要按压驱动，通常需要稳定行程/止挡；无特定温控。
- **推荐搭配**：上游接 `OUT/Sequential OUT`，下游接 `M4（合并）` 或 `M6（搅拌）`；必要时加 `Air Vent`。
- **操作步骤**：设置限流/调节状态 → 通过 IN/OUT 完成吸入 → 推送分配到下游 → 锁定关闭。
- **注意事项**：困气会降低计量一致性。
- **JSON表示**：

```json
{
    "id": "M1",
    "category": "macro_module",
    "name": "Quantitative Aspiration/Aliquoting (High-flow Regulator)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "0-500 uL quantitative metering; uses flow resistance regulator concept",
    "primary_purpose": "meter and dispense larger volumes with high accuracy",
    "parameters_mm": null,
    "parameters_material_process": "includes adjustable flow resistance (rheostat-like elastomer element) + primitive combination",
    "volume_range_uL": "0-500",
    "accuracy_spec": "error <=1% (general); reported <0.5% in 100-500 uL range",
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "typically takes from OUT/IN and delivers to downstream; requires air management for stable metering",
    "external_actuation_required": "yes; press-driven piston strokes; may require calibrated stroke/stop",
    "external_environment_control_required": "no specific",
    "recommended_with_other_elements": "upstream OUT/Sequential OUT for reagent feed; downstream merging/mixing; add air compensation element when needed",
    "operation_steps": "Step1: set regulator state for target range; Step2: actuate intake/transfer via IN/OUT; Step3: dispense metered aliquot downstream; Step4: lock/close paths",
    "notes": "performance depends on minimizing trapped air and consistent actuation"
}
```

------

#### M2 — 中流量定量吸取/分装（0–50 µL）

- **用途**：0–50 µL 的中体积精确定量分配，适合常见反应配液。
- **关键指标**：量程 `0–50 µL`；误差一般可按 `≤5%`；特定区间可到约 `~1%（20–50 µL）`、`~3%（10 µL）`。
- **接口信息**：液体入口 `1`、出口 `1`、气口 `1`。
- **外部执行/环境需求**：需要多位置门控/转移的按压序列；温控不强制。
- **推荐搭配**：搭配 `ON–OFF` 做门控与路由；配合 `Air Vent` 降低瞬态。
- **操作步骤**：门控到位 → 受控吸入 → 推送分装 → 关闭隔离。
- **注意事项**：比高流量更敏感于漏液、气泡和摩擦差异。
- **JSON表示**：

```json
{
    "id": "M2",
    "category": "macro_module",
    "name": "Quantitative Aspiration/Aliquoting (Medium-flow Regulator)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "0-50 uL quantitative metering; tighter channel/rheostat control",
    "primary_purpose": "meter mid-range volumes for reactions requiring tens of microliters",
    "parameters_mm": null,
    "parameters_material_process": "primitive combination (OUT + IN/OUT + ON/OFF + IN/OUT) with flow regulation element",
    "volume_range_uL": "0-50",
    "accuracy_spec": "error <=5% (general); ~1% in 20-50 uL; ~3% at 10 uL",
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "requires stable air compensation and controlled actuation sequence",
    "external_actuation_required": "yes; multi-position actuation for gating and transfer",
    "external_environment_control_required": "no specific",
    "recommended_with_other_elements": "pair with ON-OFF for routing; downstream merging/mixing; use vent/air compensation to suppress transient spikes",
    "operation_steps": "Step1: configure/gate with ON-OFF; Step2: aspirate via IN/OUT under regulated flow; Step3: dispense metered volume; Step4: close to isolate",
    "notes": "sensitive to leakage and air bubbles compared with high-flow range"
}
```

------

#### M3 — 低流量/离散微腔定量分装（<10 µL）

- **用途**：实现 <10 µL 的微量定量，适合高价值试剂与微量反应。
- **关键指标**：离散剂量（如 2/4/6/8/10 µL）；一般误差上限 `≤10%`；≥6 µL 可达到 `≤3%` 的更高精度。
- **接口信息**：液体入口 `1`、出口 `1`、气口 `1`。
- **外部执行/环境需求**：需要高精度门控/位置控制；微体积对蒸发敏感，建议温控/缩短暴露时间。
- **推荐搭配**：与 `E* 微腔存储`、`M5 微量合并`、`M7 气泡混匀`组合常见；建议强制配 `Air Vent`。
- **操作步骤**：选择离散微腔 → 填充/定量 → 输出到下游 → 复位封闭。
- **注意事项**：蒸发、困气和残留液对误差贡献最大。
- **JSON表示**：

```json
{
    "id": "M3",
    "category": "macro_module",
    "name": "Quantitative Aspiration/Aliquoting (Low-flow Regulator / Discrete Microchambers)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "<10 uL metering using discrete microchambers and gating",
    "primary_purpose": "meter very small volumes for high-value reagents",
    "parameters_mm": null,
    "parameters_material_process": "uses ON-OFF gating + IN + IN/OUT + OUT; discrete microchambers (e.g., 2/4/6/8/10 uL)",
    "volume_range_uL": "<10 (discrete 2/4/6/8/10)",
    "accuracy_spec": "error <=10% (general); <=3% for >=6 uL discrete doses",
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "micro-volume dosing requires strict air control and sealing integrity",
    "external_actuation_required": "yes; precise gating position control",
    "external_environment_control_required": "recommended temperature control for evaporation-sensitive micro-volumes",
    "recommended_with_other_elements": "often combined with micro-reagent storage elements and downstream mixing; avoid long ambient storage without control",
    "operation_steps": "Step1: select discrete chamber via ON-OFF gating; Step2: fill/aspirate micro-volume; Step3: dispense to downstream; Step4: reseal/lock",
    "notes": "evaporation and trapped air dominate error budget at this scale"
}
```

------

#### M4 — 大体积合并（tens µL 到 mL）

- **用途**：将多路试剂（多个 OUT）按顺序注入到同一合并腔，实现从几十微升到毫升级的合并。
- **关键参数（mm）**：`L=18; H=40–60; d=4; A=0.5; B=0.5; C=5.2; E=2.0; F=2.6`。
- **接口信息**：液体入口 `≥2`（多路输入），液体出口 `1`，气口 `1`（推荐）。
- **外部执行/环境需求**：需要对多个 OUT 进行顺序触发；无特定温控。
- **推荐搭配**：下游强烈推荐接 `M6/M7` 混匀；上游可用 `Sequential OUT` 编码加样顺序；必要时加 `Air Vent`。
- **操作步骤**：按顺序触发 OUT#1、OUT#2…进入合并腔 → 合并完成后转移到下游。
- **注意事项**：困气会导致飞溅/流量尖峰，影响合并一致性。
- **JSON表示**：

```json
{
    "id": "M4",
    "category": "macro_module",
    "name": "Reagent Merging (Tens-to-mL Scale)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "sequential addition of multiple OUT streams into a merging chamber",
    "primary_purpose": "combine multiple reagents from tens of uL up to mL into one mixture",
    "parameters_mm": "L=18; H=40-60; d=4; A=0.5; B=0.5; C=5.2; E=2.0; F=2.6",
    "parameters_material_process": "multiple OUT feeding into single IN/OUT chamber",
    "volume_range_uL": "tens uL to mL",
    "accuracy_spec": null,
    "interface_liquid_in_count": 2,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "multiple incoming reagent feeds; one merged outlet; air handling recommended to prevent spikes/splash",
    "external_actuation_required": "yes; sequential actuation of OUT stages",
    "external_environment_control_required": "no specific",
    "recommended_with_other_elements": "pair with mixing module (magnetic or bubble) after merging; upstream Sequential OUT useful for ordered addition",
    "operation_steps": "Step1: trigger OUT#1 to inject into merge chamber; Step2: trigger OUT#2... in sequence; Step3: once merged, transfer via IN/OUT to next module",
    "notes": "order and timing encode protocol; air compensation improves stability"
}
```

------

#### M5 — 微量合并（few µL 到 >10 µL，串行洗脱）

- **用途**：由 OUT 产生载液主流，依次穿过串联侧壁微腔，把多个微量试剂洗脱带出并累计合并。
- **关键参数（mm）**：`L=18; H=40–60; d=4; A=0.5; B=7; C=2; E=2.6`。
- **接口信息**：主流液体入口 `1`、出口 `1`、气口 `1`（强烈建议）。
- **外部执行/环境需求**：需要活塞序列与载液流控制；建议温控以降低蒸发。
- **推荐搭配**：下游接 `M7 气泡混匀` 更适合小体积；上游搭配 `E3 串联微腔存储`；强烈建议 `Air Vent`。
- **操作步骤**：启动载液 → 依次洗脱微腔 → 在末端收集合并液 → 进入混匀或反应域。
- **注意事项**：气泡是最主要风险源，必须设计/插入空气补偿。
- **JSON表示**：

```json
{
    "id": "M5",
    "category": "macro_module",
    "name": "Reagent Merging (Few-to->10 uL Scale via Serial Microchambers)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "carrier flow elutes micro-reagents from serial side-wall storages",
    "primary_purpose": "merge multiple micro-volume reagents into one stream with minimal waste",
    "parameters_mm": "L=18; H=40-60; d=4; A=0.5; B=7; C=2; E=2.6",
    "parameters_material_process": "OUT provides carrier flow; serial micro-reagent storage + IN/OUT interfaces",
    "volume_range_uL": "few uL to >10 uL (cumulative)",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "single in/out main stream; internal serial microports",
    "external_actuation_required": "yes; control of piston sequence and carrier flow",
    "external_environment_control_required": "recommended temperature control for micro-volume stability",
    "recommended_with_other_elements": "pair with bubble agitation mixing for small volumes; downstream reaction domains",
    "operation_steps": "Step1: initiate carrier stream from OUT; Step2: pass through serial microchambers to elute each stored reagent; Step3: collect merged stream at outlet",
    "notes": "high sensitivity to bubbles; air compensation strongly recommended"
}
```

------

#### M6 — 磁力搅拌混匀（适合较大体积）

- **用途**：在混匀腔内放置搅拌子，通过外部旋转磁场主动搅拌，实现强混匀，适合 tens µL 到 mL。
- **关键参数（mm）**：`L=18; H=40–60; d=4; D=8; A=5.2; B=5.2; C=2.0; E=2.6`。
- **接口信息**：液体入口 `1`、出口 `1`；气口 `0`。
- **外部执行/环境需求**：需要外部磁驱动（旋转磁场）；温控可选。
- **推荐搭配**：常紧接 `M4`；上游由 `IN/OUT` 转移进入，混匀后再转移到反应域。
- **操作步骤**：合并液进入 → 外磁场驱动搅拌子旋转 → 混匀完成后转出。
- **注意事项**：需要额外硬件（磁驱平台），但对大体积更稳健。
- **JSON表示**：

```json
{
    "id": "M6",
    "category": "macro_module",
    "name": "Homogenization (Magnetic Stirring)",
    "element_type": "composed module (special-case combination of primitives + external field)",
    "element_properties": "active stirring with internal stir bar; suited for larger volumes",
    "primary_purpose": "rapidly homogenize merged reagents at tens uL to mL scale",
    "parameters_mm": "L=18; H=40-60; d=4; D=8; A=5.2; B=5.2; C=2.0; E=2.6",
    "parameters_material_process": "requires insertion of magnetic stir bar; chamber geometry supports rotation",
    "volume_range_uL": "tens uL to mL",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "one inlet and one outlet; mixing happens in-chamber",
    "external_actuation_required": "no additional press beyond fluid transfer; but requires external magnetic drive",
    "external_environment_control_required": "optional heating/cooling depending on assay; external magnet alignment",
    "recommended_with_other_elements": "use immediately after merging (M4); upstream OUT/IN-OUT for delivery; downstream reaction domains",
    "operation_steps": "Step1: deliver merged liquid into chamber; Step2: apply external rotating magnetic field to spin stir bar; Step3: after mixing, transfer out to next step",
    "notes": "requires external magnet hardware; robust for larger volumes"
}
```

------

#### M7 — 气泡扰动混匀（适合小体积）

- **用途**：通过“空气 OUT”向液体中注入气泡形成扰动，实现快速混匀，适合微量到几十微升。
- **关键参数（mm）**：`L=18; H=40–60; d=4; A=2.6; B=3; C=2.6; E=0.5`。
- **接口信息**：液体入口 `1`、出口 `1`、气口 `1`。
- **外部执行/环境需求**：需要触发空气注入（按压或气源控制）；温控可选。
- **推荐搭配**：适合接在 `M5` 后；若下游还有高精度计量，建议混匀后增加消泡/排气步骤或 vent。
- **操作步骤**：装载混合液 → 注入气泡搅动 → 停止供气并转出。
- **注意事项**：残留气泡可能干扰后续计量/阀门动作，需要空气管理或等待消泡。
- **JSON表示**：

```json
 {
    "id": "M7",
    "category": "macro_module",
    "name": "Homogenization (Bubble Agitation)",
    "element_type": "composed module (special-case combination of primitives)",
    "element_properties": "mixing by controlled air bubble injection; suited for small volumes",
    "primary_purpose": "quickly homogenize micro-volume mixtures without stir bar",
    "parameters_mm": "L=18; H=40-60; d=4; A=2.6; B=3; C=2.6; E=0.5",
    "parameters_material_process": "uses an air-OUT behavior to inject bubbles through liquid",
    "volume_range_uL": "micro to tens uL",
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 1,
    "interface_notes": "needs an air source path/vent control; bubble path intersects liquid",
    "external_actuation_required": "yes; trigger air delivery via press-actuated element",
    "external_environment_control_required": "optional temperature control depending on assay",
    "recommended_with_other_elements": "use after micro-volume merging (M5) or low-flow metering (M3); pair with air management elements",
    "operation_steps": "Step1: load mixture into chamber; Step2: actuate air-OUT to inject bubbles and agitate; Step3: stop air and transfer mixed solution out",
    "notes": "air bubbles can interfere with downstream metering if not re-settled/vented"
}
```

------

### （三）中间元件 / 额外器件元素（Additional Elements-I）

#### I1 — Inlet（主入口）

- **用途**：系统级外部液体输入端口，用于连接外部样本/试剂源。
- **接口信息**：液体入口 `1`，无输出。
- **外部执行/环境需求**：无；实际吸入由下游 IN/IN-OUT 执行。
- **推荐搭配**：与 `IN` 组合形成受控吸入；与 `ON–OFF` 组合进行分支分配。
- **操作步骤**：连接外部源 → 由下游单元触发吸入/转移。
- **注意事项**：端口密封与死体积会影响计量。
- **JSON表示**：

```json
{
    "id": "I1",
    "category": "intermediate_element",
    "name": "Inlet",
    "element_type": "system interface element",
    "element_properties": "primary external fluid entry port",
    "primary_purpose": "connect external sample/reagent source to device",
    "parameters_mm": null,
    "parameters_material_process": "standard port geometry compatible with tubing/needle (implementation-specific)",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 0,
    "interface_air_port_count": 0,
    "interface_notes": "system-level entry; often precedes IN or IN/OUT units",
    "external_actuation_required": "no",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "pair with IN for controlled intake; use with ON-OFF for routing to branches",
    "operation_steps": "Step1: connect source; Step2: initiate intake using downstream IN/IN-OUT actuation",
    "notes": "port sealing and dead volume affect accuracy"
}
```

------

#### I2 — Outlet（主出口）

- **用途**：系统级外部液体输出端口，用于产物收集或废液排放。
- **接口信息**：液体输出 `1`，无输入。
- **外部执行/环境需求**：无。
- **推荐搭配**：与路由阀/废液域搭配；用于最终产物/废液收集。
- **操作步骤**：把流程末端流体路由到出口并收集。
- **注意事项**：出口背压可能影响上游计量稳定性。
- **JSON表示**：

```json
{
    "id": "I2",
    "category": "intermediate_element",
    "name": "Outlet",
    "element_type": "system interface element",
    "element_properties": "primary external fluid exit port",
    "primary_purpose": "collect final product or route waste out of device",
    "parameters_mm": null,
    "parameters_material_process": "standard port geometry compatible with tubing/collection (implementation-specific)",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "system-level exit; often follows OUT/IN-OUT transfer",
    "external_actuation_required": "no",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "pair with waste handling domain or product collection; often downstream of ON-OFF routing",
    "operation_steps": "Step1: route final stream to outlet; Step2: collect/vent as required",
    "notes": "backpressure at outlet can disturb upstream metering"
}
```

------

#### I3 — Sub-inlet（子入口）

- **用途**：为某个子流程/分支域提供补液/加样入口。
- **接口信息**：液体入口 `1`。
- **外部执行/环境需求**：无。
- **推荐搭配**：与 `ON–OFF` 实现分支选择；与 `IN/OUT` 做分支定量。
- **操作步骤**：连接试剂 → 打开对应路由 → 注入子域。
- **注意事项**：支持模块化扩展，避免重构主入口。
- **JSON表示**：

```json
{
    "id": "I3",
    "category": "intermediate_element",
    "name": "Sub-inlet",
    "element_type": "system interface element",
    "element_properties": "secondary fluid entry port for branch or local domain",
    "primary_purpose": "inject supplementary reagent into a sub-process/domain",
    "parameters_mm": null,
    "parameters_material_process": "port geometry implementation-specific",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 0,
    "interface_air_port_count": 0,
    "interface_notes": "used with ON-OFF to select branch injection",
    "external_actuation_required": "no",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "pair with ON-OFF valve and IN/OUT to control branch dosing and routing",
    "operation_steps": "Step1: connect reagent to sub-inlet; Step2: open route via gating; Step3: deliver to target domain",
    "notes": "supports modular expansion without redesigning main inlet"
}
```

------

#### I4 — Sub-outlet（子出口）

- **用途**：子流程/分支的排液或中间产物输出。
- **接口信息**：液体输出 `1`。
- **外部执行/环境需求**：无。
- **推荐搭配**：与 `ON–OFF` 路由和废液管理组合；必要时加 vent/补偿。
- **操作步骤**：路由到子出口并排出/收集。
- **注意事项**：用于域隔离、减少交叉污染风险。
- **JSON表示**：

```json
{
    "id": "I4",
    "category": "intermediate_element",
    "name": "Sub-outlet",
    "element_type": "system interface element",
    "element_properties": "secondary fluid exit port for branch discharge",
    "primary_purpose": "remove waste or intermediate product from a sub-process/domain",
    "parameters_mm": null,
    "parameters_material_process": "port geometry implementation-specific",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "used for branch waste management and domain partitioning",
    "external_actuation_required": "no",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "pair with ON-OFF routing and waste domain; use with air compensation if needed",
    "operation_steps": "Step1: route branch flow; Step2: discharge to sub-outlet",
    "notes": "helps isolate domains and reduce cross-contamination"
}
```

------

#### I5 — Air Vent（排气/空气补偿口）

- **用途**：释放困气、均压、抑制瞬态流量尖峰，提高计量与合并稳定性。
- **接口信息**：气口 `1`（通常连到大气或受控气腔）。
- **外部执行/环境需求**：无，部分流程中可能需要在反应阶段“封闭”。
- **推荐搭配**：与 `OUT/Sequential OUT`、`M2/M3/M5/M7` 等对气泡敏感模块强烈推荐。
- **操作步骤**：在灌注/驱动时提供排气通路 → 需要密封反应时关闭或隔离。
- **注意事项**：是抑制困气尖峰的关键系统元件。
- **JSON表示**：

```json
{
    "id": "I5",
    "category": "intermediate_element",
    "name": "Air Vent",
    "element_type": "system compensation element",
    "element_properties": "air release/pressure equalization port",
    "primary_purpose": "prevent air entrapment, stabilize pressure and flow, reduce transient spikes",
    "parameters_mm": null,
    "parameters_material_process": "vent channel/port; may be membrane-filtered in implementations",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 0,
    "interface_air_port_count": 1,
    "interface_notes": "connects trapped air pocket to atmosphere or controlled air volume",
    "external_actuation_required": "no",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "recommended with OUT/Sequential OUT, metering regulators, and micro-volume modules to suppress flow spikes",
    "operation_steps": "Step1: provide vent path during filling/actuation; Step2: close or isolate if protocol requires sealed reaction",
    "notes": "critical for preventing high peak flow rates caused by entrapped air"
}
```

------

#### I6 — Push Rod（推杆/执行耦合件）

- **用途**：把外部执行器的位移/力可靠传递到活塞/阀，实现可控按压驱动。
- **接口信息**：无流体端口（机械接口）。
- **外部执行/环境需求**：需要外部仪器/执行器；对对准和行程一致性要求高。
- **推荐搭配**：几乎所有按压驱动单元都需要。
- **操作步骤**：对准活塞头部 → 施加受控行程/力 → 回程复位。
- **注意事项**：行程重复性直接影响计量精度。
- **JSON表示**：

```json
{
    "id": "I6",
    "category": "intermediate_element",
    "name": "Push Rod",
    "element_type": "external actuation coupling element",
    "element_properties": "mechanical force/position transmission part",
    "primary_purpose": "transfer external actuator displacement to pistons/valves reliably",
    "parameters_mm": null,
    "parameters_material_process": "rigid linkage; alignment tolerance critical",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 0,
    "interface_liquid_out_count": 0,
    "interface_air_port_count": 0,
    "interface_notes": "not a fluid port; mechanical interface only",
    "external_actuation_required": "yes; requires external instrument/actuator",
    "external_environment_control_required": "no",
    "recommended_with_other_elements": "used with all press-actuated primitives and macro modules",
    "operation_steps": "Step1: align with piston head; Step2: apply controlled stroke/force profile; Step3: retract/reset as needed",
    "notes": "stroke repeatability influences metering accuracy"
}
```

------

#### I7 — Magnetic Beads Chamber（磁珠腔）

- **用途**：磁珠捕获/洗涤/洗脱/纯化的功能域，支持复杂核酸/蛋白工作流。
- **接口信息**：液体入口 `1`、出口 `1`。
- **外部执行/环境需求**：需要外部磁场（磁铁定位/开关）；温控可选。
- **推荐搭配**：与 `M1/M2/M4` 做上游计量与合并；与 `ON–OFF` 实现洗涤循环路由。
- **操作步骤**：送入磁珠悬液 → 开磁固定 → 引入洗涤缓冲并排出 → 洗脱并转移输出。
- **注意事项**：死体积与流速会影响磁珠损失与回收率。
- **JSON表示**：

```json
{
    "id": "I7",
    "category": "intermediate_element",
    "name": "Magnetic Beads Chamber",
    "element_type": "functional domain element",
    "element_properties": "reaction/handling zone for magnetic beads capture/wash/elution",
    "primary_purpose": "support bead-based capture/purification steps within workflow domains",
    "parameters_mm": null,
    "parameters_material_process": "chamber geometry supports bead retention; typically used with external magnet positioning",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "inlet/outlet for wash and elution streams",
    "external_actuation_required": "no additional beyond fluid routing; requires external magnet for bead immobilization",
    "external_environment_control_required": "optional temperature control depending on chemistry",
    "recommended_with_other_elements": "pair with metering/merging upstream; pair with ON-OFF routing for wash cycles; often followed by mixing or reaction domains",
    "operation_steps": "Step1: deliver bead suspension; Step2: apply external magnet to immobilize beads; Step3: route wash buffers; Step4: elute and transfer out",
    "notes": "dead volume and bead loss depend on chamber geometry and flow profiles"
}
```

------

#### I8 — Membrane Chamber（膜腔）

- **用途**：膜分离/过滤/纯化域，用于过滤或选择性透过。
- **接口信息**：液体入口 `1`、出口 `1`。
- **外部执行/环境需求**：通常仅需流体驱动，但可能需要可控压力曲线；温控可选。
- **推荐搭配**：上游计量/合并（M1/M2/M4），并建议配合 `Air Vent` 以避免困气导致膜润湿失败。
- **操作步骤**：润湿/预充 → 驱动溶液过膜 → 收集透过/截留端 → 进入下游步骤。
- **注意事项**：困气会阻碍膜润湿，密封不良会造成旁路漏过。
- **JSON表示**：

```json
{
    "id": "I8",
    "category": "intermediate_element",
    "name": "Membrane Chamber",
    "element_type": "functional domain element",
    "element_properties": "membrane-based separation/filtration zone",
    "primary_purpose": "enable membrane purification/separation steps within workflow domains",
    "parameters_mm": null,
    "parameters_material_process": "membrane integration; sealing critical to prevent bypass leakage",
    "volume_range_uL": null,
    "accuracy_spec": null,
    "interface_liquid_in_count": 1,
    "interface_liquid_out_count": 1,
    "interface_air_port_count": 0,
    "interface_notes": "inlet/outlet across membrane; may require vent depending on wetting",
    "external_actuation_required": "no additional beyond fluid routing; may require controlled pressure profile",
    "external_environment_control_required": "optional temperature control depending on process",
    "recommended_with_other_elements": "pair with metering/merging upstream; pair with air compensation to avoid trapped air preventing wetting; downstream reaction domain",
    "operation_steps": "Step1: wet/prime membrane; Step2: drive solution through membrane; Step3: collect permeate/retentate as designed; Step4: proceed to next domain",
    "notes": "air entrapment can block membrane wetting; venting strategies recommended"
}
```

## 元件实例表示

### 3.1 字段与取值规范

- `inst_id`
  - **类型**：string
  - **格式**：`U` + 3~6 位数字（例：`U001`, `U0123`）
  - **约束**：全局唯一；被 netlist/plan 引用
- `lib_id`
  - **类型**：string
  - **取值**：必须来自元件库的 `id`（例：`P1`, `M4`, `I5`, `E2`）
  - **约束**：不得虚构
- `role`
  - **类型**：string
  - **取值**：自由文本但建议使用统一命名（便于检索/规则）
  - **推荐模式**（任选其一或组合）：
    - 源：`source_<reagent>`（例：`source_LysisBuffer`）
    - 处理：`metering`, `merge`, `mix`, `route`, `capture`, `filter`, `reaction`
    - 端口：`inlet_main`, `outlet_product`, `outlet_waste`, `sub_inlet_*`, `sub_outlet_*`
    - 执行/补偿：`air_vent`, `pushrod`, `heater`, `magnet_interface`
- `domain`
  - **类型**：string
  - **允许取值（推荐枚举）**：
    - `prep`, `meter`, `merge`, `mix`, `capture`, `wash`, `filter`, `reaction`, `output`, `waste`, `utility`
  - **也允许**：自定义域名（如 `domain_1`），但建议保持上述集合以利规则检查
- `phase`
  - **类型**：string
  - **取值（推荐枚举）**：
    `sample_prep, lysis, bind_capture, wash, elute, amplify, detect, output, waste, utility`
    （允许自定义但建议优先用枚举）
  - **一致性约束**：
    `phase` 表示 **protocol 大过程阶段**；`domain` 表示 **阶段内功能域**（meter/merge/mix/capture/filter/reaction…）。
- `ports_liquid`
  - **类型**：string
  - **格式**：逗号分隔的端口名列表；无则空串 `""`
  - **端口名允许形式**：
    - `liq_in_1`, `liq_in_2`, …
    - `liq_out_1`, `liq_out_2`, …
  - **示例**：`"liq_in_1,liq_out_1"` 或 `""`
- `ports_air`
  - **类型**：string
  - **格式**：逗号分隔；无则空串
  - **端口名允许形式**：`air_1`, `air_2`, …
- `ports_act`
  - **类型**：string
  - **格式**：逗号分隔；无则空串
  - **端口名允许形式**：`act_1`, `act_2`, …
  - **说明**：用于 press/toggle/set_position 等动作目标
- `ports_thermal`
  - **类型**：string
  - **格式**：逗号分隔；无则空串
  - **端口名允许形式**：`therm_1`, `therm_2`, …
- `ports_magnetic`
  - **类型**：string
  - **格式**：逗号分隔；无则空串
  - **端口名允许形式**：`mag_1`, `mag_2`, …
- `reagent_name`
  - **类型**：string
  - **取值**：
    - 单试剂：任意字符串（例：`"LysisBuffer"`）
    - 多试剂：用 `|` 分隔（例：`"Wash1|Wash2|Elution"`）
    - 无预装试剂：空串 `""`
- `reagent_volume_uL`
  - **类型**：number 或 string（二选一；建议统一用 string 以兼容多值）
  - **取值**：
    - 单体积：数字（例：`200`）或字符串（`"200"`）
    - 多体积：用 `|` 分隔（例：`"200|200|50"`），必须与 `reagent_name` 一一对应
    - 无预装试剂：`0` 或 `""`（建议用 `0`，更利于数值处理）
- `reagent_state`
  - **类型**：string
  - **允许取值（推荐枚举）**：`liquid`, `dry`, `beads`, `air`, `empty`
  - **说明**：
    - OUT/IN 等装液一般为 `liquid`
    - 冻干试剂可用 `dry`
    - 磁珠域可用 `beads`
    - vent 可用 `air`
    - 默认 `empty`
- `param_override`
  - **类型**：string
  - **取值**：空串 `""` 或半结构字符串（推荐 `key=value;key=value`）
  - **示例**：`"H=55;plug_hardness=45ShoreA;interference=0.4"`
  - **说明**：仅在实例参数不同于库默认时填写

------

### 3.2 Instance JSON 模板（数组模板）

```json
[
  {
    "inst_id": "U001",
    "lib_id": "P1",
    "role": "source_ReagentA",
    "domain": "prep",
    "phase": "sample_prep",
    "ports_liquid": "liq_out_1",
    "ports_air": "",
    "ports_act": "act_1",
    "ports_thermal": "",
    "ports_magnetic": "",
    "reagent_name": "ReagentA",
    "reagent_volume_uL": "200",
    "reagent_state": "liquid",
    "param_override": ""
  }
]
```

## 连接表示

### 4.1 字段与取值规范

- `edge_id`
  - **类型**：string
  - **格式**：`E` + 3~6 位数字（例：`E001`）
  - **约束**：全局唯一
- `from_inst`
  - **类型**：string
  - **取值**：必须是 instance 表中的某个 `inst_id`
- `from_port`
  - **类型**：string
  - **取值**：必须在 `from_inst` 对应 instance 的某个 `ports_*` 列表中出现
  - **典型形式**：`liq_out_#`, `air_#`, `act_#`, `therm_#`, `mag_#`
- `to_inst`
  - **类型**：string
  - **取值**：必须是 instance 表中的某个 `inst_id`
- `to_port`
  - **类型**：string
  - **取值**：必须在 `to_inst` 对应 instance 的某个 `ports_*` 列表中出现
- `channel`
  - **类型**：string
  - **允许取值（枚举）**：`liquid`, `air`, `mechanical`, `thermal`, `magnetic`
- `domain`
  - **类型**：string
  - **允许取值**：与 instance 的 `domain` 同一集合（推荐：`prep|meter|merge|mix|capture|wash|filter|reaction|output|waste|utility`）
  - **约束（建议）**：一条边的 domain 应与两端实例的 domain 相同或兼容（由 verifier 定义）
- `phase`
  - **取值规则**：
    - 通常等于两端 instance 的 `phase`
    - 跨阶段连接允许，但必须显式标注：`phase="cross_phase"`（或用真实 phase 名 + 在 notes/constraint 说明跨越）
  - **最小实现**：先只允许同 phase，后续再扩展跨 phase。

------

### 4.2 Netlist JSON 模板（数组模板）

```json
[
  {
    "edge_id": "E001",
    "from_inst": "U001",
    "from_port": "liq_out_1",
    "to_inst": "U010",
    "to_port": "liq_in_1",
    "channel": "liquid",
    "domain": "merge",
    "phase": "sample_prep"
  }
]
```

## 操作表示

### 5.1 字段与取值规范

- `step_id`
  - **类型**：integer
  - **取值**：正整数；建议从 1 递增（但最小要求是唯一）
- `action`
  - **类型**：string
  - **允许取值（推荐枚举）**：
    - 机械：`press`, `release`, `toggle_open`, `toggle_close`, `set_position`
    - 混匀：`mix_stir`, `mix_bubble`
    - 磁控：`magnet_on`, `magnet_off`
    - 热控：`set_temp`, `heat_on`, `heat_off`
    - 时间：`wait`
  - **说明**：建议只用这些词，避免 LLM 发散
- `target_inst`
  - **类型**：string
  - **取值**：
    - 对具体动作：必须是某个 instance 的 `inst_id`
    - 对 `wait`：允许空串 `""`
- `target_port`
  - **类型**：string
  - **取值**：
    - `press/toggle/set_position` 通常是 `act_*`
    - `mix_stir` 可用 `mag_*` 或空串（看你是否把搅拌外设抽象成端口）
    - `set_temp/heat_on/off` 通常是 `therm_*`
    - `magnet_on/off` 通常是 `mag_*`（或空串，若磁控不按端口建模）
    - 对 `wait`：允许空串 `""`
  - **约束**：若非空，必须出现在 target_inst 的对应 `ports_*` 中
- `value`
  - **类型**：string
  - **取值**：空串 `""` 或参数串（推荐 `key=value;key=value`）
  - **常见键（建议集合）**：
    - 机械：`stroke=...`, `pos=...`, `force_N=...`, `cycle=...`
    - 热控：`temp_C=...`, `ramp_C_per_s=...`
    - 搅拌：`rpm=...`
    - 气泡：`pulse=...`, `air_volume_uL=...`
  - **示例**：`"stroke=stage1"`、`"temp_C=65"`、`"rpm=800"`
- `duration_s`
  - **类型**：integer
  - **取值**：`>=0`；瞬时动作可填 0 或 1；混匀/加热通常 >0
- `depends_on`
  - **类型**：string
  - **取值**：空串 `""` 或逗号分隔 step_id（例：`"1,2,3"`）
  - **说明**：用于表达 DAG 依赖；不想用就都填空串
- `domain`
  - **类型**：string
  - **允许取值**：同 instance domain 枚举
  - **约束（建议）**：动作 domain 与 target_inst.domain 一致（wait 可用任意域或 `utility`）
- `phase`
  - **类型**：string
  - **取值规则**：
    - 非 `wait`：必须等于 `target_inst.phase`
    - `wait`：可填 `utility` 或继承最近一步的 phase（建议填 `utility` 以简化）

------

### 5.2 Plan JSON 模板（数组模板）

```json
[
  {
    "step_id": 1,
    "action": "press",
    "target_inst": "U001",
    "target_port": "act_1",
    "value": "stroke=release",
    "duration_s": 2,
    "depends_on": "",
    "domain": "prep",
    "phase": "sample_prep"
  }
]
```

## Verifier 规则清单

### 7.1 ID 与引用一致性

- [R001] `inst_id` 全唯一
- [R002] `lib_id` 必须存在于元件库
- [R003] `edge_id` 全唯一
- [R004] `step_id` 从 1 递增或至少唯一
- [R005] instance / netlist / plan 中凡出现 `phase` 字段：必须非空字符串（wait 也必须有 phase，推荐填 `utility`）

### 7.2 端口声明一致性

- [R101] 对每个 instance：
  - `ports_liquid / ports_air / ports_act / ports_thermal / ports_magnetic` 必须是字符串；允许空串 `""`
  - 每个字段内部端口名按逗号分割后 **不得重复**（去空格后比较）
- [R102] 端口命名必须与类型一致：
  - `ports_liquid` 内只能出现 `liq_in_*` 或 `liq_out_*`
  - `ports_air` 内只能出现 `air_*`
  - `ports_act` 内只能出现 `act_*`
  - `ports_thermal` 内只能出现 `therm_*`
  - `ports_magnetic` 内只能出现 `mag_*`
- [R103] 同理检查 `air/act/thermal/magnetic`
- [R104] netlist 的 `from_port/to_port` 必须在对应 instance 的端口名列表中（对应的 `ports_*` 字段）
- [R105] plan 的 `target_port` 必须在对应 instance 的端口名列表中（对应的 `ports_*` 字段）
- ******[R106]** plan 中非 `wait` 步骤：`target_inst` 必须存在且非空；`wait` 允许 `target_inst=""` 且 `target_port=""`

### 7.3 连接类型合法性

- [R201] `channel=liquid` 时：`from_port` 必须是 `liq_out_*`，`to_port` 必须是 `liq_in_*`
- [R202] `channel=air` 时：两端必须是 `air_*`
- [R203] `channel=mechanical` 时：to_port 必须是 `act_*`
- [R204] `channel=thermal` 时：to_port 必须是 `therm_*`
- [R205] `channel=magnetic` 时：to_port 必须是 `mag_*`
- [R206] netlist 的 `phase` 一致性：
  - 若 `from_inst.phase == to_inst.phase`，则 `edge.phase` 必须等于该 phase
  - 若不同，则 `edge.phase` 必须为 `"cross_phase"`（或你定义的跨阶段标记）

### 7.4 结构连通性

- [R301] 除了纯接口件（inlet/outlet/sub-ports/push-rod），每个实例至少有 1 条入边或出边
- [R302] 每个“源”（role 含 source / OUT / Sequential OUT）应能通过 liquid edges 到达某个 sink（reaction/output/waste）
- [R303] phase 内连通性：对每个 phase（除 `utility`）：
  - 至少存在一条液体路径把该 phase 的源（source/OUT/Sequential OUT）连接到同 phase 的处理/汇（merge/mix/reaction/output/waste）
  - 若出现 `edge.phase="cross_phase"`，则必须确保跨 phase 的两侧各自仍满足本 phase 的最小连通（避免跨阶段跳线导致阶段内部断裂）

### 7.5 执行计划覆盖

- [R401] 如果存在 `requires_external_magnet=yes` → plan 必须包含 `magnet_on` 与 `magnet_off`
- [R402] 如果存在 `requires_external_heating=yes` → plan 必须包含 `set_temp` 或 `heat_on`，以及 `heat_off`
- [R403] 对所有 `requires_external_actuator=yes` 且 ports_act>0 的实例，plan 至少出现一次 `press/toggle/set_position` 指向它
- [R404] 若出现 mixing 模块：`mix_stir` 或 `mix_bubble` 必须出现一次
- [R405] plan 的 `phase` 对齐：
  - 非 `wait`：`step.phase == target_inst.phase`
  - `wait`：`step.phase` 必须存在，推荐 `"utility"`（或等于上一步 phase，但要一致化）
- [R406] 若某 phase 中存在需要外设的实例（magnet/heating/actuation），则该 phase 内应出现对应动作步骤（避免把所有 magnet_on 放到别的 phase）

### 7.6 气体管理/瞬态风险

- [R501] ：上述“同域或上游”应限定为：
  - **同 phase** 的 `domain` 内，或
  - 同 phase 的上游路径（沿 liquid edges 追溯到最近 OUT/Sequential OUT）所覆盖的节点集合中
    （避免把 vent 放到别的 phase 但实际无助于该阶段的困气）
- [R502] 若 plan 中有 bubble mixing（M7），则后续若接 metering（M2/M3）建议插入 `wait` 或 `vent` 步骤以消泡（可作为软规则）
- [R503] 若 `edge.phase="cross_phase"` 且跨越到更精密计量阶段（含 M2/M3），建议在跨 phase 连接之后插入 `wait` 或 `air_vent` 相关动作/停留，以降低气泡携带风险