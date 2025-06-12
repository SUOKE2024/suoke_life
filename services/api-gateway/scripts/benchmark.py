"""
benchmark - 索克生活项目模块
"""

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
API 网关性能测试脚本

测试 API 网关的性能和负载能力，包括并发测试、压力测试、延迟测试等。
"""



@dataclass
class TestResult:
    """测试结果"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    errors: Dict[str, int]
    status_codes: Dict[int, int]

@dataclass
class TestConfig:
    """测试配置"""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = None
    data: Optional[str] = None
    concurrent_users: int = 10
    total_requests: int = 1000
    duration: Optional[int] = None  # 测试持续时间（秒）
    timeout: float = 30.0
    ramp_up_time: int = 0  # 渐进加压时间（秒）

class PerformanceTester:
    """性能测试器"""

    def __init__(self, config: TestConfig):
"""TODO: 添加文档字符串"""
self.config = config
self.console = Console()
self.results: List[Dict[str, Any]] = []
self.start_time: Optional[float] = None
self.end_time: Optional[float] = None

    async def make_request(self, session: aiohttp.ClientSession, request_id: int) -> Dict[str, Any]:
"""发送单个请求"""
start_time = time.time()

try:
            headers = self.config.headers or {}

            if self.config.method.upper()=="GET":
                async with session.get(
                    self.config.url,
                    headers = headers,
                    timeout = aiohttp.ClientTimeout(total = self.config.timeout)
                ) as response:
                    await response.text()  # 读取响应内容
                    end_time = time.time()

                    return {
                        "request_id": request_id,
                        "status_code": response.status,
                        "response_time": end_time - start_time,
                        "success": 200 <=response.status < 400,
                        "error": None,
                        "timestamp": start_time,
                    }

            elif self.config.method.upper()=="POST":
                data = self.config.data
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass

                async with session.post(
                    self.config.url,
                    headers = headers,
                    json = data if isinstance(data, dict) else None,
                    data = data if isinstance(data, str) else None,
                    timeout = aiohttp.ClientTimeout(total = self.config.timeout)
                ) as response:
                    await response.text()
                    end_time = time.time()

                    return {
                        "request_id": request_id,
                        "status_code": response.status,
                        "response_time": end_time - start_time,
                        "success": 200 <=response.status < 400,
                        "error": None,
                        "timestamp": start_time,
                    }

            else:
                raise ValueError(f"Unsupported HTTP method: {self.config.method}")

except Exception as e:
            end_time = time.time()
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e),
                "timestamp": start_time,
            }

    async def run_concurrent_test(self) -> TestResult:
"""运行并发测试"""
self.console.print(f"🚀 开始性能测试...")
self.console.print(f"目标URL: {self.config.url}")
self.console.print(f"并发用户: {self.config.concurrent_users}")
self.console.print(f"总请求数: {self.config.total_requests}")

connector = aiohttp.TCPConnector(
            limit = self.config.concurrent_users * 2,
            limit_per_host = self.config.concurrent_users * 2,
)

async with aiohttp.ClientSession(connector = connector) as session:
            self.start_time = time.time()

            # 创建信号量来控制并发数
            semaphore = asyncio.Semaphore(self.config.concurrent_users)

            async def bounded_request(request_id: int) -> Dict[str, Any]:
                async with semaphore:
                    # 渐进加压
                    if self.config.ramp_up_time > 0:
                        delay = (request_id / self.config.total_requests) * self.config.ramp_up_time
                        await asyncio.sleep(delay)

                    return await self.make_request(session, request_id)

            # 创建进度条
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed} / {task.total})"),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("发送请求", total = self.config.total_requests)

                # 创建所有任务
                tasks = []
                for i in range(self.config.total_requests):
                    task_coro = bounded_request(i)
                    tasks.append(task_coro)

                # 批量执行任务
                batch_size = 100
                for i in range(0, len(tasks), batch_size):
                    batch = tasks[i:i + batch_size]
                    batch_results = await asyncio.gather( * batch, return_exceptions = True)

                    for result in batch_results:
                        if isinstance(result, Exception):
                            self.results.append({
                                "request_id": - 1,
                                "status_code": 0,
                                "response_time": 0,
                                "success": False,
                                "error": str(result),
                                "timestamp": time.time(),
                            })
                        else:
                            self.results.append(result)

                        progress.advance(task)

            self.end_time = time.time()

return self.analyze_results()

    async def run_duration_test(self) -> TestResult:
"""运行持续时间测试"""
self.console.print(f"🚀 开始持续时间测试...")
self.console.print(f"目标URL: {self.config.url}")
self.console.print(f"并发用户: {self.config.concurrent_users}")
self.console.print(f"测试时长: {self.config.duration}秒")

connector = aiohttp.TCPConnector(
            limit = self.config.concurrent_users * 2,
            limit_per_host = self.config.concurrent_users * 2,
)

async with aiohttp.ClientSession(connector = connector) as session:
            self.start_time = time.time()
            end_time = self.start_time + self.config.duration

            # 创建信号量来控制并发数
            semaphore = asyncio.Semaphore(self.config.concurrent_users)
            request_counter = 0

            async def worker() -> None:
                nonlocal request_counter
                while time.time() < end_time:
                    async with semaphore:
                        request_id = request_counter
                        request_counter+=1
                        result = await self.make_request(session, request_id)
                        self.results.append(result)

            # 创建工作协程
            workers = [worker() for _ in range(self.config.concurrent_users)]

            # 运行测试
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("运行测试", total = self.config.duration)

                start = time.time()
                await asyncio.gather( * workers)

                while time.time() - start < self.config.duration:
                    elapsed = time.time() - start
                    progress.update(task, completed = elapsed)
                    await asyncio.sleep(0.1)

            self.end_time = time.time()

return self.analyze_results()

    def analyze_results(self) -> TestResult:
"""分析测试结果"""
if not self.results:
            raise ValueError("No test results to analyze")

# 基本统计
total_requests = len(self.results)
successful_requests = sum(1 for r in self.results if r["success"])
failed_requests = total_requests - successful_requests
total_time = self.end_time - self.start_time

# 响应时间统计
response_times = [r["response_time"] for r in self.results if r["success"]]

if response_times:
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)

            # 计算百分位数
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
else:
            min_response_time = max_response_time = avg_response_time = 0
            median_response_time = p95_response_time = p99_response_time = 0

# 请求速率
requests_per_second = total_requests / total_time if total_time > 0 else 0

# 错误统计
errors = {}
for result in self.results:
            if result["error"]:
                error_type = type(result["error"]).__name__ if isinstance(result["error"], Exception) else "Error"
                errors[error_type] = errors.get(error_type, 0) + 1

# 状态码统计
status_codes = {}
for result in self.results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

return TestResult(
            total_requests = total_requests,
            successful_requests = successful_requests,
            failed_requests = failed_requests,
            total_time = total_time,
            min_response_time = min_response_time,
            max_response_time = max_response_time,
            avg_response_time = avg_response_time,
            median_response_time = median_response_time,
            p95_response_time = p95_response_time,
            p99_response_time = p99_response_time,
            requests_per_second = requests_per_second,
            errors = errors,
            status_codes = status_codes,
)

    def print_results(self, result: TestResult) -> None:
"""打印测试结果"""
self.console.print("\n" + " = " * 60)
self.console.print("📊 性能测试结果", style = "bold blue")
self.console.print(" = " * 60)

# 基本统计表
basic_table = Table(title = "基本统计")
basic_table.add_column("指标", style = "cyan")
basic_table.add_column("值", style = "green")

basic_table.add_row("总请求数", f"{result.total_requests:,}")
basic_table.add_row("成功请求", f"{result.successful_requests:,}")
basic_table.add_row("失败请求", f"{result.failed_requests:,}")
basic_table.add_row("成功率", f"{(result.successful_requests / result.total_requests) * 100:.2f}%")
basic_table.add_row("总耗时", f"{result.total_time:.2f}秒")
basic_table.add_row("请求速率", f"{result.requests_per_second:.2f} req / s")

self.console.print(basic_table)

# 响应时间表
if result.successful_requests > 0:
            response_table = Table(title = "响应时间统计")
            response_table.add_column("指标", style = "cyan")
            response_table.add_column("时间 (秒)", style = "green")

            response_table.add_row("最小响应时间", f"{result.min_response_time:.4f}")
            response_table.add_row("最大响应时间", f"{result.max_response_time:.4f}")
            response_table.add_row("平均响应时间", f"{result.avg_response_time:.4f}")
            response_table.add_row("中位数响应时间", f"{result.median_response_time:.4f}")
            response_table.add_row("95% 响应时间", f"{result.p95_response_time:.4f}")
            response_table.add_row("99% 响应时间", f"{result.p99_response_time:.4f}")

            self.console.print(response_table)

# 状态码统计
if result.status_codes:
            status_table = Table(title = "HTTP 状态码统计")
            status_table.add_column("状态码", style = "cyan")
            status_table.add_column("次数", style = "green")
            status_table.add_column("百分比", style = "yellow")

            for code, count in sorted(result.status_codes.items()):
                percentage = (count / result.total_requests) * 100
                status_table.add_row(str(code), f"{count:,}", f"{percentage:.2f}%")

            self.console.print(status_table)

# 错误统计
if result.errors:
            error_table = Table(title = "错误统计")
            error_table.add_column("错误类型", style = "cyan")
            error_table.add_column("次数", style = "red")

            for error_type, count in result.errors.items():
                error_table.add_row(error_type, f"{count:,}")

            self.console.print(error_table)

    def export_results(self, result: TestResult, output_file: str) -> None:
"""导出测试结果"""
export_data = {
            "test_config": asdict(self.config),
            "test_result": asdict(result),
            "test_time": datetime.now().isoformat(),
            "raw_results": self.results,
}

with open(output_file, 'w', encoding = 'utf - 8') as f:
            json.dump(export_data, f, indent = 2, ensure_ascii = False)

self.console.print(f"📄 测试结果已导出到: {output_file}")

async def run_benchmark_suite(base_url: str) -> None:
    """运行基准测试套件"""
    console = Console()

    console.print("🧪 运行 API 网关基准测试套件", style = "bold blue")

    test_cases = [
{
            "name": "健康检查端点",
            "config": TestConfig(
                url = f"{base_url} / health",
                concurrent_users = 50,
                total_requests = 1000,
            )
},
{
            "name": "指标端点",
            "config": TestConfig(
                url = f"{base_url} / metrics / stats",
                concurrent_users = 20,
                total_requests = 500,
            )
},
{
            "name": "高并发测试",
            "config": TestConfig(
                url = f"{base_url} / health",
                concurrent_users = 100,
                total_requests = 2000,
            )
},
{
            "name": "持续负载测试",
            "config": TestConfig(
                url = f"{base_url} / health",
                concurrent_users = 30,
                duration = 60,  # 60秒
            )
},
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
console.print(f"\n📋 测试 {i} / {len(test_cases)}: {test_case['name']}")

tester = PerformanceTester(test_case["config"])

if test_case["config"].duration:
            result = await tester.run_duration_test()
else:
            result = await tester.run_concurrent_test()

tester.print_results(result)
results.append({
            "name": test_case["name"],
            "result": result,
})

    # 打印汇总
    console.print("\n" + " = " * 60)
    console.print("📈 测试套件汇总", style = "bold green")
    console.print(" = " * 60)

    summary_table = Table()
    summary_table.add_column("测试名称", style = "cyan")
    summary_table.add_column("请求数", style = "green")
    summary_table.add_column("成功率", style = "green")
    summary_table.add_column("平均响应时间", style = "yellow")
    summary_table.add_column("RPS", style = "magenta")

    for test_result in results:
result = test_result["result"]
success_rate = (result.successful_requests / result.total_requests) * 100

summary_table.add_row(
            test_result["name"],
            f"{result.total_requests:,}",
            f"{success_rate:.1f}%",
            f"{result.avg_response_time:.3f}s",
            f"{result.requests_per_second:.1f}",
)

    console.print(summary_table)

async def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description = "API 网关性能测试工具")
    parser.add_argument(
" - -url",
default = "http: / /localhost:8000 / health",
help = "测试URL (默认: http: / /localhost:8000 / health)"
    )
    parser.add_argument(
" - -method",
default = "GET",
choices = ["GET", "POST"],
help = "HTTP 方法 (默认: GET)"
    )
    parser.add_argument(
" - -concurrent",
type = int,
default = 10,
help = "并发用户数 (默认: 10)"
    )
    parser.add_argument(
" - -requests",
type = int,
default = 1000,
help = "总请求数 (默认: 1000)"
    )
    parser.add_argument(
" - -duration",
type = int,
help = "测试持续时间（秒），如果指定则忽略 - -requests"
    )
    parser.add_argument(
" - -timeout",
type = float,
default = 30.0,
help = "请求超时时间（秒）(默认: 30.0)"
    )
    parser.add_argument(
" - -ramp - up",
type = int,
default = 0,
help = "渐进加压时间（秒）(默认: 0)"
    )
    parser.add_argument(
" - -data",
help = "POST 请求数据（JSON 字符串）"
    )
    parser.add_argument(
" - -headers",
help = "请求头（JSON 字符串）"
    )
    parser.add_argument(
" - -export",
help = "导出结果到文件"
    )
    parser.add_argument(
" - -suite",
action = "store_true",
help = "运行基准测试套件"
    )

    args = parser.parse_args()

    if args.suite:
base_url = args.url.rstrip(' / health').rstrip(' / ')
await run_benchmark_suite(base_url)
return

    # 解析请求头
    headers = {}
    if args.headers:
try:
            headers = json.loads(args.headers)
except json.JSONDecodeError:
            print("❌ 无效的请求头 JSON 格式")
            return

    # 创建测试配置
    config = TestConfig(
url = args.url,
method = args.method,
headers = headers,
data = args.data,
concurrent_users = args.concurrent,
total_requests = args.requests,
duration = args.duration,
timeout = args.timeout,
ramp_up_time = args.ramp_up,
    )

    # 运行测试
    tester = PerformanceTester(config)

    if args.duration:
result = await tester.run_duration_test()
    else:
result = await tester.run_concurrent_test()

    tester.print_results(result)

    if args.export:
tester.export_results(result, args.export)

if __name__=="__main__":
    asyncio.run(main())