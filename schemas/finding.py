from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FindingType(str, Enum):
    SAST = "SAST"
    LLM = "LLM"
    HYBRID = "HYBRID"

class CodeLocation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    snippet: str

class Remediation(BaseModel):
    description: str
    fixed_code: str
    diff: Optional[str] = None
    references: List[str] = []

class Finding(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    location: CodeLocation
    type: FindingType
    confidence_score: float = 1.0
    remediation: Optional[Remediation] = None
    context_graph: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
