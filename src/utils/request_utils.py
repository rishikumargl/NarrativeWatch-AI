import uuid
from datetime import datetime


def generate_request_id() -> str:
    """Generate unique request ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"req_{timestamp}_{unique_id}"


def format_response_time(seconds: float) -> str:
    """Format processing time in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.2f}s"
