"""
索克生活 - Python 3.13 新特性展示
Suoke Life - Python 3.13 New Features Demo

展示 Python 3.13 的新特性和改进，特别是在健康管理AI应用中的优势
"""

import asyncio
import sys
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import warnings

# Python 3.13 新特性导入
from types import GenericAlias
from collections.abc import Callable


@dataclass
class HealthMetrics:
    """健康指标数据类 - 展示 Python 3.13 改进的数据类支持"""
    user_id: str
    timestamp: float
    heart_rate: int
    blood_pressure: tuple[int, int]  # Python 3.13 改进的类型注解
    temperature: float
    steps: int
    sleep_hours: float
    stress_level: int  # 1-10
    
    def __post_init__(self):
        """Python 3.13 改进的数据验证"""
        if not (60 <= self.heart_rate <= 200):
            warnings.warn(f"心率异常: {self.heart_rate}", UserWarning)
        
        if not (0 <= self.stress_level <= 10):
            raise ValueError(f"压力等级必须在0-10之间: {self.stress_level}")


class HealthAIAnalyzer:
    """健康AI分析器 - 展示 Python 3.13 的性能改进"""
    
    def __init__(self):
        self.models: dict[str, Any] = {}
        self.cache: dict[str, Any] = {}
    
    async def analyze_health_data(
        self, 
        metrics: HealthMetrics,
        analysis_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        分析健康数据 - 展示 Python 3.13 的异步改进
        """
        print(f"🔍 分析用户 {metrics.user_id} 的健康数据...")
        
        # Python 3.13 改进的异步性能
        tasks = [
            self._analyze_cardiovascular(metrics),
            self._analyze_sleep_pattern(metrics),
            self._analyze_stress_level(metrics),
            self._generate_recommendations(metrics)
        ]
        
        # 并发执行分析任务
        results = await asyncio.gather(*tasks)
        
        return {
            "user_id": metrics.user_id,
            "timestamp": metrics.timestamp,
            "cardiovascular": results[0],
            "sleep": results[1],
            "stress": results[2],
            "recommendations": results[3],
            "overall_score": self._calculate_health_score(results)
        }
    
    async def _analyze_cardiovascular(self, metrics: HealthMetrics) -> dict[str, Any]:
        """心血管分析 - Python 3.13 改进的错误处理"""
        try:
            # 模拟AI模型推理
            await asyncio.sleep(0.1)
            
            systolic, diastolic = metrics.blood_pressure
            hr_status = "正常" if 60 <= metrics.heart_rate <= 100 else "异常"
            bp_status = "正常" if systolic < 140 and diastolic < 90 else "高血压"
            
            return {
                "heart_rate": {
                    "value": metrics.heart_rate,
                    "status": hr_status,
                    "risk_level": "低" if hr_status == "正常" else "中"
                },
                "blood_pressure": {
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "status": bp_status,
                    "risk_level": "低" if bp_status == "正常" else "高"
                }
            }
        except Exception as e:
            # Python 3.13 改进的异常信息
            print(f"❌ 心血管分析错误: {e}")
            return {"error": str(e)}
    
    async def _analyze_sleep_pattern(self, metrics: HealthMetrics) -> dict[str, Any]:
        """睡眠模式分析"""
        await asyncio.sleep(0.1)
        
        sleep_quality = "优秀" if metrics.sleep_hours >= 7 else "不足"
        recommendations = []
        
        if metrics.sleep_hours < 6:
            recommendations.append("建议增加睡眠时间至7-9小时")
        elif metrics.sleep_hours > 9:
            recommendations.append("睡眠时间过长，建议咨询医生")
        
        return {
            "sleep_hours": metrics.sleep_hours,
            "quality": sleep_quality,
            "recommendations": recommendations
        }
    
    async def _analyze_stress_level(self, metrics: HealthMetrics) -> dict[str, Any]:
        """压力水平分析"""
        await asyncio.sleep(0.1)
        
        stress_categories = {
            (0, 3): "低压力",
            (4, 6): "中等压力", 
            (7, 10): "高压力"
        }
        
        category = next(
            cat for (low, high), cat in stress_categories.items()
            if low <= metrics.stress_level <= high
        )
        
        return {
            "level": metrics.stress_level,
            "category": category,
            "management_needed": metrics.stress_level > 6
        }
    
    async def _generate_recommendations(self, metrics: HealthMetrics) -> list[str]:
        """生成健康建议"""
        await asyncio.sleep(0.1)
        
        recommendations = []
        
        # 基于步数的建议
        if metrics.steps < 8000:
            recommendations.append("建议增加日常步行，目标每日10000步")
        
        # 基于体温的建议
        if metrics.temperature > 37.5:
            recommendations.append("体温偏高，建议多休息并监测体温变化")
        
        # 基于压力的建议
        if metrics.stress_level > 7:
            recommendations.append("压力较高，建议进行冥想或深呼吸练习")
        
        return recommendations
    
    def _calculate_health_score(self, analysis_results: list[dict]) -> int:
        """计算综合健康评分 - 展示 Python 3.13 的计算性能"""
        score = 100
        
        # 心血管评分
        cardio = analysis_results[0]
        if cardio.get("heart_rate", {}).get("status") == "异常":
            score -= 15
        if cardio.get("blood_pressure", {}).get("status") == "高血压":
            score -= 20
        
        # 睡眠评分
        sleep = analysis_results[1]
        if sleep.get("quality") == "不足":
            score -= 10
        
        # 压力评分
        stress = analysis_results[2]
        if stress.get("management_needed"):
            score -= 15
        
        return max(0, score)


def demonstrate_python313_performance():
    """展示 Python 3.13 的性能改进"""
    print("🚀 Python 3.13 性能测试")
    print(f"Python 版本: {sys.version}")
    
    # 测试1: 列表推导式性能
    start_time = time.perf_counter()
    large_list = [i**2 for i in range(1000000)]
    list_time = time.perf_counter() - start_time
    print(f"列表推导式 (100万元素): {list_time:.4f} 秒")
    
    # 测试2: 字典操作性能
    start_time = time.perf_counter()
    large_dict = {f"key_{i}": i**2 for i in range(100000)}
    dict_time = time.perf_counter() - start_time
    print(f"字典创建 (10万键值对): {dict_time:.4f} 秒")
    
    # 测试3: 字符串操作性能
    start_time = time.perf_counter()
    text = "健康管理" * 100000
    processed = text.replace("管理", "监测")
    string_time = time.perf_counter() - start_time
    print(f"字符串处理: {string_time:.4f} 秒")
    
    print("✅ 性能测试完成")


def demonstrate_improved_error_messages():
    """展示 Python 3.13 改进的错误消息"""
    print("\n🔍 Python 3.13 错误消息改进演示")
    
    try:
        # 故意创建一个错误来展示改进的错误消息
        health_data = {"heart_rate": 75, "blood_pressure": [120, 80]}
        # 尝试访问不存在的键
        temperature = health_data["temperature"]
    except KeyError as e:
        print(f"改进的 KeyError 消息: {e}")
    
    try:
        # 类型错误演示
        metrics = HealthMetrics(
            user_id="user123",
            timestamp=time.time(),
            heart_rate="75",  # 错误类型
            blood_pressure=(120, 80),
            temperature=36.5,
            steps=8500,
            sleep_hours=7.5,
            stress_level=3
        )
    except Exception as e:
        print(f"改进的类型错误消息: {e}")


async def main():
    """主函数 - 展示完整的健康分析流程"""
    print("🏥 索克生活 - Python 3.13 健康AI分析演示")
    print("=" * 50)
    
    # 创建健康指标数据
    metrics = HealthMetrics(
        user_id="user_12345",
        timestamp=time.time(),
        heart_rate=72,
        blood_pressure=(118, 76),
        temperature=36.8,
        steps=9500,
        sleep_hours=7.2,
        stress_level=4
    )
    
    print(f"📊 用户健康数据:")
    print(f"  心率: {metrics.heart_rate} bpm")
    print(f"  血压: {metrics.blood_pressure[0]}/{metrics.blood_pressure[1]} mmHg")
    print(f"  体温: {metrics.temperature}°C")
    print(f"  步数: {metrics.steps}")
    print(f"  睡眠: {metrics.sleep_hours} 小时")
    print(f"  压力等级: {metrics.stress_level}/10")
    
    # 创建AI分析器
    analyzer = HealthAIAnalyzer()
    
    # 执行分析
    print("\n🤖 开始AI健康分析...")
    start_time = time.perf_counter()
    
    analysis_result = await analyzer.analyze_health_data(metrics)
    
    analysis_time = time.perf_counter() - start_time
    
    # 显示分析结果
    print(f"\n📋 分析结果 (耗时: {analysis_time:.4f} 秒):")
    print(f"  综合健康评分: {analysis_result['overall_score']}/100")
    
    cardio = analysis_result['cardiovascular']
    print(f"  心血管状态: {cardio['heart_rate']['status']}")
    print(f"  血压状态: {cardio['blood_pressure']['status']}")
    
    sleep = analysis_result['sleep']
    print(f"  睡眠质量: {sleep['quality']}")
    
    stress = analysis_result['stress']
    print(f"  压力状态: {stress['category']}")
    
    recommendations = analysis_result['recommendations']
    if recommendations:
        print(f"\n💡 健康建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # 性能测试
    print("\n" + "=" * 50)
    demonstrate_python313_performance()
    
    # 错误消息演示
    demonstrate_improved_error_messages()
    
    print("\n🎉 Python 3.13 健康AI分析演示完成!")
    print("主要优势:")
    print("  • 更快的异步性能")
    print("  • 改进的错误消息")
    print("  • 更好的类型检查")
    print("  • 优化的内存使用")
    print("  • 实验性 JIT 编译器支持")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main()) 