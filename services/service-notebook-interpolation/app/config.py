from typing import Optional

class ServiceConfig:
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    is_running: bool = False
    progress: int = 0
    logs: list = []
    progress_logs: list = []
