"""
错误来源基类 —— 继承此类即可添加任意错误捕获方式。

示例:
    class MotorErrorSource(ErrorSource):
        def start(self):
            self._active = True
            # 你的监听逻辑...
            self.log_error("电机丢帧")
"""

import abc
from typing import Callable


class ErrorSource(abc.ABC):
    """错误来源基类."""

    def __init__(self, name: str, log_func: Callable[[str, str], None]):
        """
        Args:
            name: 来源名称（会显示在日志中）
            log_func: 写入日志的回调，签名为 log_func(level, message)
        """
        self.name = name
        self._log = log_func
        self._active = False

    @abc.abstractmethod
    def start(self) -> None:
        """启动该来源的监听."""
        ...

    def stop(self) -> None:
        """停止监听（子类可按需重写）."""
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    def log_error(self, msg: str) -> None:
        self._log("ERROR", f"[{self.name}] {msg}")

    def log_warning(self, msg: str) -> None:
        self._log("WARNING", f"[{self.name}] {msg}")

    def log_info(self, msg: str) -> None:
        self._log("INFO", f"[{self.name}] {msg}")
