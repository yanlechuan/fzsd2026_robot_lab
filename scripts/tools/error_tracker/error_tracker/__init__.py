"""
error_tracker —— 可扩展的错误日志追踪包。

一键启动:
    from error_tracker import setup
    center = setup("logs")

手动控制:
    from error_tracker import ErrorLogCenter, ErrorSource
    center = ErrorLogCenter("logs")
    center.enable_python_exceptions()
    center.enable_signals()
    center.capture_subprocess(["python", "train.py"])

自定义来源:
    class MySource(ErrorSource):
        def start(self):
            self._active = True
            self.log_info("自定义来源已启动")

    center.add_source(MySource(center._write))
"""

from ._version import __version__
from .base import ErrorSource
from .center import ErrorLogCenter
from .sources import (
    ConsoleCaptureSource,
    ExternalLogSource,
    PythonExceptionSource,
    SignalSource,
    SubprocessSource,
)


def setup(log_dir: str = "logs", capture_console: bool = True) -> ErrorLogCenter:
    """
    一键启动：Python 异常 + 信号捕获 + 终端输出捕获。

    Args:
        log_dir: 日志目录
        capture_console: 是否捕获 stdout/stderr（默认 True，适用于 Hydra 等框架）

    Returns:
        ErrorLogCenter 实例，可继续添加其他来源
    """
    center = ErrorLogCenter(log_dir)
    center.enable_python_exceptions()
    center.enable_signals()
    if capture_console:
        center.enable_console_capture()
    return center


__all__ = [
    "__version__",
    "ErrorLogCenter",
    "ErrorSource",
    "ConsoleCaptureSource",
    "PythonExceptionSource",
    "SubprocessSource",
    "SignalSource",
    "ExternalLogSource",
    "setup",
]
