from enum import Enum


class WebSocketEventType(str, Enum):
    """
    Enumerated real-time events sent or received via WebSockets.
    """

    PARTICIPANT_JOINED = "PARTICIPANT_JOINED"
    PARTICIPANT_LEFT = "PARTICIPANT_LEFT"
    QUESTION_ACTIVATED = "QUESTION_ACTIVATED"
    ANSWER_SUBMITTED = "ANSWER_SUBMITTED"
    LEADERBOARD_UPDATED = "LEADERBOARD_UPDATED"
    ROOM_STATUS_CHANGED = "ROOM_STATUS_CHANGED"
    ERROR = "ERROR"
