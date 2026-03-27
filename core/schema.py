
## 1. core/schema.py

"""
Data structure definition module.
Defines all data models for biochip design.
"""
from pydantic import BaseModel, Field


class ComponentInstance(BaseModel):
    """Component instance."""
    inst_id: str = Field(description="Format: U + 3~6 digits")
    lib_id: str = Field(description="ID from component library")
    role: str = Field(description="Role")
    domain: str = Field(description="Functional domain")
    phase: str = Field(description="Phase")
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
    """Connection relationship."""
    edge_id: str = Field(description="Format: E + 3~6 digits")
    from_inst: str = Field(description="Source ID")
    from_port: str = Field(description="Source port")
    to_inst: str = Field(description="Target ID")
    to_port: str = Field(description="Target port")
    channel: str = Field(description="Channel type")
    domain: str = Field(description="Connection domain")
    phase: str = Field(description="Connection phase")


class OperationStep(BaseModel):
    """Operation step."""
    step_id: int = Field(description="Step ID")
    action: str = Field(description="Action type")
    target_inst: str = Field(description="Target ID")
    target_port: str = Field(default="")
    value: str = Field(default="")
    duration_s: int = Field(description="Duration")
    depends_on: str = Field(default="")
    domain: str = Field(description="Operation domain")
    phase: str = Field(description="Operation phase")


class BioChipDesign(BaseModel):
    """Complete biochip design."""
    reasoning: str = Field(description="Design/review reasoning notes")
    instances: list[ComponentInstance]
    connections: list[Connection]
    plan: list[OperationStep]
