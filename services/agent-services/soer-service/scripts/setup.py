#!/usr/bin/env python3
"""
初始化脚本
创建服务运行所需的目录结构
"""
import argparse
import json
import logging
import os
import shutil

import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup")

# 需要创建的目录
REQUIRED_DIRS = [
    "data",
    "data/profiles",
    "logs",
    "config/prompts/templates",
]

# 默认配置文件
DEFAULT_CONFIG = {
    "service": {
        "name": "soer_service",
        "version": "1.0.0",
        "description": "索儿智能体服务 - 健康生活管理引擎"
    },
    "server": {
        "host": "0.0.0.0",
        "grpc_port": 50054,
        "rest_port": 8054,
        "max_workers": 10
    },
    "grpc": {
        "max_message_length": 10485760,  # 10MB
        "port": 50054
    },
    "rest": {
        "port": 8054
    },
    "metrics": {
        "enabled": True,
        "prometheus": {
            "enabled": True,
            "port": 9098
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/soer-service.log"
    },
    "models": {
        "health_plan": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 2048,
            "temperature": 0.4,
            "system_prompt": "你是索尔，一个专注于健康生活管理的AI助手，基于中医体质和现代健康理论提供个性化的健康计划。"
        },
        "lifestyle": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 2048,
            "temperature": 0.5,
            "system_prompt": "你是索尔，一个专注于健康生活管理的AI助手，基于中医体质和现代健康理论提供个性化的生活方式建议。"
        },
        "emotional": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 1536,
            "temperature": 0.4,
            "system_prompt": "你是索尔，一个专注于健康生活管理的AI助手，基于中医情志理论分析情绪状态并提供调节建议。"
        }
    }
}

# 提示词模板
PROMPT_TEMPLATES = {
    "health_plan": """
你是索尔，一个专注于健康生活管理的AI助手。请根据用户的体质特点、健康目标和偏好生成一个个性化的健康计划。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}
- 健康目标: {health_goals}
- 个人偏好: {preferences}
- 当前季节: {current_season}

健康数据:
{health_data_formatted}

请提供以下方面的具体建议:
1. 饮食建议 (考虑中医五味理论和用户偏好)
2. 运动建议 (考虑用户的体质特点和运动偏好)
3. 生活作息建议 (考虑节气养生理念)
4. 营养补充建议 (如需要)
5. 日程安排 (一个典型的日计划)

每个建议应该具体且可执行，并与用户的体质类型相匹配。
""",

    "lifestyle": """
你是索尔，一个专注于健康生活管理的AI助手。请根据用户当前的情境和环境，提供个性化的生活方式建议。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}
- 当前情境: {context}
- 所在位置: {location}
- 环境数据: {environment_data}
- 当前习惯: {current_habits}
- 工作时间: {work_schedule}
- 健康痛点: {pain_points}

请提供以下几个方面的实用建议:
1. 作息时间安排
2. 工作效率提升方法
3. 家居环境调整建议
4. 压力管理技巧
5. 社交健康维护

每个建议应该考虑用户的体质特点、当前情境和环境因素，并提供具体可行的行动方案。
""",

    "emotional": """
你是索尔，一个专注于健康生活管理的AI助手。请分析用户当前的情绪状态，并根据中医情志理论提供调节建议。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}

情绪输入:
{emotional_inputs}

情绪分析模型结果:
{emotion_analysis_results}

请提供以下内容:
1. 主要情绪状态及强度
2. 情绪对身体健康的影响 (基于中医情志理论)
3. 情绪调节建议 (至少3个针对性的方法)
4. 是否需要进一步的健康干预

分析应融合中医五志理论，说明情绪与相应脏腑的关联，并提供有效缓解的方法。
"""
}

def create_directories() -> None:
    """创建必要的目录结构"""
    for directory in REQUIRED_DIRS:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"创建目录: {directory}")

def create_config_files() -> None:
    """创建配置文件"""
    # 创建主配置文件
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, allow_unicode=True, default_flow_style=False)
        logger.info(f"创建配置文件: {config_path}")

    # 创建提示词模板
    for name, template in PROMPT_TEMPLATES.items():
        template_path = f"config/prompts/templates/{name}.txt"
        if not os.path.exists(template_path):
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template)
            logger.info(f"创建提示词模板: {template_path}")

def create_sample_data() -> None:
    """创建示例数据"""
    # 创建示例用户档案
    sample_profile = {
        "user_id": "sample_user",
        "created_at": "2023-09-01T08:00:00",
        "last_updated": "2023-09-01T08:00:00",
        "constitution_type": "阳虚质",
        "health_goals": ["改善睡眠", "增强体质", "减轻压力"],
        "health_data": {
            "height": 175,
            "weight": 68,
            "blood_pressure": "118/75",
            "heart_rate": 72,
            "sleep_duration": 6.5,
            "activity_level": "轻度"
        },
        "allergies": ["花粉"],
        "medical_conditions": [],
        "medications": [],
        "preferences": {
            "diet_restrictions": ["无麸质"],
            "exercise_preferences": ["步行", "游泳", "瑜伽"],
            "lifestyle_preferences": ["早睡早起"]
        },
        "health_records": {
            "sleep": [
                {
                    "id": "9b3c8d7e-6f5e-4a3b-2c1d-0e9f8a7b6c5d",
                    "type": "sleep",
                    "created_at": "2023-09-01T08:00:00",
                    "data": {
                        "duration": 6.5,
                        "quality": "一般",
                        "start_time": "23:30",
                        "end_time": "06:00",
                        "interruptions": 2
                    }
                }
            ]
        },
        "active_plans": []
    }

    sample_profile_path = "data/profiles/sample_user.json"
    if not os.path.exists(sample_profile_path):
        with open(sample_profile_path, "w", encoding="utf-8") as f:
            json.dump(sample_profile, f, ensure_ascii=False, indent=2)
        logger.info(f"创建示例用户档案: {sample_profile_path}")

def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="索儿智能体服务初始化脚本")
    parser.add_argument("--clean", action="store_true", help="清理现有数据并重新初始化")
    args = parser.parse_args()

    # 如果指定了清理，删除现有数据
    if args.clean:
        for directory in REQUIRED_DIRS:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                logger.info(f"清理目录: {directory}")

    # 创建目录结构
    create_directories()

    # 创建配置文件
    create_config_files()

    # 创建示例数据
    create_sample_data()

    logger.info("初始化完成")

if __name__ == "__main__":
    main()
