"""
Risk Level Value Object
위험도 수준 값 객체
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class RiskCategory(Enum):
    """위험 분류"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskLevel:
    """위험도 수준 값 객체"""
    
    value: str
    factors: List[str] = None
    score: int = None
    
    def __post_init__(self):
        if self.value not in [level.value for level in RiskCategory]:
            raise ValueError(f"Invalid risk level: {self.value}")
        
        # 기본 점수 설정
        if self.score is None:
            score_map = {
                RiskCategory.LOW.value: 1,
                RiskCategory.MEDIUM.value: 2,
                RiskCategory.HIGH.value: 3,
                RiskCategory.CRITICAL.value: 4
            }
            object.__setattr__(self, 'score', score_map[self.value])
        
        # 기본 위험 요소 설정
        if self.factors is None:
            object.__setattr__(self, 'factors', [])
    
    @classmethod
    def from_factors(cls, factors: List[str]) -> 'RiskLevel':
        """위험 요소로부터 위험도 계산"""
        critical_risk_patterns = [
            'system_critical', 'drop', 'delete_all'
        ]
        
        high_risk_patterns = [
            'delete', 'truncate', 'update', 'insert',
            'patient_id', 'ssn', 'name', 'email', 'phone', 'pii_access'
        ]
        
        medium_risk_patterns = [
            'personal_info', 'medical_record', 'diagnosis',
            'join', 'union', 'subquery', 'patient_data'
        ]
        
        score = 1  # 기본 low risk
        
        # 위험 요소별 점수 누적
        for factor in factors:
            factor_lower = factor.lower()
            if any(pattern in factor_lower for pattern in critical_risk_patterns):
                score = max(score, 4)  # critical risk
            elif any(pattern in factor_lower for pattern in high_risk_patterns):
                score = max(score, 3)  # high risk
            elif any(pattern in factor_lower for pattern in medium_risk_patterns):
                score = max(score, 2)  # medium risk
        
        # 다중 위험 요소 보너스 점수
        if len(factors) >= 4 and score >= 2:  # 4개 이상의 위험 요소가 있고 이미 medium 이상이면
            score = min(4, score + 1)  # critical로 승격
        elif len(factors) >= 3 and score >= 2:  # 3개 이상의 위험 요소가 있고 이미 medium 이상이면
            score = min(4, score + 1)  # 한 단계 상승
        
        level_map = {
            1: RiskCategory.LOW.value,
            2: RiskCategory.MEDIUM.value,
            3: RiskCategory.HIGH.value,
            4: RiskCategory.CRITICAL.value
        }
        
        return cls(value=level_map[score], factors=factors, score=score)
    
    @property
    def category(self) -> RiskCategory:
        """RiskCategory enum 반환"""
        return RiskCategory(self.value)
    
    @property
    def requires_approval(self) -> bool:
        """승인이 필요한 위험도인지 확인"""
        return self.score >= 2  # medium 이상
    
    @property
    def requires_senior_approval(self) -> bool:
        """고위급 승인이 필요한지 확인"""
        return self.score >= 3  # high 이상
    
    @property
    def max_execution_time_minutes(self) -> int:
        """최대 실행 허용 시간 (분)"""
        time_map = {
            1: 60,   # low: 1시간
            2: 30,   # medium: 30분
            3: 15,   # high: 15분
            4: 5     # critical: 5분
        }
        return time_map[self.score]
    
    def add_factor(self, factor: str) -> 'RiskLevel':
        """위험 요소 추가 (불변성 유지)"""
        new_factors = list(self.factors) + [factor]
        return RiskLevel.from_factors(new_factors)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "level": self.value,
            "score": self.score,
            "factors": self.factors,
            "requires_approval": self.requires_approval,
            "requires_senior_approval": self.requires_senior_approval,
            "max_execution_time_minutes": self.max_execution_time_minutes
        }
    
    def __str__(self) -> str:
        return f"{self.value.upper()} (score: {self.score})"