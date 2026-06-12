from enum import Enum


class AnalysisType(str, Enum):
    PAGE = "page"
    POST = "post"
    ACCOUNT = "account"


class BiasType(str, Enum):
    POLITICAL = "political"
    GENDER = "gender"
    IDEOLOGICAL = "ideological"
    RACIAL = "racial"
    RELIGIOUS = "religious"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
