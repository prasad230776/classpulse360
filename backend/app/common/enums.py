from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class UserStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class InstitutionType(str, Enum):
    COLLEGE = "COLLEGE"
    UNIVERSITY = "UNIVERSITY"
    SCHOOL = "SCHOOL"
    TRAINING_INSTITUTE = "TRAINING_INSTITUTE"
    CORPORATE = "CORPORATE"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class QuestionType(str, Enum):
    MCQ_SINGLE = "MCQ_SINGLE"
    MCQ_MULTIPLE = "MCQ_MULTIPLE"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_ANSWER = "SHORT_ANSWER"
    WORD_CLOUD = "WORD_CLOUD"
    URL = "URL"
    FILE = "FILE"
    TEXT = "TEXT"


class DeliveryMode(str, Enum):
    INTERACTIVE = "INTERACTIVE"
    CLASSROOM_EXAM = "CLASSROOM_EXAM"
    SELF_PRACTICE = "SELF_PRACTICE"
    ASSIGNMENT = "ASSIGNMENT"


class VisibilityType(str, Enum):
    PRIVATE = "PRIVATE"
    INSTITUTION = "INSTITUTION"
    PUBLIC = "PUBLIC"


class SessionStatus(str, Enum):
    DRAFT = "DRAFT"
    WAITING = "WAITING"
    LIVE = "LIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ParticipantStatus(str, Enum):
    JOINED = "JOINED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    DISCONNECTED = "DISCONNECTED"
    ABSENT = "ABSENT"


class AnswerStatus(str, Enum):
    ANSWERED = "ANSWERED"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"


class GradingStatus(str, Enum):
    PENDING = "PENDING"
    GRADED = "GRADED"


class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
