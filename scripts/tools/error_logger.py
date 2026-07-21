"""
向后兼容包装器 —— 导入已迁移至 error_tracker 包。

如已安装 error_tracker 包，本文件的所有功能仍可使用。
推荐直接使用新包:

    from error_tracker import setup, ErrorLogCenter, ErrorSource

安装:
    pip install -e scripts/tools/error_tracker
"""

# 尝试从已安装的包导入，否则回退到本地路径
try:
    from error_tracker import *  # noqa: F401, F403
except ImportError:
    import sys
    import os
    _pkg_dir = os.path.join(os.path.dirname(__file__), "error_tracker")
    sys.path.insert(0, _pkg_dir)
    from error_tracker import *  # noqa: F401, F403

# 向后兼容别名
setup_error_logging = setup  # noqa: F405

if __name__ == "__main__":
    center = setup_error_logging("test_logs")
    print(f"日志文件: {center.log_file}")
    center.shutdown()
    import os, glob
    for f in glob.glob("test_logs/*.txt"):
        print(open(f).read())
    import shutil
    shutil.rmtree("test_logs", ignore_errors=True)
