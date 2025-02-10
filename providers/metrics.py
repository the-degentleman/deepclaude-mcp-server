from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class RequestMetrics:
    provider: str
    operation: str
    start_time: datetime
    end_time: datetime
    status: str
    error: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time).total_seconds() * 1000 