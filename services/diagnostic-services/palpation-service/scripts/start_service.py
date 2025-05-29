#!/usr/bin/env python3
"""
触诊服务启动脚本
提供简化版和完整版两种启动模式
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from palpation_service.config import get_settings


def start_simple_service():
    """启动简化版服务"""
    print("🚀 启动简化版触诊服务...")
    print("=" * 50)
    
    try:
        from palpation_service.simple_main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


def start_full_service():
    """启动完整版服务"""
    print("🚀 启动完整版触诊服务...")
    print("=" * 50)
    
    try:
        from palpation_service.main import PalpationServiceApp
        app_instance = PalpationServiceApp()
        app_instance.run()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示: 如果遇到依赖问题，请尝试使用简化版: --mode simple")
        sys.exit(1)


def show_service_info():
    """显示服务信息"""
    settings = get_settings()
    
    print("📋 服务配置信息")
    print("=" * 50)
    print(f"服务名称: {settings.service.name}")
    print(f"版本: {settings.service.version}")
    print(f"环境: {settings.service.env}")
    print(f"主机: {settings.service.host}")
    print(f"端口: {settings.service.port}")
    print(f"调试模式: {settings.service.debug}")
    print()
    
    print("🔗 服务端点")
    print("=" * 50)
    base_url = f"http://{settings.service.host}:{settings.service.port}"
    print(f"健康检查: {base_url}/health")
    print(f"API文档: {base_url}/docs")
    print(f"指标监控: {base_url}/metrics")
    print(f"配置信息: {base_url}/config")
    print(f"统计信息: {base_url}/stats")
    print()
    
    print("🧪 测试命令")
    print("=" * 50)
    print(f"curl {base_url}/health")
    print(f"curl {base_url}/config")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="索克生活 - 触诊服务启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/start_service.py                    # 启动简化版服务
  python scripts/start_service.py --mode simple      # 启动简化版服务
  python scripts/start_service.py --mode full        # 启动完整版服务
  python scripts/start_service.py --info             # 显示服务信息
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["simple", "full"],
        default="simple",
        help="启动模式: simple(简化版) 或 full(完整版)"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="显示服务配置信息"
    )
    
    args = parser.parse_args()
    
    # 显示欢迎信息
    print("🏥 索克生活 - 触诊服务")
    print("🔬 基于AI的中医触诊分析平台")
    print()
    
    if args.info:
        show_service_info()
        return
    
    if args.mode == "simple":
        start_simple_service()
    elif args.mode == "full":
        start_full_service()


if __name__ == "__main__":
    main() 