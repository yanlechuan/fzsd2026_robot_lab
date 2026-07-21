"""
错误日志中心 —— 统一管理所有错误来源 + 日志文件。

单例模式：全局只有一个 ErrorLogCenter 实例。
"""

from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from .base import ErrorSource
from .sources import (
    ConsoleCaptureSource,
    ExternalLogSource,
    PythonExceptionSource,
    SignalSource,
    SubprocessSource,
)


class ErrorLogCenter:
    """错误日志中心 —— 统一管理所有错误来源 + 日志文件."""

    _instance: Optional["ErrorLogCenter"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir: str = "logs", filename_prefix: str = "errors"):
        if self._initialized:
            return
        self._initialized = True

        self._log_dir = log_dir
        self._sources: Dict[str, ErrorSource] = {}

        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_file = os.path.join(log_dir, f"{filename_prefix}_{timestamp}.txt")

        # ---- 文件 handler ----
        self._file_handler = logging.FileHandler(self._log_file, encoding="utf-8")
        self._file_handler.setLevel(logging.DEBUG)
        self._file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))

        # ---- logger ----
        self._logger = logging.getLogger("ErrorLogCenter")
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(self._file_handler)
        self._logger.propagate = False

        atexit.register(self.shutdown)

        self._write("INFO", f"==== 日志会话开始: {self._log_file} ====")

    # ---- 内部写入 ----
    def _write(self, level: str, message: str) -> None:
        log_method = getattr(self._logger, level.lower(), self._logger.info)
        log_method(message)

    # ---- 来源管理 ----
    def add_source(self, source: ErrorSource) -> ErrorSource:
        """添加并启动一个错误来源."""
        if source.name in self._sources:
            self._write("WARNING", f"来源 '{source.name}' 已存在，将被替换")
            self._sources[source.name].stop()
        self._sources[source.name] = source
        source.start()
        self._write("INFO", f"来源已注册: {source.name}")
        return source

    def remove_source(self, name: str) -> None:
        """移除并停止一个错误来源."""
        if name in self._sources:
            self._sources[name].stop()
            del self._sources[name]
            self._write("INFO", f"来源已移除: {name}")

    # ---- 快捷启用 ----
    def enable_python_exceptions(self) -> PythonExceptionSource:
        return self.add_source(PythonExceptionSource(self._write))

    def enable_signals(
        self, signals: Optional[List[int]] = None
    ) -> SignalSource:
        return self.add_source(SignalSource(self._write, signals))

    def capture_subprocess(
        self,
        cmd: Sequence[str],
        name: str = "Subprocess",
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> SubprocessSource:
        return self.add_source(SubprocessSource(self._write, cmd, name, cwd, env))

    def monitor_external_log(
        self,
        file_path: str,
        name: str = "ExternalLog",
        poll_interval: float = 2.0,
    ) -> ExternalLogSource:
        return self.add_source(
            ExternalLogSource(self._write, file_path, name, poll_interval)
        )

    def enable_console_capture(
        self,
        name: str = "Console",
        capture_stdout: bool = True,
        capture_stderr: bool = True,
    ) -> ConsoleCaptureSource:
        """捕获 stdout/stderr 到日志（适用于 Hydra 等框架）."""
        return self.add_source(
            ConsoleCaptureSource(self._write, name, capture_stdout, capture_stderr)
        )

    # ---- 属性 ----
    @property
    def log_file(self) -> str:
        return self._log_file

    @property
    def sources(self) -> Dict[str, ErrorSource]:
        return dict(self._sources)

    # ---- 生命周期 ----
    def shutdown(self) -> None:
        """停止所有来源，关闭日志（可安全重复调用）."""
        if not self._initialized:
            return
        for source in list(self._sources.values()):
            try:
                source.stop()
            except Exception:
                pass
        self._sources.clear()
        try:
            self._write("INFO", "==== 日志会话结束 ====")
        except Exception:
            pass
        if self._file_handler:
            try:
                self._file_handler.close()
            except Exception:
                pass
            self._file_handler = None
        self._initialized = False
        ErrorLogCenter._instance = None
