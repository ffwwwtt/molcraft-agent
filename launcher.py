"""MolCraft Agent Launcher

启动 MolCraft 科研智能体 Web 应用。
用法: python launcher.py [--host HOST] [--port PORT]
"""

import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 加载 .env 配置
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")


def main():
    from server.app import run_server

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8501"))

    # 支持命令行参数覆盖
    args = sys.argv[1:]
    if len(args) >= 1:
        host = args[0]
    if len(args) >= 2:
        port = int(args[1])

    run_server(host=host, port=port)


if __name__ == "__main__":
    main()
