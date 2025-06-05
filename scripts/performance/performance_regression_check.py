#!/usr/bin/env python3
"""
性能回归检测脚本
用于CI/CD中自动检测性能回归问题
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class PerformanceRegressionChecker:
    """性能回归检测器"""
    
    def __init__(self):
        self.baseline_dir = Path("performance_baselines")
        self.current_results_dir = Path("current_performance")
        self.report_file = Path("performance_report.md")
        self.threshold_degradation = 0.20  # 20%性能下降阈值
        
    def load_baseline_data(self, service: str) -> Optional[Dict]:
        """加载基线性能数据"""
        baseline_file = self.baseline_dir / f"{service}_baseline.json"
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                return json.load(f)
        return None
    
    def run_current_performance_tests(self) -> Dict[str, Dict]:
        """运行当前性能测试"""
        results = {}
        
        # Auth-Service性能测试
        print("运行Auth-Service性能测试...")
        auth_result = self._run_service_performance_test(
            "auth-service",
            "services/auth-service",
            "tests/test_auth_advanced_fixed.py::TestAuthServicePerformance"
        )
        if auth_result:
            results["auth-service"] = auth_result
        
        # User-Service性能测试
        print("运行User-Service性能测试...")
        user_result = self._run_service_performance_test(
            "user-service", 
            "services/user-service",
            "test/test_performance_simple.py::TestUserServicePerformanceSimple"
        )
        if user_result:
            results["user-service"] = user_result
        
        return results
    
    def _run_service_performance_test(self, service_name: str, service_path: str, test_path: str) -> Optional[Dict]:
        """运行单个服务的性能测试"""
        try:
            # 切换到服务目录
            original_dir = os.getcwd()
            os.chdir(service_path)
            
            # 运行性能测试
            cmd = [
                "python", "-m", "pytest", test_path,
                "--benchmark-only",
                "--benchmark-json=benchmark_results.json",
                "-v"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # 读取结果
            if os.path.exists("benchmark_results.json"):
                with open("benchmark_results.json", 'r') as f:
                    benchmark_data = json.load(f)
                
                # 解析性能指标
                performance_metrics = self._parse_benchmark_results(benchmark_data)
                return performance_metrics
            
        except Exception as e:
            print(f"运行{service_name}性能测试失败: {e}")
        finally:
            os.chdir(original_dir)
        
        return None
    
    def _parse_benchmark_results(self, benchmark_data: Dict) -> Dict:
        """解析benchmark结果"""
        metrics = {}
        
        if "benchmarks" in benchmark_data:
            for benchmark in benchmark_data["benchmarks"]:
                test_name = benchmark["name"]
                stats = benchmark["stats"]
                
                metrics[test_name] = {
                    "mean": stats["mean"],
                    "min": stats["min"],
                    "max": stats["max"],
                    "stddev": stats["stddev"],
                    "median": stats["median"],
                    "ops_per_sec": 1.0 / stats["mean"] if stats["mean"] > 0 else 0
                }
        
        return metrics
    
    def compare_performance(self, current_results: Dict[str, Dict]) -> Dict[str, Dict]:
        """比较当前性能与基线性能"""
        comparison_results = {}
        
        for service, current_metrics in current_results.items():
            baseline_metrics = self.load_baseline_data(service)
            
            if not baseline_metrics:
                print(f"警告: 没有找到{service}的基线数据")
                comparison_results[service] = {
                    "status": "no_baseline",
                    "message": "没有基线数据，将当前结果作为新基线"
                }
                self._save_baseline_data(service, current_metrics)
                continue
            
            # 比较性能指标
            service_comparison = self._compare_service_metrics(
                baseline_metrics, current_metrics, service
            )
            comparison_results[service] = service_comparison
        
        return comparison_results
    
    def _compare_service_metrics(self, baseline: Dict, current: Dict, service: str) -> Dict:
        """比较单个服务的性能指标"""
        regressions = []
        improvements = []
        stable = []
        
        for test_name in current.keys():
            if test_name not in baseline:
                continue
            
            baseline_mean = baseline[test_name]["mean"]
            current_mean = current[test_name]["mean"]
            
            # 计算性能变化百分比
            change_percent = (current_mean - baseline_mean) / baseline_mean
            
            if change_percent > self.threshold_degradation:
                regressions.append({
                    "test": test_name,
                    "baseline_mean": baseline_mean,
                    "current_mean": current_mean,
                    "degradation_percent": change_percent * 100
                })
            elif change_percent < -0.05:  # 5%以上的改进
                improvements.append({
                    "test": test_name,
                    "baseline_mean": baseline_mean,
                    "current_mean": current_mean,
                    "improvement_percent": abs(change_percent) * 100
                })
            else:
                stable.append({
                    "test": test_name,
                    "baseline_mean": baseline_mean,
                    "current_mean": current_mean,
                    "change_percent": change_percent * 100
                })
        
        # 确定整体状态
        if regressions:
            status = "regression"
        elif improvements:
            status = "improvement"
        else:
            status = "stable"
        
        return {
            "status": status,
            "regressions": regressions,
            "improvements": improvements,
            "stable": stable,
            "total_tests": len(current)
        }
    
    def _save_baseline_data(self, service: str, metrics: Dict):
        """保存基线数据"""
        self.baseline_dir.mkdir(exist_ok=True)
        baseline_file = self.baseline_dir / f"{service}_baseline.json"
        
        baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
    
    def generate_performance_report(self, comparison_results: Dict[str, Dict]) -> str:
        """生成性能报告"""
        report_lines = [
            "# 🚀 性能回归检测报告",
            "",
            f"**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 总体概况",
            ""
        ]
        
        # 总体状态统计
        total_services = len(comparison_results)
        regression_services = sum(1 for r in comparison_results.values() if r["status"] == "regression")
        improvement_services = sum(1 for r in comparison_results.values() if r["status"] == "improvement")
        stable_services = sum(1 for r in comparison_results.values() if r["status"] == "stable")
        
        report_lines.extend([
            f"- 📈 **总服务数**: {total_services}",
            f"- 🔴 **性能回归**: {regression_services}",
            f"- 🟢 **性能改进**: {improvement_services}",
            f"- 🟡 **性能稳定**: {stable_services}",
            ""
        ])
        
        # 详细服务报告
        for service, results in comparison_results.items():
            report_lines.extend([
                f"## 🔧 {service.title()} 性能分析",
                ""
            ])
            
            if results["status"] == "no_baseline":
                report_lines.extend([
                    "ℹ️ **状态**: 新基线建立",
                    "📝 **说明**: 没有历史基线数据，当前结果已保存为新基线",
                    ""
                ])
                continue
            
            # 性能回归
            if results["regressions"]:
                report_lines.extend([
                    "### 🔴 性能回归",
                    ""
                ])
                for reg in results["regressions"]:
                    report_lines.extend([
                        f"- **{reg['test']}**",
                        f"  - 基线: {reg['baseline_mean']:.4f}s",
                        f"  - 当前: {reg['current_mean']:.4f}s", 
                        f"  - 🔻 下降: {reg['degradation_percent']:.1f}%",
                        ""
                    ])
            
            # 性能改进
            if results["improvements"]:
                report_lines.extend([
                    "### 🟢 性能改进",
                    ""
                ])
                for imp in results["improvements"]:
                    report_lines.extend([
                        f"- **{imp['test']}**",
                        f"  - 基线: {imp['baseline_mean']:.4f}s",
                        f"  - 当前: {imp['current_mean']:.4f}s",
                        f"  - 🔺 改进: {imp['improvement_percent']:.1f}%",
                        ""
                    ])
            
            # 稳定性能
            if results["stable"]:
                report_lines.extend([
                    "### 🟡 稳定性能",
                    ""
                ])
                for stable in results["stable"][:3]:  # 只显示前3个
                    report_lines.extend([
                        f"- **{stable['test']}**: {stable['current_mean']:.4f}s (变化: {stable['change_percent']:+.1f}%)",
                        ""
                    ])
                
                if len(results["stable"]) > 3:
                    report_lines.append(f"- ... 还有 {len(results['stable']) - 3} 个稳定测试")
                    report_lines.append("")
        
        # 建议和行动项
        report_lines.extend([
            "## 💡 建议和行动项",
            ""
        ])
        
        if regression_services > 0:
            report_lines.extend([
                "⚠️ **发现性能回归，建议采取以下行动**:",
                "1. 检查最近的代码变更",
                "2. 分析性能瓶颈点",
                "3. 考虑优化算法或数据结构",
                "4. 增加性能监控和告警",
                ""
            ])
        else:
            report_lines.extend([
                "✅ **性能表现良好**:",
                "1. 继续保持当前的开发实践",
                "2. 定期更新性能基线",
                "3. 考虑进一步的性能优化机会",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def run_regression_check(self) -> bool:
        """运行完整的性能回归检测"""
        print("🚀 开始性能回归检测...")
        
        # 1. 运行当前性能测试
        current_results = self.run_current_performance_tests()
        
        if not current_results:
            print("❌ 没有获取到性能测试结果")
            return False
        
        # 2. 与基线比较
        comparison_results = self.compare_performance(current_results)
        
        # 3. 生成报告
        report = self.generate_performance_report(comparison_results)
        
        # 4. 保存报告
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 性能报告已生成: {self.report_file}")
        
        # 5. 检查是否有性能回归
        has_regression = any(
            r["status"] == "regression" 
            for r in comparison_results.values()
        )
        
        if has_regression:
            print("⚠️ 检测到性能回归!")
            return False
        else:
            print("✅ 性能检测通过!")
            return True


def main():
    """主函数"""
    checker = PerformanceRegressionChecker()
    
    # 运行性能回归检测
    success = checker.run_regression_check()
    
    # 根据结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 