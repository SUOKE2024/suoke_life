#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试框架核心
提供统一的测试执行和管理功能
"""

from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import traceback
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestType(Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    E2E = "e2e"


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: TestStatus
    duration: float = 0.0
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    output: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == TestStatus.PASSED
    
    @property
    def is_failure(self) -> bool:
        """是否失败"""
        return self.status in [TestStatus.FAILED, TestStatus.ERROR]


@dataclass
class TestCase:
    """测试用例"""
    name: str
    func: Callable
    test_type: TestType = TestType.UNIT
    description: str = ""
    tags: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    skip: bool = False
    skip_reason: str = ""
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    async def run(self) -> TestResult:
        """运行测试用例"""
        result = TestResult(
            test_name=self.name,
            status=TestStatus.PENDING,
            start_time=datetime.now()
        )
        
        if self.skip:
            result.status = TestStatus.SKIPPED
            result.output = self.skip_reason
            result.end_time = datetime.now()
            return result
        
        try:
            result.status = TestStatus.RUNNING
            start_time = time.time()
            
            # 执行setup
            if self.setup:
                if asyncio.iscoroutinefunction(self.setup):
                    await self.setup()
                else:
                    self.setup()
            
            # 执行测试函数
            if asyncio.iscoroutinefunction(self.func):
                if self.timeout:
                    await asyncio.wait_for(self.func(), timeout=self.timeout)
                else:
                    await self.func()
            else:
                self.func()
            
            # 执行teardown
            if self.teardown:
                if asyncio.iscoroutinefunction(self.teardown):
                    await self.teardown()
                else:
                    self.teardown()
            
            result.status = TestStatus.PASSED
            result.duration = time.time() - start_time
            
        except asyncio.TimeoutError:
            result.status = TestStatus.ERROR
            result.error_message = f"测试超时（{self.timeout}秒）"
            result.duration = time.time() - start_time
            
        except AssertionError as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            result.error_traceback = traceback.format_exc()
            result.duration = time.time() - start_time
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.error_traceback = traceback.format_exc()
            result.duration = time.time() - start_time
        
        finally:
            result.end_time = datetime.now()
        
        return result


@dataclass
class TestSuite:
    """测试套件"""
    name: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    parallel: bool = False
    max_workers: int = 4
    
    def add_test(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def add_tests(self, test_cases: List[TestCase]):
        """批量添加测试用例"""
        self.test_cases.extend(test_cases)
    
    def filter_tests(
        self,
        test_type: Optional[TestType] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None
    ) -> List[TestCase]:
        """过滤测试用例"""
        filtered = self.test_cases
        
        if test_type:
            filtered = [t for t in filtered if t.test_type == test_type]
        
        if tags:
            filtered = [t for t in filtered if any(tag in t.tags for tag in tags)]
        
        if name_pattern:
            import re
            pattern = re.compile(name_pattern)
            filtered = [t for t in filtered if pattern.search(t.name)]
        
        return filtered
    
    async def run(
        self,
        test_type: Optional[TestType] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None
    ) -> List[TestResult]:
        """运行测试套件"""
        # 过滤测试用例
        tests_to_run = self.filter_tests(test_type, tags, name_pattern)
        
        if not tests_to_run:
            logger.warning(f"测试套件 {self.name} 中没有匹配的测试用例")
            return []
        
        results = []
        
        try:
            # 执行套件setup
            if self.setup:
                if asyncio.iscoroutinefunction(self.setup):
                    await self.setup()
                else:
                    self.setup()
            
            # 运行测试用例
            if self.parallel:
                # 并行执行
                semaphore = asyncio.Semaphore(self.max_workers)
                
                async def run_with_semaphore(test_case):
                    async with semaphore:
                        return await test_case.run()
                
                tasks = [run_with_semaphore(test) for test in tests_to_run]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理异常
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        results[i] = TestResult(
                            test_name=tests_to_run[i].name,
                            status=TestStatus.ERROR,
                            error_message=str(result),
                            error_traceback=traceback.format_exc()
                        )
            else:
                # 串行执行
                for test_case in tests_to_run:
                    result = await test_case.run()
                    results.append(result)
            
        finally:
            # 执行套件teardown
            if self.teardown:
                try:
                    if asyncio.iscoroutinefunction(self.teardown):
                        await self.teardown()
                    else:
                        self.teardown()
                except Exception as e:
                    logger.error(f"测试套件teardown失败: {e}")
        
        return results


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_suites: List[TestSuite] = []
        self.results: List[TestResult] = []
    
    def add_suite(self, suite: TestSuite):
        """添加测试套件"""
        self.test_suites.append(suite)
    
    def add_test(self, test_case: TestCase, suite_name: str = "default"):
        """添加单个测试用例"""
        # 查找或创建套件
        suite = None
        for s in self.test_suites:
            if s.name == suite_name:
                suite = s
                break
        
        if not suite:
            suite = TestSuite(name=suite_name)
            self.test_suites.append(suite)
        
        suite.add_test(test_case)
    
    async def run_all(
        self,
        test_type: Optional[TestType] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None,
        parallel_suites: bool = False
    ) -> Dict[str, List[TestResult]]:
        """运行所有测试"""
        all_results = {}
        
        if parallel_suites:
            # 并行运行套件
            tasks = []
            for suite in self.test_suites:
                task = suite.run(test_type, tags, name_pattern)
                tasks.append((suite.name, task))
            
            results = await asyncio.gather(*[task for _, task in tasks])
            
            for (suite_name, _), suite_results in zip(tasks, results):
                all_results[suite_name] = suite_results
                self.results.extend(suite_results)
        else:
            # 串行运行套件
            for suite in self.test_suites:
                suite_results = await suite.run(test_type, tags, name_pattern)
                all_results[suite.name] = suite_results
                self.results.extend(suite_results)
        
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self.results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "error": 0,
                "skipped": 0,
                "success_rate": 0.0,
                "total_duration": 0.0
            }
        
        total = len(self.results)
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        error = len([r for r in self.results if r.status == TestStatus.ERROR])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        success_rate = (passed / (total - skipped)) * 100 if (total - skipped) > 0 else 0
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": error,
            "skipped": skipped,
            "success_rate": success_rate,
            "total_duration": total_duration
        }
    
    def print_summary(self):
        """打印测试摘要"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        print(f"总计: {summary['total']}")
        print(f"通过: {summary['passed']}")
        print(f"失败: {summary['failed']}")
        print(f"错误: {summary['error']}")
        print(f"跳过: {summary['skipped']}")
        print(f"成功率: {summary['success_rate']:.2f}%")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        print("="*60)
        
        # 打印失败的测试
        failed_tests = [r for r in self.results if r.is_failure]
        if failed_tests:
            print("\n失败的测试:")
            for result in failed_tests:
                print(f"  - {result.test_name}: {result.error_message}")


class TestFramework:
    """测试框架"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.runner = TestRunner()
        self.global_setup: Optional[Callable] = None
        self.global_teardown: Optional[Callable] = None
    
    def set_global_setup(self, setup_func: Callable):
        """设置全局setup"""
        self.global_setup = setup_func
    
    def set_global_teardown(self, teardown_func: Callable):
        """设置全局teardown"""
        self.global_teardown = teardown_func
    
    def add_suite(self, suite: TestSuite):
        """添加测试套件"""
        self.runner.add_suite(suite)
    
    def add_test(self, test_case: TestCase, suite_name: str = "default"):
        """添加测试用例"""
        self.runner.add_test(test_case, suite_name)
    
    async def run(self, **kwargs) -> Dict[str, List[TestResult]]:
        """运行测试框架"""
        try:
            # 执行全局setup
            if self.global_setup:
                if asyncio.iscoroutinefunction(self.global_setup):
                    await self.global_setup()
                else:
                    self.global_setup()
            
            # 运行测试
            results = await self.runner.run_all(**kwargs)
            
            return results
            
        finally:
            # 执行全局teardown
            if self.global_teardown:
                try:
                    if asyncio.iscoroutinefunction(self.global_teardown):
                        await self.global_teardown()
                    else:
                        self.global_teardown()
                except Exception as e:
                    logger.error(f"全局teardown失败: {e}")
    
    def print_summary(self):
        """打印测试摘要"""
        self.runner.print_summary()


# 全局测试框架注册表
_frameworks: Dict[str, TestFramework] = {}

def register_test_framework(name: str, framework: TestFramework):
    """注册测试框架"""
    _frameworks[name] = framework
    logger.info(f"注册测试框架: {name}")

def get_test_framework(name: str) -> Optional[TestFramework]:
    """获取测试框架"""
    return _frameworks.get(name)

def create_default_framework() -> TestFramework:
    """创建默认测试框架"""
    framework = TestFramework("default")
    register_test_framework("default", framework)
    return framework 