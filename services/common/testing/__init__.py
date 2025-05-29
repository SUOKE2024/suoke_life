#!/usr/bin/env python3
"""
测试工具集模块
提供统一的测试框架和工具
"""

from .assertions import (
    AssertionHelper,
    DatabaseAssertion,
    PerformanceAssertion,
    ResponseAssertion,
)
from .fixtures import (
    DatabaseFixture,
    DataFixture,
    FixtureManager,
    ServiceFixture,
    get_fixture_manager,
)
from .mock_tools import (
    MockDatabase,
    MockHTTPClient,
    MockManager,
    MockService,
    create_mock_manager,
)
from .test_decorators import (
    integration_test,
    mock_service,
    performance_test,
    test_case,
    unit_test,
    use_fixture,
)
from .test_framework import (
    TestCase,
    TestFramework,
    TestResult,
    TestRunner,
    TestSuite,
    get_test_framework,
)

__all__ = [
    # 断言工具
    "AssertionHelper",
    "DataFixture",
    "DatabaseAssertion",
    "DatabaseFixture",
    # 测试夹具
    "FixtureManager",
    "MockDatabase",
    "MockHTTPClient",
    # Mock工具
    "MockManager",
    "MockService",
    "PerformanceAssertion",
    "ResponseAssertion",
    "ServiceFixture",
    "TestCase",
    # 核心框架
    "TestFramework",
    "TestResult",
    "TestRunner",
    "TestSuite",
    "create_mock_manager",
    "get_fixture_manager",
    "get_test_framework",
    "integration_test",
    "mock_service",
    "performance_test",
    # 装饰器
    "test_case",
    "unit_test",
    "use_fixture",
]
