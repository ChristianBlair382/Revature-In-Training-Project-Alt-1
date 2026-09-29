from enum import Enum

class EQUIPMENT_STATUS(str, Enum):
    IDLE = "Idle"
    IN_USE = "In-Use"
    MAINTENANCE = "Maintenance"
    RETIRED = "Retired"

class FIELD_JOB_STATUS(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class FIELD_JOB_PRIORITY(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    CRITICAL = "Critical"

class USER_ROLE(str, Enum):
    FOA = "Field_Operations_Admin"
    FH = "Field_Hand"
    AUD = "Auditor"