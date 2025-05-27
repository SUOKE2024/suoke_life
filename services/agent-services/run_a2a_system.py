#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 A2A 智能体系统启动器
Suoke Life A2A Agent System Launcher

统一的启动脚本，支持多种运行模式
"""

import argparse
import asyncio
import logging
import sys
import os

def run_demo():
    """运行演示模式"""
    print("🎭 启动索克生活 A2A 智能体网络演示")
    print("=" * 60)
    
    from start_a2a_network import main as demo_main
    asyncio.run(demo_main())

def run_monitor():
    """运行监控器"""
    print("🔍 启动索克生活 A2A 智能体网络监控器")
    print("=" * 60)
    
    from a2a_network_monitor import main as monitor_main
    asyncio.run(monitor_main())

def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """运行 Web 仪表板"""
    print("🌐 启动索克生活 A2A 智能体网络 Web 仪表板")
    print("=" * 60)
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print("💡 在浏览器中打开上述地址来访问监控仪表板")
    print("=" * 60)
    
    from a2a_dashboard import run_dashboard
    run_dashboard(host=host, port=port, debug=debug)

def run_interactive():
    """运行交互模式"""
    print("💬 启动索克生活 A2A 智能体网络交互模式")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    
    import subprocess
    import sys
    
    # 启动交互模式
    subprocess.run([sys.executable, "start_a2a_network.py", "interactive"])

def show_status():
    """显示系统状态"""
    print("📊 索克生活 A2A 智能体系统状态")
    print("=" * 60)
    
    try:
        from a2a_agent_network import create_suoke_life_a2a_network
        
        async def check_status():
            network = create_suoke_life_a2a_network()
            status = await network.get_agent_status()
            
            print(f"🤖 智能体总数: {status['total_agents']}")
            print(f"📋 工作流数量: {len(status['workflows'])}")
            print(f"⏰ 时间戳: {status['timestamp']}")
            
            print("\n🤖 智能体详情:")
            for agent_id, agent_info in status['agents'].items():
                print(f"  • {agent_info['name']} ({agent_id})")
                print(f"    状态: {agent_info['status']}")
                print(f"    能力: {len(agent_info['capabilities'])} 项")
            
            print("\n📋 可用工作流:")
            for workflow in status['workflows']:
                print(f"  • {workflow}")
        
        asyncio.run(check_status())
        
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='索克生活 A2A 智能体系统启动器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式说明:
  demo        - 运行预设的演示请求，展示智能体协作能力
  monitor     - 启动命令行监控器，实时监控网络状态和性能
  dashboard   - 启动 Web 仪表板，提供可视化监控界面
  interactive - 启动交互模式，可以直接与智能体对话
  status      - 显示系统当前状态和配置信息

示例:
  python run_a2a_system.py demo                    # 运行演示
  python run_a2a_system.py monitor                 # 启动监控器
  python run_a2a_system.py dashboard               # 启动 Web 仪表板
  python run_a2a_system.py dashboard --port 8080   # 在端口 8080 启动仪表板
  python run_a2a_system.py interactive             # 启动交互模式
  python run_a2a_system.py status                  # 查看系统状态
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['demo', 'monitor', 'dashboard', 'interactive', 'status'],
        help='运行模式'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Web 仪表板主机地址 (仅用于 dashboard 模式)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web 仪表板端口 (仅用于 dashboard 模式)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式 (仅用于 dashboard 模式)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 显示欢迎信息
    print("🚀 索克生活 A2A 智能体系统")
    print("🏥 基于 Google Agent-to-Agent 协议的智能健康管理平台")
    print("🤖 四大智能体: 小艾、小克、老克、索儿")
    print()
    
    try:
        if args.mode == 'demo':
            run_demo()
        elif args.mode == 'monitor':
            run_monitor()
        elif args.mode == 'dashboard':
            run_dashboard(host=args.host, port=args.port, debug=args.debug)
        elif args.mode == 'interactive':
            run_interactive()
        elif args.mode == 'status':
            show_status()
    
    except KeyboardInterrupt:
        print("\n⏹️  程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        if args.log_level == 'DEBUG':
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 