from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional

@dataclass
class JobData:
    job_id: str
    company_name: str
    url: str
    title: str
    description: str
    location: Optional[str] = "N/A"
    posted_at: Optional[str] = "N/A"
    meta_data: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict:
        return asdict(self)
