# error-tracker

可扩展的错误日志追踪包 —— 将所有报错/异常按时间戳记录到 txt 文件。

纯 Python 实现，零外部依赖，Python 3.8+ 即可运行。

---

## 安装

```bash
# 开发模式安装（推荐，方便修改）
pip install -e .

# 或打包为 wheel 后安装
pip install build && python3 -m build --wheel
pip install dist/error_tracker-0.1.0-py3-none-any.whl

# 或直接从 git 安装
pip install git+https://github.com/你的用户名/error-tracker.git
```

## 移植到其他电脑

纯 Python，零依赖，四种方式任选：

| 方式 | 命令 |
|------|------|
| 复制文件夹 | `scp -r error_tracker/ user@pc:/path/` → `pip install -e .` |
| 打 wheel 包 | `python3 -m build --wheel` → 拷贝 `.whl` → `pip install xxx.whl` |
| 不安装直接用 | `export PYTHONPATH="/path/to/error_tracker:$PYTHONPATH"` |
| GitHub 安装 | `pip install git+https://github.com/xxx/error-tracker.git` |

---

## 快速开始

```python
from error_tracker import setup

# 一行启动：Python 异常 + OS 信号 + 终端输出捕获（默认）
center = setup("logs")

# 所有未捕获异常 + 终端 stderr 自动写入 logs/errors_20260706_211800.txt
raise ValueError("测试异常")
```

> **提示**：`setup()` 默认启用终端输出捕获（`capture_console=True`），可将 Hydra 等框架内部 try/except 截住的异常也写入日志。如果不需要，传 `setup("logs", capture_console=False)`。

日志输出格式：

```
2026-07-06 21:18:00 [INFO] ==== 日志会话开始: logs/errors_20260706_211800.txt ====
2026-07-06 21:18:00 [INFO] [Python] Python 异常捕获已启用
2026-07-06 21:18:00 [INFO] 来源已注册: Python
2026-07-06 21:18:00 [INFO] [Signal] 信号捕获已启用 (4 signals)
2026-07-06 21:18:00 [INFO] 来源已注册: Signal
2026-07-06 21:18:00 [CRITICAL] [Python] 未捕获异常:
Traceback (most recent call last):
  ...
ValueError: 测试异常
2026-07-06 21:18:00 [INFO] ==== 日志会话结束 ====
```

---

## 进阶用法

```python
from error_tracker import ErrorLogCenter

center = ErrorLogCenter("logs", filename_prefix="my_app")

# ---- 内置错误来源 ----
center.enable_python_exceptions()                  # Python 未捕获异常
center.enable_signals()                            # SIGTERM / SIGSEGV / SIGINT
center.enable_console_capture()                    # 捕获 stdout/stderr（自动分级）

# 捕获子进程输出（自动识别 ERROR/WARNING）
center.capture_subprocess(
    ["python", "train.py", "--task", "my_dog_flat"],
    name="Training",
    cwd="/home/user/project",
)

# 监控外部日志文件（类似 tail -f）
center.monitor_external_log(
    "/home/user/.isaac-sim/kit/logs/Kit.log",
    name="IsaacSim",
    poll_interval=2.0,
)

# ... 程序运行 ...

center.shutdown()  # 显式关闭（进程退出也会自动关闭）
```

### 为什么需要终端输出捕获？

某些框架（如 Hydra、wandb）在内部 `try/except` 后直接 `sys.exit()`，异常不会冒泡到 `sys.excepthook`，因此 `PythonExceptionSource` 无法捕获。但它们会把 traceback 打印到 `stderr`。

`ConsoleCaptureSource` 接管 `sys.stdout` / `sys.stderr`，将终端输出同步写入日志文件，且 **stderr 自动分级**：

| stderr 内容含 | 日志级别 |
|---|---|
| `error` / `traceback` / `cuda out of memory` / … | `ERROR` |
| `warn` / `deprecat` / … | `WARNING` |
| 其他 | `INFO` |

---

## 自定义错误来源

继承 `ErrorSource`，实现 `start()` 即可：

```python
from error_tracker import ErrorLogCenter, ErrorSource

class MotorErrorSource(ErrorSource):
    """监控电机通信错误"""
    def start(self):
        self._active = True
        # 你的串口/W.BUS 监听逻辑...
        self.log_info("电机监控已启动")
        # 检测到错误时:
        self.log_error("电机丢帧，CH1 超时")
        # 检测到警告时:
        self.log_warning("电机温度偏高: 65°C")

class GPUSource(ErrorSource):
    """监控 GPU 异常"""
    def start(self):
        self._active = True
        # 轮询 nvidia-smi 或 hook CUDA API...
        self.log_error("CUDA out of memory")

center = ErrorLogCenter("logs")
center.add_source(MotorErrorSource(center._write))
center.add_source(GPUSource(center._write))
```

---

## 架构

```
ErrorLogCenter (单例，管理日志文件 + 所有来源)
  │
  ├── ConsoleCaptureSource    ← 捕获 stdout/stderr，绕过 Hydra 等框架
  ├── PythonExceptionSource   ← 捕获 Python 未处理异常
  ├── SubprocessSource        ← 捕获子进程 stderr/stdout
  ├── SignalSource            ← 捕获 SIGTERM / SIGSEGV / SIGINT
  ├── ExternalLogSource       ← tail -f 外部日志文件
  │
  └── 任意自定义 ErrorSource  ← 继承基类，想加什么加什么
```

---

## API 参考

### ErrorLogCenter

| 方法 | 说明 |
|------|------|
| `ErrorLogCenter(log_dir, filename_prefix)` | 创建日志中心（单例） |
| `.add_source(source)` | 注册并启动错误来源 |
| `.remove_source(name)` | 移除并停止来源 |
| `.enable_console_capture(name)` | 快捷启用 stdout/stderr 捕获（自动分级） |
| `.enable_python_exceptions()` | 快捷启用 Python 异常捕获 |
| `.enable_signals(signals)` | 快捷启用信号捕获 |
| `.capture_subprocess(cmd, name, cwd, env)` | 快捷捕获子进程 |
| `.monitor_external_log(path, name, interval)` | 快捷监控外部日志 |
| `.log_file` | 只读属性，当前日志文件路径 |
| `.sources` | 只读属性，已注册来源的 dict |
| `.shutdown()` | 停止所有来源，关闭日志文件 |

### ErrorSource（基类）

| 方法 | 说明 |
|------|------|
| `start()` | **抽象方法**，子类必须实现 |
| `stop()` | 停止监听 |
| `log_error(msg)` | 写入 ERROR 级别日志 |
| `log_warning(msg)` | 写入 WARNING 级别日志 |
| `log_info(msg)` | 写入 INFO 级别日志 |
| `is_active` | 只读属性，是否正在运行 |

### 快捷函数

```python
from error_tracker import setup

# 等价于: ErrorLogCenter("logs") + python_exceptions + signals + console_capture
center = setup("logs")

# 不需要捕获终端输出时
center = setup("logs", capture_console=False)
```

---

## 兼容旧代码

原有的 `error_logger.py` 仍可使用：

```python
import error_logger
center = error_logger.setup_error_logging("logs")
```

