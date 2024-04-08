import re
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class LogQuery(BaseModel):
    log_file: str = ""
    amount: Optional[int] = 100
    message: Optional[str] = None


class LogOrder(str, Enum):
    desc = "desc"
    asc = "asc"


class LogLevels(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def get_logs(log_file: str, order: str, amount: int, level: str, message: str):
    with open(f"logs/{log_file}", "r") as file:
        lines = file.readlines()

    if message:
        lines = [line for line in lines if message in line]

    if level:
        lines = [line for line in lines if level in line]

    lines = sorted(lines, reverse=order == "desc")

    lines = lines[:amount]

    # Convert to JSON. Each line is a separate entry in the JSON array.
    json_lines = []
    for line in lines:
        # Adjusting for the format "[yyyy-mm-dd hh:mm:ss] [log level] message"
        date_time, log_level, msg = re.match(
            r"\[(.*?)\] \[(.*?)\] (.*)", line.strip()
        ).groups()
        json_lines.append({"date_time": date_time, "level": log_level, "message": msg})

    return json_lines
