#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 A2A 智能体网络监控器
Suoke Life A2A Agent Network Monitor

实时监控智能体网络的状态、性能和健康度
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from a2a_agent_network import create_suoke_life_a2a_network

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """智能体指标"""
    agent_id: str
    name: str
    status: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    last_activity: str
    uptime: float
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        return 1.0 - self.success_rate

@dataclass
class NetworkMetrics:
    """网络指标"""
    total_agents: int
    active_agents: int
    total_workflows: int
    network_uptime: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    peak_concurrent_requests: int
    
    @property
    def success_rate(self) -> float:
        """网络成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

class A2ANetworkMonitor:
    """A2A 网络监控器"""
    
    def __init__(self, network_config: Dict[str, Any] = None):
        """
        初始化网络监控器
        
        Args:
            network_config: 网络配置
        """
        self.network = create_suoke_life_a2a_network(network_config)
        self.start_time = time.time()
        self.metrics_history = []
        self.agent_metrics = {}
        self.network_metrics = NetworkMetrics(
            total_agents=4,
            active_agents=0,
            total_workflows=3,
            network_uptime=0.0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            peak_concurrent_requests=0
        )
        
        # 初始化智能体指标
        self._init_agent_metrics()
        
        logger.info("A2A 网络监控器初始化完成")
    
    def _init_agent_metrics(self):
        """初始化智能体指标"""
        agents = [
            ("xiaoai", "小艾智能体"),
            ("xiaoke", "小克智能体"),
            ("laoke", "老克智能体"),
            ("soer", "索儿智能体")
        ]
        
        for agent_id, name in agents:
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                name=name,
                status="inactive",
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.0,
                last_activity="",
                uptime=0.0
            )
    
    async def start_monitoring(self):
        """开始监控"""
        try:
            # 启动网络
            await self.network.start_network()
            
            # 更新智能体状态
            for agent_id in self.agent_metrics:
                self.agent_metrics[agent_id].status = "active"
                self.agent_metrics[agent_id].last_activity = datetime.now().isoformat()
            
            self.network_metrics.active_agents = len(self.agent_metrics)
            
            logger.info("网络监控已启动")
            
        except Exception as e:
            logger.error(f"启动监控失败: {e}")
            raise
    
    async def stop_monitoring(self):
        """停止监控"""
        try:
            await self.network.stop_network()
            
            # 更新智能体状态
            for agent_id in self.agent_metrics:
                self.agent_metrics[agent_id].status = "inactive"
            
            self.network_metrics.active_agents = 0
            
            logger.info("网络监控已停止")
            
        except Exception as e:
            logger.error(f"停止监控失败: {e}")
            raise
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集指标数据"""
        try:
            # 获取网络状态
            network_status = await self.network.get_agent_status()
            
            # 更新网络运行时间
            self.network_metrics.network_uptime = time.time() - self.start_time
            
            # 更新智能体运行时间
            for agent_id in self.agent_metrics:
                if self.agent_metrics[agent_id].status == "active":
                    self.agent_metrics[agent_id].uptime = self.network_metrics.network_uptime
            
            # 构建指标报告
            metrics_report = {
                "timestamp": datetime.now().isoformat(),
                "network_metrics": asdict(self.network_metrics),
                "agent_metrics": {
                    agent_id: asdict(metrics) 
                    for agent_id, metrics in self.agent_metrics.items()
                },
                "network_status": network_status
            }
            
            # 保存到历史记录
            self.metrics_history.append(metrics_report)
            
            # 保持最近100条记录
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics_report
            
        except Exception as e:
            logger.error(f"收集指标失败: {e}")
            return {"error": str(e)}
    
    async def test_agent_performance(self, agent_id: str, test_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """测试智能体性能"""
        try:
            if agent_id not in self.agent_metrics:
                return {"error": f"智能体 {agent_id} 不存在"}
            
            results = []
            total_time = 0.0
            successful_count = 0
            
            for request in test_requests:
                start_time = time.time()
                
                try:
                    # 处理请求
                    result = await self.network.process_user_request(request)
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if result.get("success", False):
                        successful_count += 1
                    
                    results.append({
                        "request": request,
                        "result": result,
                        "response_time": response_time,
                        "success": result.get("success", False)
                    })
                    
                    total_time += response_time
                    
                except Exception as e:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    results.append({
                        "request": request,
                        "result": {"error": str(e)},
                        "response_time": response_time,
                        "success": False
                    })
                    
                    total_time += response_time
            
            # 更新智能体指标
            agent_metrics = self.agent_metrics[agent_id]
            agent_metrics.total_requests += len(test_requests)
            agent_metrics.successful_requests += successful_count
            agent_metrics.failed_requests += (len(test_requests) - successful_count)
            agent_metrics.avg_response_time = total_time / len(test_requests)
            agent_metrics.last_activity = datetime.now().isoformat()
            
            # 更新网络指标
            self.network_metrics.total_requests += len(test_requests)
            self.network_metrics.successful_requests += successful_count
            self.network_metrics.failed_requests += (len(test_requests) - successful_count)
            
            performance_report = {
                "agent_id": agent_id,
                "test_count": len(test_requests),
                "successful_count": successful_count,
                "failed_count": len(test_requests) - successful_count,
                "success_rate": successful_count / len(test_requests),
                "avg_response_time": total_time / len(test_requests),
                "total_time": total_time,
                "results": results
            }
            
            return performance_report
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            health_status = {
                "overall_health": "healthy",
                "network_status": "active",
                "agents": {},
                "issues": [],
                "recommendations": []
            }
            
            # 检查智能体健康状态
            for agent_id, metrics in self.agent_metrics.items():
                agent_health = {
                    "status": metrics.status,
                    "health": "healthy",
                    "issues": []
                }
                
                # 检查错误率
                if metrics.error_rate > 0.1:  # 错误率超过10%
                    agent_health["health"] = "warning"
                    agent_health["issues"].append(f"错误率过高: {metrics.error_rate:.2%}")
                    health_status["issues"].append(f"{metrics.name}错误率过高")
                
                # 检查响应时间
                if metrics.avg_response_time > 5.0:  # 响应时间超过5秒
                    agent_health["health"] = "warning"
                    agent_health["issues"].append(f"响应时间过长: {metrics.avg_response_time:.2f}秒")
                    health_status["issues"].append(f"{metrics.name}响应时间过长")
                
                # 检查活动状态
                if metrics.status != "active":
                    agent_health["health"] = "critical"
                    agent_health["issues"].append("智能体未激活")
                    health_status["issues"].append(f"{metrics.name}未激活")
                
                health_status["agents"][agent_id] = agent_health
            
            # 检查网络整体健康状态
            if self.network_metrics.success_rate < 0.9:  # 成功率低于90%
                health_status["overall_health"] = "warning"
                health_status["issues"].append("网络成功率过低")
                health_status["recommendations"].append("检查智能体配置和网络连接")
            
            if self.network_metrics.active_agents < self.network_metrics.total_agents:
                health_status["overall_health"] = "warning"
                health_status["issues"].append("部分智能体未激活")
                health_status["recommendations"].append("重启未激活的智能体")
            
            # 确定整体健康状态
            if any(agent["health"] == "critical" for agent in health_status["agents"].values()):
                health_status["overall_health"] = "critical"
            elif any(agent["health"] == "warning" for agent in health_status["agents"].values()):
                health_status["overall_health"] = "warning"
            
            return health_status
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "overall_health": "critical",
                "error": str(e)
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            "network_metrics": asdict(self.network_metrics),
            "agent_metrics": {
                agent_id: {
                    "name": metrics.name,
                    "status": metrics.status,
                    "success_rate": metrics.success_rate,
                    "avg_response_time": metrics.avg_response_time,
                    "total_requests": metrics.total_requests,
                    "uptime": metrics.uptime
                }
                for agent_id, metrics in self.agent_metrics.items()
            },
            "history_count": len(self.metrics_history)
        }
    
    def export_metrics(self, filename: str = None) -> str:
        """导出指标数据"""
        if filename is None:
            filename = f"a2a_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "network_metrics": asdict(self.network_metrics),
            "agent_metrics": {
                agent_id: asdict(metrics) 
                for agent_id, metrics in self.agent_metrics.items()
            },
            "metrics_history": self.metrics_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filename


async def main():
    """监控器主函数"""
    # 创建监控器
    monitor = A2ANetworkMonitor()
    
    try:
        # 启动监控
        await monitor.start_monitoring()
        
        print("🔍 索克生活 A2A 智能体网络监控器")
        print("=" * 60)
        
        # 收集初始指标
        metrics = await monitor.collect_metrics()
        print(f"✅ 网络启动成功，活跃智能体: {metrics['network_metrics']['active_agents']}")
        
        # 健康检查
        health = await monitor.health_check()
        print(f"🏥 网络健康状态: {health['overall_health']}")
        
        # 性能测试
        test_requests = [
            {
                "user_id": "test_user",
                "message": "我想了解阳虚体质的调理方法",
                "type": "general"
            },
            {
                "user_id": "test_user",
                "message": "帮我定制一些农产品",
                "type": "general"
            },
            {
                "user_id": "test_user",
                "message": "分析我的健康数据",
                "type": "general"
            }
        ]
        
        print("\n🧪 开始性能测试...")
        for agent_id in ["xiaoai", "xiaoke", "laoke", "soer"]:
            performance = await monitor.test_agent_performance(agent_id, test_requests[:1])
            print(f"  {agent_id}: 成功率 {performance['success_rate']:.2%}, "
                  f"平均响应时间 {performance['avg_response_time']:.2f}秒")
        
        # 显示指标摘要
        print("\n📊 指标摘要:")
        summary = monitor.get_metrics_summary()
        network_metrics = summary['network_metrics']
        print(f"  网络成功率: {network_metrics.get('success_rate', 0):.2%}")
        print(f"  总请求数: {network_metrics.get('total_requests', 0)}")
        print(f"  网络运行时间: {network_metrics.get('network_uptime', 0):.1f}秒")
        
        # 导出指标
        filename = monitor.export_metrics()
        print(f"\n💾 指标数据已导出到: {filename}")
        
    except KeyboardInterrupt:
        print("\n⏹️  监控被用户中断")
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
    finally:
        # 停止监控
        await monitor.stop_monitoring()
        print("🔚 监控已停止")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 