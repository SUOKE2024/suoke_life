#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署验证脚本
用于验证RAG服务部署后的基本功能是否正常
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("deployment-verifier")

# 环境配置
ENVIRONMENTS = {
    "dev": {
        "base_url": "https://dev.api.suoke.life/rag",
        "timeout": 10,
    },
    "staging": {
        "base_url": "https://staging.api.suoke.life/rag",
        "timeout": 15,
    },
    "prod": {
        "base_url": "https://api.suoke.life/rag",
        "timeout": 20,
    }
}

# 测试用例
TEST_CASES = [
    {
        "endpoint": "/health",
        "method": "GET",
        "expected_status": 200,
        "response_check": lambda resp: resp.get("status") == "ok",
    },
    {
        "endpoint": "/api/v1/status",
        "method": "GET",
        "expected_status": 200,
        "response_check": lambda resp: "version" in resp,
    },
    {
        "endpoint": "/api/v1/query",
        "method": "POST",
        "payload": {
            "query": "中医四诊合参的基本理论是什么？",
            "max_results": 1,
        },
        "expected_status": 200,
        "response_check": lambda resp: "results" in resp and len(resp["results"]) > 0,
    }
]

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="验证RAG服务部署")
    parser.add_argument(
        "--env", 
        type=str, 
        choices=list(ENVIRONMENTS.keys()),
        default="dev",
        help="指定要验证的环境"
    )
    parser.add_argument(
        "--retries", 
        type=int, 
        default=3,
        help="失败重试次数"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="显示详细日志"
    )
    return parser.parse_args()

def make_request(
    url: str, 
    method: str, 
    timeout: int, 
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """发送HTTP请求并返回JSON响应"""
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    if headers:
        default_headers.update(headers)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(
                url, 
                json=payload, 
                headers=default_headers, 
                timeout=timeout
            )
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return {"error": str(e)}

def run_test_case(
    base_url: str, 
    test_case: Dict[str, Any], 
    timeout: int, 
    retries: int,
    verbose: bool
) -> bool:
    """运行单个测试用例"""
    endpoint = test_case["endpoint"]
    method = test_case.get("method", "GET")
    payload = test_case.get("payload")
    expected_status = test_case.get("expected_status", 200)
    response_check = test_case.get("response_check")
    
    url = f"{base_url}{endpoint}"
    
    logger.info(f"验证端点: {endpoint} [{method}]")
    
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                logger.info(f"重试 #{attempt}...")
                time.sleep(2 * attempt)  # 指数退避
                
            if verbose and payload:
                logger.info(f"请求载荷: {json.dumps(payload, ensure_ascii=False)}")
                
            response = make_request(url, method, timeout, payload)
            
            if verbose:
                logger.info(f"响应: {json.dumps(response, ensure_ascii=False)}")
                
            if response_check and not response_check(response):
                logger.error(f"响应验证失败: {json.dumps(response, ensure_ascii=False)}")
                continue
                
            logger.info(f"✅ 端点 {endpoint} 验证通过")
            return True
            
        except Exception as e:
            logger.error(f"测试用例执行失败: {e}")
            
    logger.error(f"❌ 端点 {endpoint} 验证失败，已重试 {retries} 次")
    return False

def main():
    """主函数"""
    args = parse_args()
    env = args.env
    retries = args.retries
    verbose = args.verbose
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    if env not in ENVIRONMENTS:
        logger.error(f"未知环境: {env}")
        sys.exit(1)
    
    env_config = ENVIRONMENTS[env]
    base_url = env_config["base_url"]
    timeout = env_config["timeout"]
    
    logger.info(f"开始验证部署: 环境={env}, 基础URL={base_url}")
    
    results = []
    for test_case in TEST_CASES:
        success = run_test_case(base_url, test_case, timeout, retries, verbose)
        results.append(success)
    
    if all(results):
        logger.info(f"✅ 所有测试通过! 环境 {env} 的RAG服务运行正常")
        sys.exit(0)
    else:
        success_count = sum(results)
        total_count = len(results)
        logger.error(f"❌ 测试未完全通过: {success_count}/{total_count} 成功")
        sys.exit(1)

if __name__ == "__main__":
    main() 