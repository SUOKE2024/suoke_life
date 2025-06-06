"""
test_end_to_end - 索克生活项目模块
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import aiohttp
import asyncio
import json
import logging
import sys
import time
import uuid
import websockets

#!/usr/bin/env python3
"""
小艾智能体端到端测试套件
验证从用户请求到响应的完整功能流程
"""



# 添加项目路径
sys.path.insert(0, Path().resolve())

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 使用loguru logger

@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    steps: list[str]
    expected_results: list[str]
    timeout: float = 30.0
    critical: bool = True

@dataclass
class TestResult:
    """测试结果"""
    scenario_name: str
    success: bool
    duration: float
    steps_completed: int
    total_steps: int
    error_message: str | None = None
    details: dict[str, Any] | None = None

class EndToEndTestSuite:
    """端到端测试套件"""

    def __init__(self, base_url: str= "http://localhost:8000", ws_url: str= "ws://localhost:8001"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.session = None
        self.test_user_id = f"e2e_test_user_{uuid.uuid4().hex[:8]}"
        self.test_session_id = f"e2e_session_{uuid.uuid4().hex[:8]}"

        # 测试场景定义
        self.scenarios = [
            TestScenario(
                name="健康咨询完整流程",
                description="用户通过聊天进行健康咨询的完整流程",
                steps=[
                    "建立WebSocket连接",
                    "发送健康咨询消息",
                    "接收智能体回复",
                    "请求设备状态检查",
                    "获取健康建议",
                    "结束会话"
                ],
                expected_results=[
                    "连接成功建立",
                    "消息发送成功",
                    "收到智能回复",
                    "设备状态正常",
                    "获得个性化建议",
                    "会话正常结束"
                ]
            ),
            TestScenario(
                name="多模态设备访问流程",
                description="访问摄像头、麦克风等设备的完整流程",
                steps=[
                    "检查设备可用性",
                    "请求摄像头权限",
                    "拍摄照片",
                    "图像分析处理",
                    "获取分析结果",
                    "清理资源"
                ],
                expected_results=[
                    "设备检测成功",
                    "权限获取成功",
                    "照片拍摄成功",
                    "图像处理完成",
                    "分析结果准确",
                    "资源清理完成"
                ]
            ),
            TestScenario(
                name="网络优化功能验证",
                description="验证WebSocket、HTTP/2、压缩等网络优化功能",
                steps=[
                    "启用数据压缩",
                    "建立HTTP/2连接",
                    "测试WebSocket双向通信",
                    "验证压缩效果",
                    "检查连接性能",
                    "获取优化报告"
                ],
                expected_results=[
                    "压缩功能启用",
                    "HTTP/2连接建立",
                    "双向通信正常",
                    "压缩率达标",
                    "性能提升明显",
                    "报告数据完整"
                ]
            ),
            TestScenario(
                name="并发用户处理能力",
                description="测试系统处理多个并发用户的能力",
                steps=[
                    "创建多个用户会话",
                    "并发发送请求",
                    "验证响应正确性",
                    "检查资源使用",
                    "测试负载均衡",
                    "清理所有会话"
                ],
                expected_results=[
                    "会话创建成功",
                    "并发处理正常",
                    "响应准确无误",
                    "资源使用合理",
                    "负载分布均匀",
                    "清理完全"
                ]
            ),
            TestScenario(
                name="错误处理和恢复",
                description="测试系统的错误处理和恢复能力",
                steps=[
                    "模拟网络中断",
                    "发送无效请求",
                    "测试超时处理",
                    "验证错误响应",
                    "检查自动恢复",
                    "确认系统稳定"
                ],
                expected_results=[
                    "网络中断检测",
                    "无效请求拒绝",
                    "超时正确处理",
                    "错误信息清晰",
                    "自动恢复成功",
                    "系统保持稳定"
                ]
            ),
            TestScenario(
                name="性能基准测试",
                description="测试系统的性能基准指标",
                steps=[
                    "测量响应时间",
                    "检查吞吐量",
                    "监控资源使用",
                    "验证缓存效果",
                    "测试扩展性",
                    "生成性能报告"
                ],
                expected_results=[
                    "响应时间<1秒",
                    "吞吐量>100 RPS",
                    "CPU使用<80%",
                    "缓存命中率>70%",
                    "扩展性良好",
                    "报告详细准确"
                ]
            )
        ]

    async def setup(self):
        """设置测试环境"""
        logger.info("设置端到端测试环境")

        self.session = aiohttp.ClientSession()

        # 等待服务启动
        for _ in range(60):  # 增加等待时间
            try:
                async with self.session.get(f"{self.base_url}/api/v1/health/") as resp:
                    if resp.status == 200:
                        logger.info("HTTP服务已启动")
                        break
            except Exception as e:
                raise Exception() from e

        # 验证WebSocket服务
        try:
            uri = f"{self.ws_url}/api/v1/network/ws/test_connection"
            async with websockets.connect(uri) as websocket:
                await websocket.recv()  # 接收连接确认
                logger.info("WebSocket服务已启动")
        except Exception as e:
            raise Exception() from e

    async def _run_device_integration_scenario(self, scenario: TestScenario) -> TestResult:
        """运行设备集成测试场景"""
        start_time = time.time()
        steps_completed = 0

        try:
            # 步骤1: 检查设备可用性
            device_url = f"{self.base_url}/api/v1/devices/status"
            async with self.session.get(device_url) as resp:
                if resp.status != 200:
                    raise Exception("设备状态检查失败")

                device_status = await resp.json()
                if not device_status.get("success"):
                    raise Exception("设备不可用")

                steps_completed += 1
                logger.info("✓ 步骤1完成: 设备可用性检查")

            # 步骤2-3: 请求摄像头权限并拍摄照片
            capture_url = f"{self.base_url}/api/v1/devices/camera/capture"
            capture_data = {
                "user_id": self.test_user_id,
                "quality": "medium",
                "format": "jpeg"
            }

            async with self.session.post(capture_url, json=capture_data) as resp:
                if resp.status != 200:
                    raise Exception("摄像头访问失败")

                capture_result = await resp.json()
                if not capture_result.get("success"):
                    raise Exception("照片拍摄失败")

                steps_completed += 2
                logger.info("✓ 步骤2-3完成: 摄像头权限获取和照片拍摄")

            if capture_result.get("data", {}).get("image_data"):
                analysis_url = f"{self.base_url}/api/v1/devices/multimodal/analyze"
                analysis_data = {
                    "user_id": self.test_user_id,
                    "data_type": "image",
                    "image_data": capture_result["data"]["image_data"]
                }

                async with self.session.post(analysis_url, json=analysis_data) as resp:
                    if resp.status == 200:
                        analysis_result = await resp.json()
                        if analysis_result.get("success"):
                            steps_completed += 2
                            logger.info("✓ 步骤4-5完成: 图像分析处理")
                        else:
                            raise Exception("图像分析失败")
                    else:
                        raise Exception("图像分析请求失败")
            else:
                raise Exception("没有图像数据可供分析")

            # 步骤6: 清理资源
            cleanup_url = f"{self.base_url}/api/v1/devices/cleanup"
            cleanup_data = {"user_id": self.test_user_id}

            async with self.session.post(cleanup_url, json=cleanup_data) as resp:
                steps_completed += 1
                logger.info("✓ 步骤6完成: 资源清理")

            duration = time.time() - start_time
            return TestResult(
                scenario_name=scenario.name,
                success=True,
                duration=duration,
                steps_completed=steps_completed,
                total_steps=len(scenario.steps),
                details={
                    "image_captured": True,
                    "analysis_completed": True,
                    "cleanup_done": True
                }
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                scenario_name=scenario.name,
                success=False,
                duration=duration,
                steps_completed=steps_completed,
                total_steps=len(scenario.steps),
                error_message=str(e),
                details={"connection_id": connection_id if 'connection_id' in locals() else None}
            )

    async def run_all_scenarios(self) -> list[TestResult]:
        """运行所有测试场景"""
        logger.info("开始端到端测试套件")

        await self.setup()

        try:
            scenario_functions = [
                self.run_scenario_health_consultation,
                self.run_scenario_device_access,
                self.run_scenario_network_optimization,
                self.run_scenario_concurrent_users,
                self.run_scenario_error_handling,
                self.run_scenario_performance_benchmark
            ]

            results = []

            for i, _ in enumerate(scenario_functions):
                logger.info(f"执行测试场景 {i+1}/{len(scenario_functions)}: {self.scenarios[i].name}")

                try:
                    result = await asyncio.wait_for(
                        scenario_func(),
                        timeout=self.scenarios[i].timeout
                    )
                    results.append(result)

                    if result.success:
                        logger.info(f"✅ 场景 '{result.scenario_name}' 成功完成")
                    else:
                        logger.error(f"❌ 场景 '{result.scenario_name}' 失败: {result.error_message}")

                        # 如果是关键测试失败,可以选择继续或停止
                        if self.scenarios[i].critical:
                            logger.warning("关键测试失败,但继续执行其他测试")

                except TimeoutError:
                    logger.error(f"⏰ 场景 '{self.scenarios[i].name}' 超时")
                    results.append(TestResult(
                        scenario_name=self.scenarios[i].name,
                        success=False,
                        duration=self.scenarios[i].timeout,
                        steps_completed=0,
                        total_steps=len(self.scenarios[i].steps),
                        error_message="测试超时"
                    ))
                except Exception as e:
                    logger.error(f"💥 场景 '{self.scenarios[i].name}' 异常: {e}")
                    results.append(TestResult(
                        scenario_name=self.scenarios[i].name,
                        success=False,
                        duration=0,
                        steps_completed=0,
                        total_steps=len(self.scenarios[i].steps),
                        error_message=str(e)
                    ))

                # 场景间短暂休息
                await asyncio.sleep(1)

            return results

        finally:
            await self.cleanup()

    def generate_report(self, results: list[TestResult]) -> dict[str, Any]:
        """生成测试报告"""
        total_scenarios = len(results)
        successful_scenarios = sum(1 for r in results if r.success)
        total_steps = sum(r.total_steps for r in results)
        completed_steps = sum(r.steps_completed for r in results)
        total_duration = sum(r.duration for r in results)

        success_rate = successful_scenarios / total_scenarios * 100 if total_scenarios > 0 else 0
        step_completion_rate = completed_steps / total_steps * 100 if total_steps > 0 else 0

        # 分析失败原因
        failed_scenarios = [r for r in results if not r.success]
        failure_reasons = [r.error_message for r in failed_scenarios if r.error_message]

        # 性能指标
        avg_scenario_duration = total_duration / total_scenarios if total_scenarios > 0 else 0

        if success_rate >= 90 and step_completion_rate >= 95:
            grade = "优秀"
            grade_emoji = "🏆"
        elif success_rate >= 80 and step_completion_rate >= 85:
            grade = "良好"
            grade_emoji = "🥈"
        elif success_rate >= 70 and step_completion_rate >= 75:
            grade = "一般"
            grade_emoji = "🥉"
        elif success_rate >= 50:
            grade = "需要改进"
            grade_emoji = "⚠️"
        else:
            grade = "较差"
            grade_emoji = "❌"

        return {
            "test_summary": {
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "failed_scenarios": len(failed_scenarios),
                "success_rate": success_rate,
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "step_completion_rate": step_completion_rate,
                "total_duration": total_duration,
                "avg_scenario_duration": avg_scenario_duration
            },
            "grade": {
                "score": success_rate,
                "level": grade,
                "emoji": grade_emoji
            },
            "scenario_results": [
                {
                    "name": r.scenario_name,
                    "success": r.success,
                    "duration": r.duration,
                    "steps_completed": r.steps_completed,
                    "total_steps": r.total_steps,
                    "completion_rate": r.steps_completed / r.total_steps * 100 if r.total_steps > 0 else 0,
                    "error_message": r.error_message,
                    "details": r.details
                }
                for r in results
            ],
            "failure_analysis": {
                "failed_scenarios": [r.scenario_name for r in failed_scenarios],
                "failure_reasons": failure_reasons,
                "common_issues": self._analyze_common_issues(failure_reasons)
            },
            "recommendations": self._generate_recommendations(results)
        }

    def _analyze_common_issues(self, failure_reasons: list[str]) -> list[str]:
        """分析常见问题"""
        common_issues = []

        # 分析失败原因中的关键词
        reason_text = " ".join(failure_reasons).lower()

        if "timeout" in reason_text or "超时" in reason_text:
            common_issues.append("网络或服务响应超时")

        if "connection" in reason_text or "连接" in reason_text:
            common_issues.append("连接建立或维护问题")

        if "permission" in reason_text or "权限" in reason_text:
            common_issues.append("权限或认证问题")

        if "device" in reason_text or "设备" in reason_text:
            common_issues.append("设备访问或硬件问题")

        if "memory" in reason_text or "内存" in reason_text:
            common_issues.append("内存或资源不足")

        return common_issues

    def _generate_recommendations(self, results: list[TestResult]) -> list[str]:
        """生成改进建议"""
        recommendations = []

        failed_results = [r for r in results if not r.success]

        for result in failed_results:
            if "健康咨询" in result.scenario_name:
                recommendations.append("优化聊天响应速度和准确性")
            elif "设备访问" in result.scenario_name:
                recommendations.append("改进设备权限管理和错误处理")
            elif "网络优化" in result.scenario_name:
                recommendations.append("检查网络优化配置和实现")
            elif "并发用户" in result.scenario_name:
                recommendations.append("提升并发处理能力和资源管理")
            elif "错误处理" in result.scenario_name:
                recommendations.append("完善错误处理和恢复机制")
            elif "性能基准" in result.scenario_name:
                recommendations.append("优化系统性能和响应时间")

        # 通用建议
        success_rate = sum(1 for r in results if r.success) / len(results) * 100

        if success_rate < 80:
            recommendations.append("进行全面的系统稳定性检查")

        if any(r.duration > 20 for r in results):
            recommendations.append("优化测试执行时间和系统响应")

        return list(set(recommendations))  # 去重

async def main():
    """主函数"""
    print("=" * 80)
    print("小艾智能体端到端测试套件")
    print("=" * 80)

    test_suite = EndToEndTestSuite()

    try:
        # 运行所有测试场景
        results = await test_suite.run_all_scenarios()

        report = test_suite.generate_report(results)

        # 输出测试结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        summary = report["test_summary"]
        print(f"总测试场景: {summary['total_scenarios']}")
        print(f"成功场景: {summary['successful_scenarios']}")
        print(f"失败场景: {summary['failed_scenarios']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"步骤完成率: {summary['step_completion_rate']:.1f}%")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        print(f"平均场景耗时: {summary['avg_scenario_duration']:.2f}秒")

        # 输出评级
        grade = report["grade"]
        print(f"\n系统评级: {grade['emoji']} {grade['level']} ({grade['score']:.1f}分)")

        # 输出详细结果
        print("\n" + "-" * 60)
        print("详细测试结果")
        print("-" * 60)

        for scenario in report["scenario_results"]:
            status = "✅" if scenario["success"] else "❌"
            print(f"\n{status} {scenario['name']}")
            print(f"   完成率: {scenario['completion_rate']:.1f}% ({scenario['steps_completed']}/{scenario['total_steps']})")
            print(f"   耗时: {scenario['duration']:.2f}秒")

            if not scenario["success"] and scenario["error_message"]:
                print(f"   错误: {scenario['error_message']}")

            if scenario["details"]:
                print(f"   详情: {scenario['details']}")

        # 输出失败分析
        if report["failure_analysis"]["failed_scenarios"]:
            print("\n" + "-" * 60)
            print("失败分析")
            print("-" * 60)

            print("失败场景:")
            for failed_scenario in report["failure_analysis"]["failed_scenarios"]:
                print(f"  • {failed_scenario}")

            if report["failure_analysis"]["common_issues"]:
                print("\n常见问题:")
                for issue in report["failure_analysis"]["common_issues"]:
                    print(f"  • {issue}")

        # 输出改进建议
        if report["recommendations"]:
            print("\n" + "-" * 60)
            print("改进建议")
            print("-" * 60)

            for i, _ in enumerate(report["recommendations"], 1):
                print(f"{i}. {recommendation}")

        # 保存详细报告
        report_filename = f"e2e_test_report_{int(time.time())}.json"
        with Path(report_filename).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存到: {report_filename}")

        # 输出总结
        print("\n" + "=" * 60)
        if summary["success_rate"] >= 80:
            print("🎉 端到端测试总体成功!系统功能基本正常。")
        elif summary["success_rate"] >= 60:
            print("⚠️ 端到端测试部分成功,系统需要一些改进。")
        else:
            print("❌ 端到端测试失败较多,系统需要重大改进。")

        print("\n请根据测试结果和建议进行相应的优化和修复。")

        return 0 if summary["success_rate"] >= 80 else 1

    except Exception as e:
        logger.error(f"端到端测试执行失败: {e}")
        print(f"\n💥 测试执行失败: {e}")
        print("\n请检查:")
        print("1. HTTP服务器是否正在运行 (python cmd/server/http_server.py)")
        print("2. WebSocket服务器是否正在运行")
        print("3. 所有依赖服务是否可用")
        print("4. 网络连接是否正常")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
