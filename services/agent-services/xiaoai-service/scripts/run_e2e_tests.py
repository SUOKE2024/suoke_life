#!/usr/bin/env python3
"""
小艾智能体端到端测试运行脚本
提供便捷的测试执行和管理功能
"""

import argparse
import asyncio
import json
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 使用loguru logger

class E2ETestRunner:
    """端到端测试运行器"""

    def __init__(self, config_file: str | None= None, environment: str= "development"):
        self.config_file = config_file or "config/e2e_test_config.yaml"
        self.environment = environment
        self.config = {}
        self.server_processes = []
        self.test_results = {}

    def load_config(self):
        """加载测试配置"""
        try:
            import yaml
            config_path = project_root / self.config_file

            if not config_path.exists():
                logger.warning(f"配置文件不存在: {config_path}")
                self.config = self._get_default_config()
                return

            with Path(config_path).open(encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # 应用环境特定配置
            if self.environment in self.config.get("environments", {}):
                env_config = self.config["environments"][self.environment]
                self._merge_config(self.config, env_config)

            logger.info(f"已加载配置文件: {config_path}")

        except ImportError:
            logger.warning("PyYAML未安装,使用默认配置")
            self.config = self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """获取默认配置"""
        return {
            "environment": {
                "http_server": {
                    "host": "localhost",
                    "port": 8000,
                    "base_url": "http://localhost:8000"
                },
                "websocket_server": {
                    "host": "localhost",
                    "port": 8001,
                    "base_url": "ws://localhost:8001"
                },
                "timeouts": {
                    "connection_timeout": 10,
                    "request_timeout": 30,
                    "scenario_timeout": 60,
                    "total_timeout": 300
                }
            },
            "scenarios": {
                "health_consultation": {"enabled": True, "timeout": 45},
                "device_access": {"enabled": True, "timeout": 60},
                "network_optimization": {"enabled": True, "timeout": 30},
                "concurrent_users": {"enabled": True, "timeout": 45},
                "error_handling": {"enabled": True, "timeout": 30},
                "performance_benchmark": {"enabled": True, "timeout": 60}
            }
        }

    def _merge_config(self, base_config: dict[str, Any], env_config: dict[str, Any]):
        """合并环境配置"""
        for key, value in env_config.items():
            if isinstance(value, dict) and key in base_config:
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value

    async def check_dependencies(self) -> bool:
        """检查依赖"""
        logger.info("检查测试依赖...")

        required_packages = [
            "aiohttp",
            "websockets",
            "asyncio"
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.error(f"缺少依赖包: {missing_packages}")
            logger.info("请运行: pip install aiohttp websockets")
            return False

        logger.info("✓ 依赖检查通过")
        return True

    async def start_services(self, auto_start: bool = True) -> bool:
        """启动服务"""
        if not auto_start:
            logger.info("跳过自动启动服务,请确保服务已手动启动")
            return True

        logger.info("启动测试服务...")

        try:
            # 启动HTTP服务器
            http_cmd = [
                sys.executable,
                str(project_root / "cmd/server/http_server.py"),
                "--host", self.config["environment"]["http_server"]["host"],
                "--port", str(self.config["environment"]["http_server"]["port"]),
                "--env", self.environment
            ]

            logger.info(f"启动HTTP服务器: {' '.join(http_cmd)}")
            http_process = subprocess.Popen(
                http_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root
            )
            self.server_processes.append(("http_server", http_process))

            # 等待服务启动
            await asyncio.sleep(5)

            # 检查服务状态
            if http_process.poll() is not None:
                stdout, stderr = http_process.communicate()
                logger.error("HTTP服务器启动失败:")
                logger.error(f"stdout: {stdout.decode()}")
                logger.error(f"stderr: {stderr.decode()}")
                return False

            logger.info("✓ 服务启动成功")
            return True

        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            return False

    async def stop_services(self):
        """停止服务"""
        logger.info("停止测试服务...")

        for service_name, process in self.server_processes:
            try:
                logger.info(f"停止 {service_name}...")
                process.terminate()

                # 等待进程结束
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"强制终止 {service_name}")
                    process.kill()
                    process.wait()

                logger.info(f"✓ {service_name} 已停止")

            except Exception as e:
                logger.error(f"停止 {service_name} 失败: {e}")

        self.server_processes.clear()

    async def wait_for_services(self) -> bool:
        """等待服务就绪"""
        logger.info("等待服务就绪...")

        import aiohttp

        http_url = self.config["environment"]["http_server"]["base_url"]
        timeout = self.config["environment"]["timeouts"]["connection_timeout"]

        for _ in range(30):  # 最多等待30秒
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{http_url}/api/v1/health/", timeout=timeout) as resp:
                        if resp.status == 200:
                            logger.info("✓ HTTP服务就绪")
                            return True
            except Exception as e:
                logger.debug(f"等待服务就绪 ({i+1}/30): {e}")
                await asyncio.sleep(1)

        logger.error("服务启动超时")
        return False

    async def run_tests(self, scenarios: list[str] | None = None) -> dict[str, Any]:
        """运行测试"""
        logger.info("开始执行端到端测试")

        # 导入测试模块
        from test_end_to_end import EndToEndTestSuite

        http_url = self.config["environment"]["http_server"]["base_url"]
        ws_url = self.config["environment"]["websocket_server"]["base_url"]

        test_suite = EndToEndTestSuite(base_url=http_url, ws_url=ws_url)

        # 过滤测试场景
        if scenarios:
            enabled_scenarios = []
            for i, _ in enumerate(test_suite.scenarios):
                if scenario.name in scenarios or str(i) in scenarios:
                    enabled_scenarios.append(scenario)
            test_suite.scenarios = enabled_scenarios
        else:
            # 根据配置过滤场景
            enabled_scenarios = []
            scenario_config = self.config.get("scenarios", {})

            for scenario in test_suite.scenarios:
                scenario_key = scenario.name.lower().replace(" ", "_").replace("完整流程", "").replace("功能验证", "").replace("处理能力", "").replace("和恢复", "").replace("测试", "").strip()

                # 简化场景名称匹配
                if "健康咨询" in scenario.name:
                    scenario_key = "health_consultation"
                elif "设备访问" in scenario.name:
                    scenario_key = "device_access"
                elif "网络优化" in scenario.name:
                    scenario_key = "network_optimization"
                elif "并发用户" in scenario.name:
                    scenario_key = "concurrent_users"
                elif "错误处理" in scenario.name:
                    scenario_key = "error_handling"
                elif "性能基准" in scenario.name:
                    scenario_key = "performance_benchmark"

                if scenario_config.get(scenario_key, {}).get("enabled", True):
                    timeout = scenario_config.get(scenario_key, {}).get("timeout")
                    if timeout:
                        scenario.timeout = timeout
                    enabled_scenarios.append(scenario)

            test_suite.scenarios = enabled_scenarios

        logger.info(f"将执行 {len(test_suite.scenarios)} 个测试场景")

        # 运行测试
        try:
            results = await test_suite.run_all_scenarios()
            report = test_suite.generate_report(results)

            self.test_results = report
            return report

        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {
                "test_summary": {
                    "total_scenarios": 0,
                    "successful_scenarios": 0,
                    "failed_scenarios": 0,
                    "success_rate": 0,
                    "error": str(e)
                }
            }

    def save_results(self, results: dict[str, Any], output_file: str | None= None):
        """保存测试结果"""
        if not output_file:
            timestamp = int(time.time())
            output_file = f"e2e_test_results_{timestamp}.json"

        output_path = project_root / output_file

        try:
            with Path(output_path).open('w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"测试结果已保存到: {output_path}")

        except Exception as e:
            logger.error(f"保存测试结果失败: {e}")

    def print_summary(self, results: dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "=" * 80)
        print("小艾智能体端到端测试结果摘要")
        print("=" * 80)

        summary = results.get("test_summary", {})
        grade = results.get("grade", {})

        print(f"测试环境: {self.environment}")
        print(f"总测试场景: {summary.get('total_scenarios', 0)}")
        print(f"成功场景: {summary.get('successful_scenarios', 0)}")
        print(f"失败场景: {summary.get('failed_scenarios', 0)}")
        print(f"成功率: {summary.get('success_rate', 0):.1f}%")
        print(f"总耗时: {summary.get('total_duration', 0):.2f}秒")

        # 评级
        print(f"\n系统评级: {grade.get('emoji', '❓')} {grade.get('level', '未知')} ({grade.get('score', 0):.1f}分)")

        # 场景结果
        print("\n" + "-" * 60)
        print("场景执行结果")
        print("-" * 60)

        for scenario in results.get("scenario_results", []):
            status = "✅" if scenario.get("success") else "❌"
            print(f"{status} {scenario.get('name', 'Unknown')}")
            print(f"   完成率: {scenario.get('completion_rate', 0):.1f}%")
            print(f"   耗时: {scenario.get('duration', 0):.2f}秒")

            if not scenario.get("success") and scenario.get("error_message"):
                print(f"   错误: {scenario.get('error_message')}")

        # 改进建议
        recommendations = results.get("recommendations", [])
        if recommendations:
            print("\n" + "-" * 60)
            print("改进建议")
            print("-" * 60)

            for i, _ in enumerate(recommendations, 1):
                print(f"{i}. {rec}")

        print("\n" + "=" * 80)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小艾智能体端到端测试运行器')

    parser.add_argument('--config', '-c',
                       help='测试配置文件路径',
                       default='config/e2e_test_config.yaml')

    parser.add_argument('--environment', '-e',
                       help='测试环境 (development, testing, staging, production)',
                       default='development',
                       choices=['development', 'testing', 'staging', 'production'])

    parser.add_argument('--scenarios', '-s',
                       help='要执行的测试场景 (用逗号分隔)',
                       default=None)

    parser.add_argument('--auto-start', '-a',
                       help='自动启动服务',
                       action='store_true',
                       default=False)

    parser.add_argument('--output', '-o',
                       help='结果输出文件',
                       default=None)

    parser.add_argument('--verbose', '-v',
                       help='详细输出',
                       action='store_true',
                       default=False)

    parser.add_argument('--no-cleanup',
                       help='测试后不清理服务',
                       action='store_true',
                       default=False)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = E2ETestRunner(
        config_file=args.config,
        environment=args.environment
    )

    # 加载配置
    runner.load_config()

    # 解析测试场景
    scenarios = None
    if args.scenarios:
        scenarios = [s.strip() for s in args.scenarios.split(',')]

    try:
        # 检查依赖
        if not await runner.check_dependencies():
            return 1

        # 启动服务
        if not await runner.start_services(auto_start=args.auto_start):
            return 1

        # 等待服务就绪
        if not await runner.wait_for_services():
            return 1

        # 运行测试
        results = await runner.run_tests(scenarios=scenarios)

        # 保存结果
        if args.output or results.get("test_summary", {}).get("total_scenarios", 0) > 0:
            runner.save_results(results, args.output)

        # 打印摘要
        runner.print_summary(results)

        # 返回退出码
        success_rate = results.get("test_summary", {}).get("success_rate", 0)
        return 0 if success_rate >= 80 else 1

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        return 1
    finally:
        # 清理服务
        if not args.no_cleanup:
            await runner.stop_services()

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info("收到中断信号,正在清理...")
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 运行主函数
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
