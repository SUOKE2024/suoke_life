#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务集成测试 - 负载和性能测试
测试服务在高并发请求下的表现
"""
import os
import time
import uuid
import pytest
import asyncio
import statistics
from typing import List, Dict, Any

from httpx import AsyncClient

from cmd.server.main import app


# 测试配置
TEST_SERVER_HOST = os.getenv("TEST_SERVER_HOST", "localhost")
TEST_SERVER_HTTP_PORT = int(os.getenv("TEST_SERVER_HTTP_PORT", "8080"))
TEST_USERS_COUNT = int(os.getenv("TEST_USERS_COUNT", "10"))  # 测试用户数量
TEST_CONCURRENCY = int(os.getenv("TEST_CONCURRENCY", "50"))  # 并发请求数
TEST_DURATION = int(os.getenv("TEST_DURATION", "10"))  # 测试持续时间(秒)


@pytest.fixture
def test_user_batch():
    """生成批量测试用户数据"""
    users = []
    for i in range(TEST_USERS_COUNT):
        unique_id = str(uuid.uuid4())[:8]
        users.append({
            "username": f"loadtest_user_{unique_id}",
            "email": f"loadtest_{unique_id}@example.com",
            "password": "LoadTest123!",
            "phone_number": f"+8613800{unique_id}",
            "profile_data": {
                "display_name": f"负载测试用户{i}",
                "age": 30,
                "location": "北京"
            }
        })
    return users


@pytest.fixture
async def http_client():
    """创建HTTP客户端"""
    base_url = f"http://{TEST_SERVER_HOST}:{TEST_SERVER_HTTP_PORT}"
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client


async def register_test_users(client, users):
    """注册测试用户"""
    tokens = {}
    
    for user in users:
        # 注册用户
        response = await client.post("/api/v1/auth/register", json=user)
        assert response.status_code == 201
        
        # 登录获取令牌
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        
        tokens[user["username"]] = {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"]
        }
    
    return tokens


@pytest.mark.asyncio
async def test_login_performance(http_client, test_user_batch):
    """测试登录接口的性能"""
    # 先注册用户
    tokens = await register_test_users(http_client, test_user_batch)
    
    # 准备登录数据
    login_payloads = []
    for user in test_user_batch:
        login_payloads.append({
            "username": user["username"],
            "password": user["password"]
        })
    
    # 执行并发登录
    start_time = time.time()
    response_times = []
    success_count = 0
    error_count = 0
    
    async def login_task(payload):
        nonlocal success_count, error_count
        task_start = time.time()
        try:
            response = await http_client.post("/api/v1/auth/login", json=payload)
            response_time = time.time() - task_start
            response_times.append(response_time)
            
            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1
                
            return response.status_code, response_time
        except Exception as e:
            error_count += 1
            return -1, time.time() - task_start
    
    # 创建任务列表
    tasks = []
    for _ in range(TEST_CONCURRENCY):
        payload = login_payloads[_ % len(login_payloads)]
        tasks.append(login_task(payload))
    
    # 执行并发任务
    results = await asyncio.gather(*tasks)
    
    # 分析结果
    total_time = time.time() - start_time
    total_requests = len(results)
    
    # 计算性能指标
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        rps = total_requests / total_time
    else:
        avg_time = min_time = max_time = p95_time = rps = 0
    
    # 输出性能报告
    performance_report = {
        "total_requests": total_requests,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": f"{success_count/total_requests*100:.2f}%",
        "total_time": f"{total_time:.2f}s",
        "avg_response_time": f"{avg_time*1000:.2f}ms",
        "min_response_time": f"{min_time*1000:.2f}ms",
        "max_response_time": f"{max_time*1000:.2f}ms",
        "p95_response_time": f"{p95_time*1000:.2f}ms",
        "requests_per_second": f"{rps:.2f}",
    }
    
    print("\n登录性能测试报告:")
    for key, value in performance_report.items():
        print(f"  {key}: {value}")
    
    # 确保成功率至少为90%
    assert success_count / total_requests >= 0.9


@pytest.mark.asyncio
async def test_token_verification_performance(http_client, test_user_batch):
    """测试令牌验证接口的性能"""
    # 先注册用户并获取令牌
    tokens = await register_test_users(http_client, test_user_batch)
    
    # 准备验证请求
    verify_requests = []
    for username, token_data in tokens.items():
        access_token = token_data["access_token"]
        verify_requests.append({
            "token": access_token
        })
    
    # 执行并发验证
    start_time = time.time()
    response_times = []
    success_count = 0
    error_count = 0
    
    async def verify_task(payload):
        nonlocal success_count, error_count
        task_start = time.time()
        try:
            response = await http_client.post("/api/v1/auth/verify", json=payload)
            response_time = time.time() - task_start
            response_times.append(response_time)
            
            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1
                
            return response.status_code, response_time
        except Exception as e:
            error_count += 1
            return -1, time.time() - task_start
    
    # 创建任务列表
    tasks = []
    for _ in range(TEST_CONCURRENCY):
        payload = verify_requests[_ % len(verify_requests)]
        tasks.append(verify_task(payload))
    
    # 执行并发任务
    results = await asyncio.gather(*tasks)
    
    # 分析结果
    total_time = time.time() - start_time
    total_requests = len(results)
    
    # 计算性能指标
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        rps = total_requests / total_time
    else:
        avg_time = min_time = max_time = p95_time = rps = 0
    
    # 输出性能报告
    performance_report = {
        "total_requests": total_requests,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": f"{success_count/total_requests*100:.2f}%",
        "total_time": f"{total_time:.2f}s",
        "avg_response_time": f"{avg_time*1000:.2f}ms",
        "min_response_time": f"{min_time*1000:.2f}ms",
        "max_response_time": f"{max_time*1000:.2f}ms",
        "p95_response_time": f"{p95_time*1000:.2f}ms",
        "requests_per_second": f"{rps:.2f}",
    }
    
    print("\n令牌验证性能测试报告:")
    for key, value in performance_report.items():
        print(f"  {key}: {value}")
    
    # 确保成功率至少为95%
    assert success_count / total_requests >= 0.95


@pytest.mark.asyncio
async def test_sustained_load(http_client, test_user_batch):
    """测试持续负载下的性能"""
    # 先注册用户并获取令牌
    tokens = await register_test_users(http_client, test_user_batch)
    
    # 准备各种请求类型
    login_payloads = []
    verify_payloads = []
    refresh_payloads = []
    
    for user in test_user_batch:
        # 登录请求
        login_payloads.append({
            "username": user["username"],
            "password": user["password"]
        })
        
        # 令牌验证请求
        token_data = tokens.get(user["username"], {})
        if token_data:
            verify_payloads.append({
                "token": token_data.get("access_token", "")
            })
            
            # 刷新令牌请求
            refresh_payloads.append({
                "refresh_token": token_data.get("refresh_token", "")
            })
    
    # 各种请求的混合负载
    mixed_payloads = []
    for i in range(len(test_user_batch)):
        if i < len(login_payloads):
            mixed_payloads.append(("login", login_payloads[i]))
        if i < len(verify_payloads):
            mixed_payloads.append(("verify", verify_payloads[i]))
        if i < len(refresh_payloads):
            mixed_payloads.append(("refresh", refresh_payloads[i]))
    
    # 执行持续负载测试
    start_time = time.time()
    end_time = start_time + TEST_DURATION
    
    results = {
        "login": {"success": 0, "error": 0, "times": []},
        "verify": {"success": 0, "error": 0, "times": []},
        "refresh": {"success": 0, "error": 0, "times": []},
    }
    
    request_count = 0
    
    async def load_task():
        nonlocal request_count
        while time.time() < end_time:
            # 随机选择一个请求类型和负载
            req_type, payload = mixed_payloads[request_count % len(mixed_payloads)]
            request_count += 1
            
            task_start = time.time()
            try:
                if req_type == "login":
                    response = await http_client.post("/api/v1/auth/login", json=payload)
                elif req_type == "verify":
                    response = await http_client.post("/api/v1/auth/verify", json=payload)
                elif req_type == "refresh":
                    response = await http_client.post("/api/v1/auth/refresh", json=payload)
                
                response_time = time.time() - task_start
                results[req_type]["times"].append(response_time)
                
                if response.status_code < 400:
                    results[req_type]["success"] += 1
                else:
                    results[req_type]["error"] += 1
                    
            except Exception as e:
                results[req_type]["error"] += 1
    
    # 创建并发任务
    tasks = [load_task() for _ in range(TEST_CONCURRENCY)]
    await asyncio.gather(*tasks)
    
    # 分析结果
    total_time = time.time() - start_time
    total_requests = sum(results[req_type]["success"] + results[req_type]["error"] 
                        for req_type in results)
    
    # 计算总体性能指标
    all_times = []
    for req_type in results:
        all_times.extend(results[req_type]["times"])
    
    if all_times:
        avg_time = statistics.mean(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        p95_time = sorted(all_times)[int(len(all_times) * 0.95)]
        rps = total_requests / total_time
    else:
        avg_time = min_time = max_time = p95_time = rps = 0
    
    # 输出性能报告
    performance_report = {
        "test_duration": f"{total_time:.2f}s",
        "total_requests": total_requests,
        "requests_per_second": f"{rps:.2f}",
        "avg_response_time": f"{avg_time*1000:.2f}ms",
        "min_response_time": f"{min_time*1000:.2f}ms",
        "max_response_time": f"{max_time*1000:.2f}ms",
        "p95_response_time": f"{p95_time*1000:.2f}ms",
    }
    
    print("\n持续负载测试报告:")
    for key, value in performance_report.items():
        print(f"  {key}: {value}")
    
    # 按请求类型输出明细
    for req_type in results:
        total = results[req_type]["success"] + results[req_type]["error"]
        if total == 0:
            continue
            
        success_rate = results[req_type]["success"] / total * 100
        times = results[req_type]["times"]
        
        if times:
            avg = statistics.mean(times) * 1000
            req_report = {
                "total_requests": total,
                "success_rate": f"{success_rate:.2f}%",
                "avg_response_time": f"{avg:.2f}ms"
            }
        else:
            req_report = {
                "total_requests": total,
                "success_rate": f"{success_rate:.2f}%",
                "avg_response_time": "N/A"
            }
            
        print(f"\n  {req_type} 请求:")
        for key, value in req_report.items():
            print(f"    {key}: {value}")
    
    # 确保总体成功率至少为85%
    total_success = sum(results[req_type]["success"] for req_type in results)
    assert total_success / total_requests >= 0.85 