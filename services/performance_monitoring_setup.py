#!/usr/bin/env python3
"""
索克生活项目 - 性能监控系统设置
实施业务指标监控和性能瓶颈识别
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.monitoring_active = False
        self.metrics_data = {
            "system_metrics": [],
            "service_metrics": [],
            "business_metrics": [],
            "alerts": []
        }
        self.thresholds = {
            "cpu_usage": 80.0,  # CPU使用率阈值
            "memory_usage": 85.0,  # 内存使用率阈值
            "disk_usage": 90.0,  # 磁盘使用率阈值
            "response_time": 2.0  # 响应时间阈值(秒)
        }
    
    async def start_monitoring(self):
        """启动监控"""
        logger.info("🚀 启动性能监控系统...")
        self.monitoring_active = True
        
        # 启动系统监控线程
        system_thread = threading.Thread(target=self._monitor_system_metrics)
        system_thread.daemon = True
        system_thread.start()
        
        # 启动服务监控线程
        service_thread = threading.Thread(target=self._monitor_service_metrics)
        service_thread.daemon = True
        service_thread.start()
        
        logger.info("✅ 性能监控系统启动完成")
    
    def stop_monitoring(self):
        """停止监控"""
        logger.info("🛑 停止性能监控系统...")
        self.monitoring_active = False
        logger.info("✅ 性能监控系统已停止")
    
    def _monitor_system_metrics(self):
        """监控系统指标"""
        while self.monitoring_active:
            try:
                # 模拟系统指标（在实际环境中应使用psutil）
                cpu_percent = random.uniform(20, 80)
                memory_usage = random.uniform(40, 75)
                disk_usage = random.uniform(30, 60)
                
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_usage,
                    "memory_available": random.uniform(2, 8),  # GB
                    "disk_usage": disk_usage,
                    "disk_free": random.uniform(50, 200)  # GB
                }
                
                self.metrics_data["system_metrics"].append(metrics)
                
                # 检查阈值并生成告警
                self._check_system_thresholds(metrics)
                
                # 保持最近100条记录
                if len(self.metrics_data["system_metrics"]) > 100:
                    self.metrics_data["system_metrics"] = self.metrics_data["system_metrics"][-100:]
                
                time.sleep(10)  # 每10秒采集一次
                
            except Exception as e:
                logger.error(f"系统监控错误: {str(e)}")
                time.sleep(5)
    
    def _monitor_service_metrics(self):
        """监控服务指标"""
        while self.monitoring_active:
            try:
                # 模拟服务指标采集
                services = [
                    "xiaoai-service", "xiaoke-service", "laoke-service", "soer-service",
                    "api-gateway", "user-management-service", "blockchain-service",
                    "ai-model-service", "communication-service"
                ]
                
                for service in services:
                    # 模拟服务健康检查
                    response_time = self._simulate_service_response_time(service)
                    
                    metrics = {
                        "timestamp": datetime.now().isoformat(),
                        "service_name": service,
                        "response_time": response_time,
                        "status": "healthy" if response_time < self.thresholds["response_time"] else "slow",
                        "requests_per_minute": self._simulate_request_rate(),
                        "error_rate": self._simulate_error_rate()
                    }
                    
                    self.metrics_data["service_metrics"].append(metrics)
                    
                    # 检查服务阈值
                    self._check_service_thresholds(metrics)
                
                # 保持最近500条记录
                if len(self.metrics_data["service_metrics"]) > 500:
                    self.metrics_data["service_metrics"] = self.metrics_data["service_metrics"][-500:]
                
                time.sleep(30)  # 每30秒采集一次
                
            except Exception as e:
                logger.error(f"服务监控错误: {str(e)}")
                time.sleep(10)
    
    def _simulate_service_response_time(self, service: str) -> float:
        """模拟服务响应时间"""
        import random
        base_time = {
            "xiaoai-service": 0.5,
            "xiaoke-service": 0.6,
            "laoke-service": 0.4,
            "soer-service": 0.7,
            "api-gateway": 0.2,
            "user-management-service": 0.3,
            "blockchain-service": 1.2,
            "ai-model-service": 1.5,
            "communication-service": 0.8
        }.get(service, 0.5)
        
        # 添加随机波动
        return base_time + random.uniform(-0.2, 0.5)
    
    def _simulate_request_rate(self) -> int:
        """模拟请求速率"""
        import random
        return random.randint(50, 200)
    
    def _simulate_error_rate(self) -> float:
        """模拟错误率"""
        import random
        return random.uniform(0.0, 2.0)
    
    def _check_system_thresholds(self, metrics: Dict[str, Any]):
        """检查系统阈值"""
        alerts = []
        
        if metrics["cpu_usage"] > self.thresholds["cpu_usage"]:
            alerts.append({
                "type": "system",
                "level": "warning",
                "message": f"CPU使用率过高: {metrics['cpu_usage']:.1f}%",
                "timestamp": metrics["timestamp"]
            })
        
        if metrics["memory_usage"] > self.thresholds["memory_usage"]:
            alerts.append({
                "type": "system",
                "level": "warning",
                "message": f"内存使用率过高: {metrics['memory_usage']:.1f}%",
                "timestamp": metrics["timestamp"]
            })
        
        if metrics["disk_usage"] > self.thresholds["disk_usage"]:
            alerts.append({
                "type": "system",
                "level": "critical",
                "message": f"磁盘使用率过高: {metrics['disk_usage']:.1f}%",
                "timestamp": metrics["timestamp"]
            })
        
        for alert in alerts:
            self.metrics_data["alerts"].append(alert)
            logger.warning(f"🚨 {alert['message']}")
    
    def _check_service_thresholds(self, metrics: Dict[str, Any]):
        """检查服务阈值"""
        if metrics["response_time"] > self.thresholds["response_time"]:
            alert = {
                "type": "service",
                "level": "warning",
                "message": f"{metrics['service_name']} 响应时间过长: {metrics['response_time']:.2f}s",
                "timestamp": metrics["timestamp"]
            }
            self.metrics_data["alerts"].append(alert)
            logger.warning(f"🚨 {alert['message']}")
        
        if metrics["error_rate"] > 5.0:
            alert = {
                "type": "service",
                "level": "critical",
                "message": f"{metrics['service_name']} 错误率过高: {metrics['error_rate']:.1f}%",
                "timestamp": metrics["timestamp"]
            }
            self.metrics_data["alerts"].append(alert)
            logger.error(f"🚨 {alert['message']}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_data["system_metrics"]:
            return {"status": "no_data", "message": "暂无监控数据"}
        
        # 最新系统指标
        latest_system = self.metrics_data["system_metrics"][-1]
        
        # 服务状态统计
        service_status = {}
        for metric in self.metrics_data["service_metrics"][-9:]:  # 最近9个服务
            service_status[metric["service_name"]] = metric["status"]
        
        # 告警统计
        recent_alerts = [a for a in self.metrics_data["alerts"] 
                        if (datetime.now() - datetime.fromisoformat(a["timestamp"])).seconds < 300]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "cpu_usage": latest_system["cpu_usage"],
                "memory_usage": latest_system["memory_usage"],
                "disk_usage": latest_system["disk_usage"]
            },
            "service_status": service_status,
            "alerts": {
                "total": len(self.metrics_data["alerts"]),
                "recent": len(recent_alerts),
                "critical": len([a for a in recent_alerts if a["level"]=="critical"])
            },
            "monitoring_active": self.monitoring_active
        }
    
    def save_metrics_report(self) -> str:
        """保存监控报告"""
        report_file = f"performance_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_duration": "实时监控",
            "summary": self.get_performance_summary(),
            "metrics_data": self.metrics_data,
            "thresholds": self.thresholds
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 性能监控报告已保存到: {report_file}")
        return report_file

class BusinessMetricsCollector:
    """业务指标收集器"""
    
    def __init__(self):
        self.business_metrics = {
            "user_activity": [],
            "service_usage": [],
            "health_data_processing": [],
            "ai_model_performance": []
        }
    
    def collect_user_activity_metrics(self):
        """收集用户活动指标"""
        # 模拟用户活动数据
        import random
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "active_users": random.randint(100, 500),
            "new_registrations": random.randint(5, 20),
            "session_duration_avg": random.uniform(10, 30),  # 分钟
            "feature_usage": {
                "health_check": random.randint(50, 150),
                "ai_consultation": random.randint(20, 80),
                "data_analysis": random.randint(10, 40),
                "community_interaction": random.randint(30, 100)
            }
        }
        
        self.business_metrics["user_activity"].append(metrics)
        return metrics
    
    def collect_ai_performance_metrics(self):
        """收集AI模型性能指标"""
        import random
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "model_accuracy": random.uniform(0.85, 0.95),
            "inference_time": random.uniform(0.5, 2.0),  # 秒
            "model_load": random.uniform(0.3, 0.8),  # 负载率
            "successful_predictions": random.randint(100, 300),
            "failed_predictions": random.randint(0, 10)
        }
        
        self.business_metrics["ai_model_performance"].append(metrics)
        return metrics

async def main():
    """主函数"""
    print("📊 索克生活项目 - 性能监控系统设置")
    print("=" * 50)
    
    # 创建监控器
    monitor = PerformanceMonitor()
    business_collector = BusinessMetricsCollector()
    
    try:
        # 启动监控
        await monitor.start_monitoring()
        
        print("🔍 监控系统运行中... (按 Ctrl+C 停止)")
        
        # 运行监控一段时间
        for i in range(12):  # 运行2分钟
            await asyncio.sleep(10)
            
            # 收集业务指标
            if i % 3==0:  # 每30秒收集一次业务指标
                business_collector.collect_user_activity_metrics()
                business_collector.collect_ai_performance_metrics()
            
            # 显示当前状态
            summary = monitor.get_performance_summary()
            print(f"📈 监控状态 - CPU: {summary['system_status']['cpu_usage']:.1f}%, "
                  f"内存: {summary['system_status']['memory_usage']:.1f}%, "
                  f"告警: {summary['alerts']['recent']}")
        
        # 保存报告
        report_file = monitor.save_metrics_report()
        
        print(f"\n✅ 监控完成!")
        print(f"📄 性能报告: {report_file}")
        
        # 显示摘要
        summary = monitor.get_performance_summary()
        print(f"\n📊 性能摘要:")
        print(f"  系统状态: CPU {summary['system_status']['cpu_usage']:.1f}%, "
              f"内存 {summary['system_status']['memory_usage']:.1f}%")
        print(f"  服务状态: {len(summary['service_status'])} 个服务监控中")
        print(f"  告警情况: 总计 {summary['alerts']['total']} 个告警")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断监控")
    except Exception as e:
        logger.error(f"监控失败: {str(e)}")
    finally:
        monitor.stop_monitoring()

if __name__=="__main__":
    asyncio.run(main())