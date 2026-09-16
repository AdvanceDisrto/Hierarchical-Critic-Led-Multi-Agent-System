from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Subsystem = Literal["thermofluids", "microgrid", "orchestration_software"]
SUBSYSTEMS = {"thermofluids", "microgrid", "orchestration_software"}

class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

class Assignment(Model):
    subsystem: Subsystem
    objective: str = Field(min_length=1)
    metrics: list[str]

class Plan(Model):
    rationale: str
    assignments: list[Assignment]

    @model_validator(mode="after")
    def complete(self):
        if len(self.assignments) != 3 or {a.subsystem for a in self.assignments} != SUBSYSTEMS:
            raise ValueError("Director must assign each of the three subsystems exactly once")
        return self

class Specification(Model):
    parameter: str
    value: float
    unit: str
    basis: Literal["target", "calculated", "measured"]
    justification: str
    evidence_ids: list[str]

class Claim(Model):
    number: int = Field(gt=0)
    parent: int | None
    text: str

class Artifact(Model):
    subsystem: Subsystem
    title: str = Field(min_length=1)
    abstract: str
    description: str
    specifications: list[Specification]
    claims: list[Claim]
    trademarks: list[str]

    @model_validator(mode="after")
    def valid_claims(self):
        seen = set()
        for c in self.claims:
            if c.number != len(seen) + 1 or (c.parent is not None and c.parent not in seen):
                raise ValueError("Claims must be sequential with earlier parent references")
            seen.add(c.number)
        return self

class Evidence(Model):
    id: str
    kind: Literal["patent", "trademark", "engineering"]
    source_url: str = Field(pattern=r"^https://")
    retrieved_at: str
    query: str
    excerpt: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

class Review(Model):
    status: Literal["PASSED", "REJECTED", "NEEDS_EVIDENCE"]
    reasoning: str = Field(min_length=1)
    remedies: list[str]
    evidence_ids: list[str]

class Chirp(Model):
    id: str
    run_id: str
    sender: str
    frequency: Literal["thermofluid_telemetry", "grid_load_signals", "software_heartbeat", "global_broadcast"]
    event: Literal["ring", "data_dump", "rejection_alert"]
    payload: dict = Field(default_factory=dict)
    timestamp: float
