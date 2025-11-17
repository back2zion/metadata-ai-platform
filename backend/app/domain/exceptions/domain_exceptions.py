"""
Domain Exceptions
도메인 계층 예외 정의
"""


class DomainException(Exception):
    """도메인 예외의 기본 클래스"""
    pass


class InvalidSQLSyntaxError(DomainException):
    """잘못된 SQL 구문 예외"""
    
    def __init__(self, sql: str, message: str = "Invalid SQL syntax"):
        self.sql = sql
        self.message = message
        super().__init__(f"{message}: {sql}")


class SecurityValidationError(DomainException):
    """보안 검증 실패 예외"""
    
    def __init__(self, violations: list, message: str = "Security validation failed"):
        self.violations = violations
        self.message = message
        super().__init__(f"{message}: {', '.join(violations)}")


class MedicalDataAccessError(DomainException):
    """의료 데이터 접근 권한 예외"""
    
    def __init__(self, resource: str, user: str, message: str = "Medical data access denied"):
        self.resource = resource
        self.user = user
        self.message = message
        super().__init__(f"{message}: User '{user}' cannot access '{resource}'")


class PIIDataExposureError(DomainException):
    """개인식별정보 노출 위험 예외"""
    
    def __init__(self, pii_fields: list, message: str = "PII data exposure risk"):
        self.pii_fields = pii_fields
        self.message = message
        super().__init__(f"{message}: Fields {', '.join(pii_fields)}")