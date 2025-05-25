#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工具集模块
提供统一的测试框架和工具
"""

from .test_framework import (
    TestFramework,
    TestCase,
    TestSuite,
    TestResult,
    TestRunner,
    get_test_framework
)

from .mock_tools import (
    MockManager,
    MockService,
    MockDatabase,
    MockHTTPClient,
    create_mock_manager
)

from .fixtures import (
    FixtureManager,
    DataFixture,
    DatabaseFixture,
    ServiceFixture,
    get_fixture_manager
)

from .assertions import (
    AssertionHelper,
    ResponseAssertion,
    DatabaseAssertion,
    PerformanceAssertion
)

from .test_decorators import (
    test_case,
    integration_test,
    unit_test,
    performance_test,
    mock_service,
    use_fixture
)

__all__ = [
    # 核心框架
    'TestFramework',
    'TestCase',
    'TestSuite',
    'TestResult',
    'TestRunner',
    'get_test_framework',
    
    # Mock工具
    'MockManager',
    'MockService',
    'MockDatabase',
    'MockHTTPClient',
    'create_mock_manager',
    
    # 测试夹具
    'FixtureManager',
    'DataFixture',
    'DatabaseFixture',
    'ServiceFixture',
    'get_fixture_manager',
    
    # 断言工具
    'AssertionHelper',
    'ResponseAssertion',
    'DatabaseAssertion',
    'PerformanceAssertion',
    
    # 装饰器
    'test_case',
    'integration_test',
    'unit_test',
    'performance_test',
    'mock_service',
    'use_fixture'
] 