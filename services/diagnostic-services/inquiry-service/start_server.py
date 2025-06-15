"""
问诊服务启动脚本
"""

import argparse
import asyncio
import os
import sys

# 设置Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from cmd.server import serve


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动问诊服务")
    parser.add_argument(
        "--config",
        default="./config/config.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--mode",
        choices=["grpc", "rest", "both"],
        default="grpc",
        help="启动模式：grpc（仅gRPC）、rest（仅REST API）、both（同时启动）"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="服务端口（覆盖配置文件中的设置）"
    )

    args = parser.parse_args()

    # 设置环境变量
    os.environ["CONFIG_PATH"] = args.config

    print("正在启动问诊服务...")
    print(f"配置文件: {args.config}")
    print(f"启动模式: {args.mode}")

    if args.mode == "grpc":
        print("启动gRPC服务...")
        asyncio.run(serve())
    elif args.mode == "rest":
        print("启动REST API服务...")
        from api.enhanced_api_gateway import main as rest_main
        rest_main()
    elif args.mode == "both":
        print("同时启动gRPC和REST API服务...")
        # 在生产环境中，应该使用进程管理器如supervisor来管理多个服务
        import threading
        import time

        # 启动gRPC服务（在后台线程）
        def start_grpc():
            asyncio.run(serve())

        grpc_thread = threading.Thread(target=start_grpc, daemon=True)
        grpc_thread.start()

        # 等待一下让gRPC服务启动
        time.sleep(2)

        # 启动REST API服务（在主线程）
        from api.enhanced_api_gateway import main as rest_main
        rest_main()

if __name__ == "__main__":
    main()
