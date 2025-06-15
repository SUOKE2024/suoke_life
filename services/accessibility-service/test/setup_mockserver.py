#!/usr/bin/env python

"""
MockServer配置脚本 - 用于设置集成测试中需要的模拟服务

该脚本配置MockServer模拟依赖服务的响应，用于集成测试。
"""

import json
import logging
import os
import time

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MockServer配置
MOCKSERVER_URL = os.environ.get("MOCKSERVER_URL", "http://localhost:1080")
MAX_RETRY = 5
RETRY_INTERVAL = 2  # 秒


def wait_for_mockserver() -> None:
    """等待MockServer启动并可用"""
    for i in range(MAX_RETRY):
        try:
            response = requests.get(f"{MOCKSERVER_URL}/status")
            if response.status_code == 200:
                logger.info("MockServer已准备就绪")
                return True
        except requests.exceptions.ConnectionError:
            logger.info(f"等待MockServer启动...（{i+1}/{MAX_RETRY}）")

        time.sleep(RETRY_INTERVAL)

    logger.error("无法连接到MockServer，已达到最大重试次数")
    return False


def create_expectation(request_matcher, response_action):
    """创建MockServer期望"""
    expectation = {
        "httpRequest": request_matcher,
        "httpResponse": response_action,
        "times": {"unlimited": True},
    }

    response = requests.put(
        f"{MOCKSERVER_URL}/mockserver/expectation", json=expectation
    )

    if response.status_code == 201:
        logger.info(f"成功创建期望: {request_matcher.get('path', '')}")
        return True
    else:
        logger.error(f"创建期望失败: {response.text}")
        return False


def setup_health_data_service_mock() -> None:
    """设置健康数据服务的模拟响应"""
    # 模拟获取健康数据API
    create_expectation(
        {
            "method": "GET",
            "path": "/api/health-data/user/.*",
            "pathParameters": {"user_id": [".*"]},
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "user_id": "${pathParameters['user_id'][0]}",
                    "health_data": [
                        {
                            "type": "pulse",
                            "value": "75",
                            "unit": "bpm",
                            "timestamp": int(time.time()) - 3600,
                            "source": "mock",
                        },
                        {
                            "type": "blood_pressure",
                            "value": "120/80",
                            "unit": "mmHg",
                            "timestamp": int(time.time()) - 7200,
                            "source": "mock",
                        },
                        {
                            "type": "temperature",
                            "value": "36.5",
                            "unit": "°C",
                            "timestamp": int(time.time()) - 14400,
                            "source": "mock",
                        },
                    ],
                }
            ),
        },
    )

    # 模拟保存健康数据API
    create_expectation(
        {
            "method": "POST",
            "path": "/api/health-data/submit",
            "body": {
                "type": "JSON",
                "matchType": "ONLY_MATCHING_FIELDS",
                "json": {"user_id": ".*"},
            },
        },
        {
            "statusCode": 201,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {"success": True, "message": "数据提交成功", "data_points_accepted": 1}
            ),
        },
    )


def setup_agent_service_mock() -> None:
    """设置智能体服务的模拟响应"""
    # 模拟小艾智能体API
    create_expectation(
        {
            "method": "POST",
            "path": "/api/agents/xiaoai/notify",
            "body": {
                "type": "JSON",
                "matchType": "ONLY_MATCHING_FIELDS",
                "json": {"event_type": ".*", "user_id": ".*"},
            },
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "success": True,
                    "agent_id": "xiaoai-001",
                    "message": "通知已接收",
                    "timestamp": int(time.time()),
                }
            ),
        },
    )

    # 模拟其他智能体API
    for agent in ["xiaoke", "laoke", "soer"]:
        create_expectation(
            {
                "method": "POST",
                "path": f"/api/agents/{agent}/notify",
                "body": {
                    "type": "JSON",
                    "matchType": "ONLY_MATCHING_FIELDS",
                    "json": {"event_type": ".*", "user_id": ".*"},
                },
            },
            {
                "statusCode": 200,
                "headers": {"Content-Type": ["application/json"]},
                "body": json.dumps(
                    {
                        "success": True,
                        "agent_id": f"{agent}-001",
                        "message": "通知已接收",
                        "timestamp": int(time.time()),
                    }
                ),
            },
        )


def setup_user_service_mock() -> None:
    """设置用户服务的模拟响应"""
    # 模拟获取用户信息API
    create_expectation(
        {
            "method": "GET",
            "path": "/api/users/.*",
            "pathParameters": {"user_id": [".*"]},
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "user_id": "${pathParameters['user_id'][0]}",
                    "name": "测试用户",
                    "email": "test@suoke.life",
                    "phone": "13800138000",
                    "preferences": {
                        "font_size": "medium",
                        "high_contrast": False,
                        "voice_type": "female",
                        "speech_rate": 1.0,
                        "language": "zh-CN",
                        "dialect": "mandarin",
                    },
                    "emergency_contacts": [
                        {
                            "name": "紧急联系人1",
                            "relationship": "家人",
                            "phone": "13900139000",
                        }
                    ],
                }
            ),
        },
    )

    # 模拟用户不存在的情况
    create_expectation(
        {
            "method": "GET",
            "path": "/api/users/not-exist",
        },
        {
            "statusCode": 404,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps({"error": "用户不存在", "error_code": "USER_NOT_FOUND"}),
        },
    )

    # 模拟获取用户设置API
    create_expectation(
        {
            "method": "GET",
            "path": "/api/users/.*/settings",
            "pathParameters": {"user_id": [".*"]},
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "user_id": "${pathParameters['user_id'][0]}",
                    "accessibility": {
                        "font_size": "medium",
                        "high_contrast": False,
                        "voice_type": "female",
                        "speech_rate": 1.0,
                        "language": "zh-CN",
                        "dialect": "mandarin",
                        "screen_reader": False,
                        "sign_language": False,
                        "enabled_features": ["voice_assistance", "content_conversion"],
                    },
                    "notification": {
                        "enable_push": True,
                        "enable_sms": True,
                        "enable_email": False,
                        "quiet_hours_start": "22:00",
                        "quiet_hours_end": "08:00",
                    },
                    "privacy": {
                        "share_health_data": True,
                        "share_location": False,
                        "data_retention_days": 90,
                    },
                }
            ),
        },
    )


def setup_alert_service_mock() -> None:
    """设置警报服务的模拟响应"""
    # 模拟触发健康警报API
    create_expectation(
        {
            "method": "POST",
            "path": "/api/alerts/trigger",
            "body": {
                "type": "JSON",
                "matchType": "ONLY_MATCHING_FIELDS",
                "json": {"user_id": ".*", "alert_level": ".*"},
            },
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "success": True,
                    "alert_id": f"alert-{int(time.time())}",
                    "message": "警报已触发",
                    "notified_contacts": ["13900139000"],
                    "timestamp": int(time.time()),
                }
            ),
        },
    )

    # 模拟获取警报历史API
    create_expectation(
        {
            "method": "GET",
            "path": "/api/alerts/history",
            "queryStringParameters": {"user_id": [".*"]},
        },
        {
            "statusCode": 200,
            "headers": {"Content-Type": ["application/json"]},
            "body": json.dumps(
                {
                    "user_id": "${queryStringParameters['user_id'][0]}",
                    "alerts": [
                        {
                            "alert_id": f"alert-{int(time.time())-86400}",
                            "alert_level": "WARNING",
                            "alert_type": "high_pulse",
                            "description": "检测到较高心率",
                            "timestamp": int(time.time()) - 86400,
                            "acknowledged": True,
                        },
                        {
                            "alert_id": f"alert-{int(time.time())-172800}",
                            "alert_level": "INFORMATION",
                            "alert_type": "activity_reminder",
                            "description": "今日活动量不足",
                            "timestamp": int(time.time()) - 172800,
                            "acknowledged": True,
                        },
                    ],
                    "total_count": 2,
                    "has_more": False,
                }
            ),
        },
    )


def main() -> None:
    """主函数，设置所有模拟服务"""
    if not wait_for_mockserver():
        return False

    # 设置各个模拟服务
    setup_health_data_service_mock()
    setup_agent_service_mock()
    setup_user_service_mock()
    setup_alert_service_mock()

    logger.info("所有模拟服务配置完成")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
