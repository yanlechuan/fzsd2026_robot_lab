"""
内置错误来源集合。

- PythonExceptionSource:  捕获 Python 未处理异常
- SubprocessSource:       捕获子进程 stderr/stdout
- SignalSource:           捕获 OS 信号 (SIGTERM, SIGSEGV...)
- ExternalLogSource:      监控外部日志文件增量
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
import traceback
from typing import Callable, Dict, List, Optional, Sequence

from .base import ErrorSource


class PythonExceptionSource(ErrorSource):
    """捕获当前 Python 进程中所有未处理的异常."""

    def __init__(self, log_func: Callable[[str, str], None]):
        super().__init__("Python", log_func)
        self._original_hook = sys.excepthook
        self._original_thread_hook = None

    def start(self) -> None:
        self._active = True
        sys.excepthook = self._handler
        if hasattr(threading, "excepthook"):
            self._original_thread_hook = threading.excepthook
            threading.excepthook = self._thread_handler
        self.log_info("Python 异常捕获已启用")

    def stop(self) -> None:
        sys.excepthook = self._original_hook
        if self._original_thread_hook and hasattr(threading, "excepthook"):
            threading.excepthook = self._original_thread_hook
        super().stop()

    def _handler(self, exc_type, exc_value, exc_tb):
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self._log("CRITICAL", f"[{self.name}] 未捕获异常:\n{tb_str}")
        self._original_hook(exc_type, exc_value, exc_tb)

    def _thread_handler(self, args):
        tb_str = "".join(traceback.format_exception(
            args.exc_type, args.exc_value, args.exc_traceback
        ))
        self._log("CRITICAL", f"[{self.name}] 线程异常:\n{tb_str}")
        if self._original_thread_hook:
            self._original_thread_hook(args)


class SubprocessSource(ErrorSource):
    """捕获子进程的 stdout/stderr 输出."""

    ERROR_KEYWORDS = (
        "error", "traceback", "exception", "failed", "critical",
        "fatal", "segfault", "[err", "cuda error", "out of memory",
    )
    WARN_KEYWORDS = ("warn", "deprecat")

    def __init__(
        self,
        log_func: Callable[[str, str], None],
        cmd: Sequence[str],
        name: str = "Subprocess",
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, log_func)
        self._cmd = list(cmd)
        self._cwd = cwd
        self._env = env
        self._process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        self._active = True
        self.log_info(f"启动子进程: {' '.join(self._cmd)}")

        self._process = subprocess.Popen(
            self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=self._cwd,
            env=self._env,
        )

        def _reader():
            for line in iter(self._process.stdout.readline, ""):
                line = line.rstrip("\n")
                if not line:
                    continue
                lower = line.lower()
                if any(kw in lower for kw in self.ERROR_KEYWORDS):
                    self.log_error(line)
                elif any(kw in lower for kw in self.WARN_KEYWORDS):
                    self.log_warning(line)
                else:
                    self.log_info(line)
            self._process.stdout.close()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self.log_info("正在终止子进程...")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self.log_warning("子进程被强制终止")
        super().stop()

    @property
    def returncode(self) -> Optional[int]:
        return self._process.poll() if self._process else None

    def wait(self) -> int:
        return self._process.wait() if self._process else -1


class SignalSource(ErrorSource):
    """捕获 OS 信号 (SIGTERM, SIGINT, SIGSEGV 等)."""

    DEFAULT_SIGNALS = [
        signal.SIGTERM,
        signal.SIGINT,
        signal.SIGSEGV,
        signal.SIGABRT,
    ]

    def __init__(
        self,
        log_func: Callable[[str, str], None],
        signals: Optional[List[int]] = None,
    ):
        super().__init__("Signal", log_func)
        self._signals = signals or self.DEFAULT_SIGNALS
        self._originals: Dict[int, object] = {}

    def start(self) -> None:
        self._active = True
        for sig in self._signals:
            if sig in (signal.SIGKILL, signal.SIGSTOP):
                continue
            try:
                self._originals[sig] = signal.signal(sig, self._handler)
            except (ValueError, OSError):
                pass
        self.log_info(f"信号捕获已启用 ({len(self._originals)} signals)")

    def stop(self) -> None:
        for sig, original in self._originals.items():
            try:
                signal.signal(sig, original)
            except (ValueError, OSError):
                pass
        super().stop()

    def _handler(self, signum, frame):
        sig_name = signal.Signals(signum).name
        self.log_error(f"收到信号: {sig_name} ({signum})")
        if signum in (signal.SIGSEGV, signal.SIGABRT, signal.SIGBUS):
            tb_str = "".join(traceback.format_stack(frame))
            self.log_error(f"信号时堆栈:\n{tb_str}")

        # 恢复原始处理器
        original = self._originals.get(signum)
        if callable(original):
            signal.signal(signum, original)

        # SIGINT: 用 raise KeyboardInterrupt 而非 os.kill，避免中断 Isaac Sim 等框架的加载链
        if signum == signal.SIGINT:
            raise KeyboardInterrupt

        # 其他信号：重新发送
        os.kill(os.getpid(), signum)


class ExternalLogSource(ErrorSource):
    """监控外部日志文件的增量内容（类似 tail -f）."""

    def __init__(
        self,
        log_func: Callable[[str, str], None],
        file_path: str,
        name: str = "ExternalLog",
        poll_interval: float = 2.0,
    ):
        super().__init__(name, log_func)
        self._file_path = file_path
        self._poll_interval = poll_interval

    def start(self) -> None:
        self._active = True
        t = threading.Thread(target=self._tail, daemon=True)
        t.start()
        self.log_info(f"监控外部日志: {self._file_path}")

    def _tail(self) -> None:
        waited = 0
        while self._active and not os.path.exists(self._file_path):
            time.sleep(1)
            waited += 1
            if waited > 30:
                self.log_warning(f"等待文件超时: {self._file_path}")
                return

        with open(self._file_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            while self._active:
                line = f.readline()
                if line:
                    line = line.rstrip("\n")
                    if line:
                        self.log_info(line)
                else:
                    time.sleep(self._poll_interval)


class ConsoleCaptureSource(ErrorSource):
    """捕获 stdout/stderr 输出到日志文件。

    适用于 Hydra 等框架——它们内部 try/except 后直接 sys.exit()，
    异常不会冒泡到 sys.excepthook，但会打印到 stderr。
    此来源将终端输出同步写入日志文件。
    """

    def __init__(
        self,
        log_func: Callable[[str, str], None],
        name: str = "Console",
        capture_stdout: bool = True,
        capture_stderr: bool = True,
    ):
        super().__init__(name, log_func)
        self._capture_stdout = capture_stdout
        self._capture_stderr = capture_stderr
        self._orig_stdout = None
        self._orig_stderr = None

    # stderr 自动级别判定的关键词
    _STDERR_ERROR_KW = (
        "error", "traceback", "exception", "failed", "critical",
        "fatal", "segfault", "cuda out of memory", "outofmemory",
        "modulenotfound", "importerror", "keyboardinterrupt",
    )
    _STDERR_WARN_KW = ("warn", "deprecat", "futurewarning", "pendingdeprecation")

    def start(self) -> None:
        self._active = True

        class _TeeWriter:
            """同时写入原始流和日志，stderr 自动判定 ERROR/WARNING/INFO."""
            def __init__(self, original, log_func, stream_name):
                self._original = original
                self._log = log_func
                self._name = stream_name
                self._buffer = ""

            def _level_for(self, line: str) -> str:
                if self._name != "stderr":
                    return "INFO"
                lower = line.lower()
                if any(kw in lower for kw in ConsoleCaptureSource._STDERR_ERROR_KW):
                    return "ERROR"
                if any(kw in lower for kw in ConsoleCaptureSource._STDERR_WARN_KW):
                    return "WARNING"
                return "INFO"

            def write(self, s: str) -> int:
                self._original.write(s)
                self._buffer += s
                if "\n" in self._buffer:
                    lines = self._buffer.split("\n")
                    self._buffer = lines[-1]
                    for line in lines[:-1]:
                        line = line.rstrip("\r")
                        if line:
                            level = self._level_for(line)
                            self._log(level, f"[Console:{self._name}] {line}")
                return len(s)

            def flush(self) -> None:
                self._original.flush()
                if self._buffer:
                    level = self._level_for(self._buffer)
                    self._log(level, f"[Console:{self._name}] {self._buffer}")
                    self._buffer = ""

            def __getattr__(self, name):
                return getattr(self._original, name)

        if self._capture_stdout:
            self._orig_stdout = sys.stdout
            sys.stdout = _TeeWriter(sys.stdout, self._log, "stdout")

        if self._capture_stderr:
            self._orig_stderr = sys.stderr
            sys.stderr = _TeeWriter(sys.stderr, self._log, "stderr")

        self.log_info("终端输出捕获已启用")

    def stop(self) -> None:
        if self._orig_stdout is not None:
            sys.stdout.flush()
            sys.stdout = self._orig_stdout
        if self._orig_stderr is not None:
            sys.stderr.flush()
            sys.stderr = self._orig_stderr
        super().stop()
