from typing import Any, Dict, List, Optional, Union

"""
run_dev - 索克生活项目模块
"""

import sys
from pathlib import Path

from look_service.cmd.server import main

#! / usr / bin / env python3
"""Development server runner for look service."""


# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
