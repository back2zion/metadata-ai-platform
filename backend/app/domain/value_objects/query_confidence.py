"""
Query Confidence Value Object
쿼리 신뢰도 값 객체
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueryConfidence:
    """쿼리 신뢰도 값 객체 (0.0 ~ 1.0)"""
    
    value: float
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValueError("Confidence value must be a number")
        
        if not (0.0 <= self.value <= 1.0):
            raise ValueError("Confidence value must be between 0.0 and 1.0")
    
    @property
    def percentage(self) -> int:
        """백분율로 변환 (0-100)"""
        return int(self.value * 100)
    
    @property
    def level(self) -> str:
        """신뢰도 수준 분류"""
        if self.value >= 0.9:
            return "very_high"
        elif self.value >= 0.8:
            return "high"
        elif self.value >= 0.6:
            return "medium"
        elif self.value >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def is_acceptable(self, threshold: float = 0.7) -> bool:
        """임계값 이상인지 확인"""
        return self.value >= threshold
    
    def __str__(self) -> str:
        return f"{self.percentage}% ({self.level})"