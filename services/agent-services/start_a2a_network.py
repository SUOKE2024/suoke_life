#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 A2A 智能体网络启动脚本
Suoke Life A2A Agent Network Startup Script

启动和测试四大智能体的 A2A 协议网络
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('a2a_network.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    from a2a_agent_network import create_suoke_life_a2a_network
except ImportError as e:
    logger.error(f"导入 A2A 网络模块失败: {e}")
    logger.info("请确保已安装 python-a2a 并且所有智能体模块都可用")
    sys.exit(1)


class A2ANetworkDemo:
    """A2A 智能体网络演示"""
    
    def __init__(self):
        """初始化演示"""
        self.network = None
        self.demo_requests = [
            {
                "user_id": "demo_user_001",
                "message": "我最近总是感觉疲劳，睡眠质量也不好，想了解一下我的体质",
                "type": "workflow",
                "workflow": "健康咨询工作流"
            },
            {
                "user_id": "demo_user_002",
                "message": "我是阳虚体质，想定制一些适合我的有机农产品",
                "type": "workflow", 
                "workflow": "农产品定制工作流"
            },
            {
                "user_id": "demo_user_003",
                "message": "帮我分析一下我的心率数据，最近几天平均心率是75",
                "type": "general"
            },
            {
                "user_id": "demo_user_004",
                "message": "我想学习一些中医养生知识",
                "type": "general"
            },
            {
                "user_id": "demo_user_005",
                "message": "我今天心情不太好，感觉有点焦虑",
                "type": "general"
            }
        ]
    
    async def initialize_network(self):
        """初始化网络"""
        try:
            logger.info("正在初始化索克生活 A2A 智能体网络...")
            
            # 创建网络配置
            config = {
                "xiaoai": {
                    "port": 5001,
                    "host": "localhost"
                },
                "xiaoke": {
                    "port": 5002,
                    "host": "localhost"
                },
                "laoke": {
                    "port": 5003,
                    "host": "localhost"
                },
                "soer": {
                    "port": 5004,
                    "host": "localhost"
                }
            }
            
            # 创建网络实例
            self.network = create_suoke_life_a2a_network(config)
            
            logger.info("A2A 智能体网络初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"网络初始化失败: {e}")
            return False
    
    async def start_network(self):
        """启动网络"""
        try:
            logger.info("正在启动 A2A 智能体网络...")
            await self.network.start_network()
            logger.info("A2A 智能体网络启动成功")
            return True
        except Exception as e:
            logger.error(f"网络启动失败: {e}")
            return False
    
    async def show_network_status(self):
        """显示网络状态"""
        try:
            logger.info("获取网络状态...")
            status = await self.network.get_agent_status()
            
            print("\n" + "="*60)
            print("索克生活 A2A 智能体网络状态")
            print("="*60)
            print(f"网络状态: {status['network_status']}")
            print(f"智能体总数: {status['total_agents']}")
            print(f"可用工作流: {len(status['workflows'])}")
            
            print("\n智能体详情:")
            for agent_id, agent_info in status['agents'].items():
                print(f"  {agent_info['name']} ({agent_id})")
                print(f"    状态: {agent_info['status']}")
                print(f"    能力数量: {len(agent_info['capabilities'])}")
                print(f"    主要能力: {', '.join(list(agent_info['capabilities'])[:3])}")
                print()
            
            print("可用工作流:")
            for workflow in status['workflows']:
                print(f"  • {workflow}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
    
    async def run_demo_requests(self):
        """运行演示请求"""
        try:
            logger.info("开始运行演示请求...")
            
            for i, request in enumerate(self.demo_requests, 1):
                print(f"\n{'='*60}")
                print(f"演示请求 {i}/{len(self.demo_requests)}")
                print(f"{'='*60}")
                print(f"用户ID: {request['user_id']}")
                print(f"请求类型: {request['type']}")
                if request['type'] == 'workflow':
                    print(f"工作流: {request['workflow']}")
                print(f"用户消息: {request['message']}")
                print(f"\n处理中...")
                
                # 处理请求
                result = await self.network.process_user_request(request)
                
                # 显示结果
                print(f"\n处理结果:")
                if result['success']:
                    print(f"✅ 处理成功")
                    if 'result' in result:
                        if isinstance(result['result'], dict):
                            if 'response' in result['result']:
                                print(f"回复: {result['result']['response']}")
                            elif 'workflow' in result['result']:
                                print(f"工作流: {result['result']['workflow']}")
                                print(f"状态: {result['result']['status']}")
                                print(f"步骤数: {len(result['result']['results'])}")
                            else:
                                print(f"结果: {json.dumps(result['result'], ensure_ascii=False, indent=2)}")
                        else:
                            print(f"结果: {result['result']}")
                else:
                    print(f"❌ 处理失败: {result.get('error', '未知错误')}")
                
                # 等待一下再处理下一个请求
                await asyncio.sleep(1)
            
            logger.info("所有演示请求处理完成")
            
        except Exception as e:
            logger.error(f"运行演示请求失败: {e}")
    
    async def interactive_mode(self):
        """交互模式"""
        try:
            print(f"\n{'='*60}")
            print("进入交互模式")
            print("输入 'quit' 或 'exit' 退出")
            print("输入 'status' 查看网络状态")
            print("输入 'help' 查看帮助")
            print(f"{'='*60}")
            
            while True:
                try:
                    user_input = input("\n请输入您的消息: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit']:
                        print("退出交互模式")
                        break
                    elif user_input.lower() == 'status':
                        await self.show_network_status()
                        continue
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    elif not user_input:
                        continue
                    
                    # 处理用户输入
                    request = {
                        "user_id": "interactive_user",
                        "message": user_input,
                        "type": "general"
                    }
                    
                    print("处理中...")
                    result = await self.network.process_user_request(request)
                    
                    if result['success']:
                        if 'result' in result and 'response' in result['result']:
                            print(f"\n回复: {result['result']['response']}")
                        else:
                            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    else:
                        print(f"\n处理失败: {result.get('error', '未知错误')}")
                
                except KeyboardInterrupt:
                    print("\n\n收到中断信号，退出交互模式")
                    break
                except Exception as e:
                    print(f"\n处理输入时出错: {e}")
        
        except Exception as e:
            logger.error(f"交互模式运行失败: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
  quit/exit  - 退出交互模式
  status     - 查看网络状态
  help       - 显示此帮助信息

示例消息:
  "我想了解我的体质"
  "帮我制定健康计划"
  "我想学习中医知识"
  "分析我的健康数据"
  "我心情不好"
  "推荐一些农产品"
        """
        print(help_text)
    
    async def stop_network(self):
        """停止网络"""
        try:
            if self.network:
                logger.info("正在停止 A2A 智能体网络...")
                await self.network.stop_network()
                logger.info("A2A 智能体网络已停止")
        except Exception as e:
            logger.error(f"停止网络失败: {e}")
    
    async def run(self, mode: str = "demo"):
        """运行演示"""
        try:
            # 初始化网络
            if not await self.initialize_network():
                return False
            
            # 启动网络
            if not await self.start_network():
                return False
            
            # 显示网络状态
            await self.show_network_status()
            
            if mode == "demo":
                # 运行演示请求
                await self.run_demo_requests()
            elif mode == "interactive":
                # 进入交互模式
                await self.interactive_mode()
            elif mode == "both":
                # 先运行演示，再进入交互模式
                await self.run_demo_requests()
                await self.interactive_mode()
            
            return True
            
        except Exception as e:
            logger.error(f"运行演示失败: {e}")
            return False
        finally:
            # 停止网络
            await self.stop_network()


async def main():
    """主函数"""
    print("索克生活 A2A 智能体网络演示")
    print("="*60)
    
    # 检查命令行参数
    mode = "demo"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["demo", "interactive", "both"]:
            mode = arg
        else:
            print(f"无效的模式: {arg}")
            print("可用模式: demo, interactive, both")
            return
    
    print(f"运行模式: {mode}")
    
    # 创建并运行演示
    demo = A2ANetworkDemo()
    success = await demo.run(mode)
    
    if success:
        print("\n演示完成！")
    else:
        print("\n演示失败！")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n收到中断信号，程序退出")
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1) 