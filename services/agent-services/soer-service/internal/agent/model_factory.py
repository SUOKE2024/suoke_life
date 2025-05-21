#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型工厂类
负责创建和管理不同类型的大模型客户端，为索儿智能体提供支持
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Union, Tuple
import asyncio
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from abc import ABC, abstractmethod
import aiohttp

try:
    import openai
    from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam
    from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionMessageParam
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logging.warning("未安装openai库，无法使用OpenAI API")

try:
    import zhipuai
    HAS_ZHIPUAI = True
except ImportError:
    HAS_ZHIPUAI = False
    logging.warning("未安装zhipuai库，无法使用智谱API")

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector, track_llm_metrics
from pkg.utils.resilience import circuit_breaker, rate_limiter

logger = logging.getLogger(__name__)

class ModelInterface(ABC):
    """模型接口抽象类"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本响应"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭模型资源"""
        pass

class LLMModel(ModelInterface):
    """大语言模型实现"""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        """初始化LLM模型"""
        self.model_id = model_id
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8000/v1/completions")
        self.api_key = config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.max_tokens = config.get("max_tokens", 1024)
        self.temperature = config.get("temperature", 0.7)
        
        # 设置重试次数和超时
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 30)
        
        # 创建HTTP会话
        self.session = None
        
        logger.info(f"初始化LLM模型: {model_id}")
    
    async def _ensure_session(self) -> None:
        """确保HTTP会话已创建"""
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本响应"""
        await self._ensure_session()
        
        # 准备请求数据
        data = {
            "model": self.model_id,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 1.0),
            "n": 1,
            "stream": False,
            "stop": kwargs.get("stop", None)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    self.endpoint,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API请求失败: 状态码 {response.status}, 错误: {error_text}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                            continue
                        return f"模型调用失败: HTTP {response.status}"
                    
                    result = await response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["text"]
                    else:
                        logger.error(f"API响应格式错误: {result}")
                        return "模型响应解析失败"
            
            except asyncio.TimeoutError:
                logger.error(f"调用模型超时 (尝试 {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return "模型调用超时"
            
            except Exception as e:
                logger.error(f"调用模型出错: {str(e)}", exc_info=True)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return f"模型调用出错: {str(e)}"
    
    async def close(self) -> None:
        """关闭模型资源"""
        if self.session:
            await self.session.close()
            self.session = None

class ChatLLMModel(ModelInterface):
    """聊天模型实现"""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        """初始化聊天LLM模型"""
        self.model_id = model_id
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8000/v1/chat/completions")
        self.api_key = config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.max_tokens = config.get("max_tokens", 1024)
        self.temperature = config.get("temperature", 0.7)
        self.system_prompt = config.get("system_prompt", "你是索尔，一个专注于健康生活管理的AI助手，基于中医体质和现代健康理论提供个性化的生活方式指导。")
        
        # 设置重试次数和超时
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 60)
        
        # 创建HTTP会话
        self.session = None
        
        logger.info(f"初始化聊天LLM模型: {model_id}")
    
    async def _ensure_session(self) -> None:
        """确保HTTP会话已创建"""
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成聊天响应"""
        await self._ensure_session()
        
        # 准备消息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 如果有历史消息，添加到消息列表中
        if "history" in kwargs:
            messages = kwargs["history"] + [{"role": "user", "content": prompt}]
        
        # 准备请求数据
        data = {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 1.0),
            "n": 1,
            "stream": False,
            "stop": kwargs.get("stop", None)
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    self.endpoint,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API请求失败: 状态码 {response.status}, 错误: {error_text}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                            continue
                        return f"模型调用失败: HTTP {response.status}"
                    
                    result = await response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"API响应格式错误: {result}")
                        return "模型响应解析失败"
            
            except asyncio.TimeoutError:
                logger.error(f"调用模型超时 (尝试 {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return "模型调用超时"
            
            except Exception as e:
                logger.error(f"调用模型出错: {str(e)}", exc_info=True)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return f"模型调用出错: {str(e)}"
    
    async def close(self) -> None:
        """关闭模型资源"""
        if self.session:
            await self.session.close()
            self.session = None

class MockModel(ModelInterface):
    """模拟模型实现（测试和开发环境使用）"""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        """初始化模拟模型"""
        self.model_id = model_id
        self.config = config
        self.mock_responses = self._load_mock_responses()
        logger.info(f"初始化模拟模型: {model_id}")
    
    def _load_mock_responses(self) -> Dict[str, str]:
        """加载模拟响应"""
        mock_responses = {}
        
        # 健康计划模拟响应
        mock_responses["health_plan"] = """
## 健康计划

### 饮食建议
- 早餐：温热粥类为主，如小米粥、薏米粥，搭配一小碟咸菜或腐乳
- 午餐：以温性食物为主，如胡萝卜、南瓜炖排骨汤
- 晚餐：清淡为主，如蒸鱼、蔬菜汤，避免辛辣刺激食物
- 水果：建议食用熟苹果、桂圆、龙眼等温性水果
- 避免：生冷、寒凉食物，如冰镇饮料、凉拌菜、西瓜等

### 运动建议
- 每日晨起练习八段锦或太极拳15-20分钟
- 午后散步30分钟，保持身体温暖
- 每周进行2-3次中等强度有氧运动，如快走、慢跑
- 避免大量出汗的剧烈运动
- 雨天或寒冷天气减少户外活动

### 生活作息建议
- 早睡早起，尽量保持23:00前入睡，6:30-7:00起床
- 午饭后适当午休20-30分钟
- 保持居室温暖干燥，避免受风寒
- 情绪调节：保持心情舒畅，避免忧思郁怒
- 定期按摩足三里、关元等穴位增强阳气

### 营养补充建议
- 每日一勺蜂蜜温水，补中益气
- 适量补充维生素D，增强免疫力
- 根据体质可适量服用人参茶或黄芪茶
- 冬季可服用桂圆红枣茶，温补脾胃

### 日程安排
早晨6:30-7:00：起床，温水洗漱
7:00-7:30：八段锦或太极拳练习
7:30-8:00：温热早餐
12:00-12:30：午餐
12:30-13:00：午休
15:00-15:30：下午茶（温性茶饮）
17:00-17:30：傍晚散步
18:30-19:00：晚餐
21:00-21:30：泡脚、按摩穴位
23:00前：就寝
"""
        
        # 生活方式建议模拟响应
        mock_responses["lifestyle"] = """
## 生活方式建议

### 作息时间安排
- 根据您的上班时间，建议6:30起床，保证充足睡眠
- 设置固定就寝时间，夜间23:00前入睡
- 工作日中午争取20-30分钟午休
- 周末保持相近的作息规律，避免睡眠时间差异过大

### 工作效率提升方法
- 采用番茄工作法，25分钟专注工作后休息5分钟
- 办公桌摆放绿色植物，缓解视觉疲劳
- 每工作1小时，起身活动5分钟，避免久坐
- 重要事项安排在精力最充沛的上午9-11点处理
- 使用待办清单工具，降低心理负担

### 家居环境调整建议
- 卧室保持通风，湿度控制在40-60%
- 客厅和书房增加柔和照明，减少直射强光
- 厨房油烟及时排出，使用空气净化器
- 添加适合阳虚体质的植物，如吊兰、芦荟等
- 床铺保持温暖干燥，换季及时更换寝具

### 压力管理技巧
- 每日练习腹式呼吸5-10分钟
- 建立固定的放松仪式，如泡茶、听音乐
- 工作压力大时，使用5-4-3-2-1感官专注法
- 周末安排一次大自然接触活动
- 写感恩日记，培养积极心态

### 社交健康维护
- 每周安排一次与朋友或家人的线下聚会
- 加入一个兴趣小组或社区活动
- 主动联系久未联系的朋友
- 学习一项需要社交互动的新技能或爱好
- 适度限制社交媒体使用时间，增加真实社交
"""
        
        # 情绪分析模拟响应
        mock_responses["emotional"] = """
## 情绪分析报告

### 主要情绪状态：忧郁（强度：中度）
用户当前表现出中度忧郁情绪，伴随轻微焦虑。情绪表达中包含对工作压力的担忧和对未来的不确定感。

### 情绪对身体健康的影响
根据中医情志理论，忧郁情绪主要影响肺系统功能。长期忧郁可导致气机郁滞，影响肺的宣发肃降功能。目前用户的忧郁情绪已经对肺系统产生轻度影响，可能表现为胸闷、气短等症状。同时，情绪的波动也间接影响脾胃功能，可能导致食欲减退和消化功能下降。

### 情绪调节建议
1. **疏肝理气法**：每日进行深呼吸练习，吸气时意念气息沿任脉上行，呼气时沿督脉下行，帮助疏通气机，每次10-15分钟。

2. **穴位按摩**：每日按摩合谷穴、太冲穴和内关穴各2-3分钟，帮助疏肝解郁，改善气血运行。

3. **香薰调理**：使用薰衣草、佛手柑等精油进行芳香疗法，有助于缓解忧郁情绪。可在工作场所使用便携式香薰，或晚上休息时在卧室使用香薰灯。

4. **饮食调整**：增加玫瑰花茶、柑橘类水果摄入，减少辛辣刺激食物，有助于疏肝解郁。

5. **活动安排**：每周安排2-3次户外散步或轻度运动，尤其是在树木繁茂的公园，帮助舒展胸肺，改善气机流通。

### 进一步干预建议
目前情绪状态属于轻中度，通过自我调节可以改善。建议持续关注情绪变化，若两周内忧郁情绪无改善或加重，建议咨询中医师进行辩证施治，或考虑心理咨询辅助调节。
"""
        
        return mock_responses
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成模拟响应"""
        # 模拟网络延迟
        await asyncio.sleep(0.5)
        
        # 根据模型ID返回对应的模拟响应
        if self.model_id in self.mock_responses:
            return self.mock_responses[self.model_id]
        else:
            return "这是一个模拟响应。实际部署时将使用真实的AI模型。"
    
    async def close(self) -> None:
        """关闭模型资源"""
        pass  # 模拟模型不需要清理资源

class ModelFactory:
    """
    大模型工厂类，用于创建、管理和调用各种大模型服务，为索儿智能体提供健康管理相关能力
    """
    
    def __init__(self):
        """初始化大模型工厂"""
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 加载配置
        self.llm_config = self.config.get_section('models.llm')
        self.local_llm_config = self.config.get_section('models.local_llm')
        
        # 设置默认模型
        self.primary_model = self.llm_config.get('primary_model', 'gpt-4o-mini')
        self.fallback_model = self.llm_config.get('fallback_model', 'llama-3-8b')
        
        # 初始化客户端映射表
        self.clients = {}
        
        # 初始化各大模型客户端
        self._init_openai_client()
        self._init_local_llm_client()
        self._init_zhipu_client()
        self._init_baidu_client()
        
        logger.info(f"大模型工厂初始化完成，可用模型: {list(self.clients.keys())}")
    
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        if not HAS_OPENAI:
            logger.warning("未安装openai库，跳过OpenAI客户端初始化")
            return
        
        try:
            # 获取API密钥
            api_key = self.llm_config.get('api_key', os.getenv('OPENAI_API_KEY', ''))
            
            if not api_key:
                logger.warning("未配置OpenAI API密钥，跳过OpenAI客户端初始化")
                return
            
            # 创建客户端
            api_base = self.llm_config.get('api_base', 'https://api.openai.com/v1')
            org_id = self.llm_config.get('org_id', None)
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base,
                organization=org_id,
                timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
            )
            
            # 验证连接
            if self._verify_openai_connection(client):
                # 注册客户端
                openai_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
                for model in openai_models:
                    self.clients[model] = {
                        'client': client,
                        'type': 'openai',
                        'provider': 'OpenAI',
                        'max_tokens': 8192
                    }
                
                logger.info(f"OpenAI客户端初始化成功，已注册模型: {openai_models}")
            else:
                logger.warning("OpenAI客户端连接验证失败，跳过注册")
        
        except Exception as e:
            logger.error(f"初始化OpenAI客户端失败: {e}")
    
    def _verify_openai_connection(self, client) -> bool:
        """验证OpenAI客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是索儿，一个专注于健康管理的智能体"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )
            
            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("OpenAI连接验证成功")
                return True
            else:
                logger.warning("OpenAI连接验证响应无效")
                return False
                
        except Exception as e:
            logger.warning(f"OpenAI连接验证失败: {e}")
            return False
    
    def _init_local_llm_client(self):
        """初始化本地LLM客户端"""
        try:
            # 检查本地LLM配置
            local_llm_url = self.local_llm_config.get('endpoint_url')
            
            if not local_llm_url:
                logger.warning("未配置本地LLM端点URL，跳过本地LLM客户端初始化")
                return
            
            # 创建客户端 (使用OpenAI兼容接口)
            client = openai.OpenAI(
                base_url=local_llm_url,
                api_key="not-needed",  # 本地服务可能不需要API密钥
                timeout=httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=5.0)
            )
            
            # 验证连接
            if self._verify_local_llm_connection(client):
                # 注册客户端
                local_models = self.local_llm_config.get('available_models', ['llama-3-8b', 'llama-3-70b'])
                for model in local_models:
                    self.clients[model] = {
                        'client': client,
                        'type': 'local_llm',
                        'provider': 'Local',
                        'max_tokens': self.local_llm_config.get('max_tokens', 4096)
                    }
                
                logger.info(f"本地LLM客户端初始化成功，已注册模型: {local_models}")
            else:
                logger.warning("本地LLM客户端连接验证失败，跳过注册")
                
        except Exception as e:
            logger.error(f"初始化本地LLM客户端失败: {e}")
    
    def _verify_local_llm_connection(self, client) -> bool:
        """验证本地LLM客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model=self.local_llm_config.get('default_model', 'llama-3-8b'),
                messages=[
                    {"role": "system", "content": "你是索儿，一个专注于健康管理的智能体"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )
            
            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("本地LLM连接验证成功")
                return True
            else:
                logger.warning("本地LLM连接验证响应无效")
                return False
                
        except Exception as e:
            logger.warning(f"本地LLM连接验证失败: {e}")
            return False
    
    def _init_zhipu_client(self):
        """初始化智谱AI客户端"""
        if not HAS_ZHIPUAI:
            logger.warning("未安装zhipuai库，跳过智谱客户端初始化")
            return
        
        try:
            # 获取API密钥
            zhipu_config = self.config.get_section('models.zhipu')
            api_key = zhipu_config.get('api_key', os.getenv('ZHIPU_API_KEY', ''))
            
            if not api_key:
                logger.warning("未配置智谱API密钥，跳过智谱客户端初始化")
                return
            
            # 创建客户端
            client = zhipuai.ZhipuAI(api_key=api_key)
            
            # 验证连接
            if self._verify_zhipu_connection(client):
                # 注册客户端
                zhipu_models = ['glm-4', 'glm-3-turbo']
                for model in zhipu_models:
                    self.clients[model] = {
                        'client': client,
                        'type': 'zhipu',
                        'provider': '智谱AI',
                        'max_tokens': 8192
                    }
                
                logger.info(f"智谱AI客户端初始化成功，已注册模型: {zhipu_models}")
            else:
                logger.warning("智谱AI客户端连接验证失败，跳过注册")
                
        except Exception as e:
            logger.error(f"初始化智谱AI客户端失败: {e}")
    
    def _verify_zhipu_connection(self, client) -> bool:
        """验证智谱AI客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model="glm-3-turbo",
                messages=[
                    {"role": "system", "content": "你是索儿，一个专注于健康管理的智能体"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )
            
            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("智谱AI连接验证成功")
                return True
            else:
                logger.warning("智谱AI连接验证响应无效")
                return False
                
        except Exception as e:
            logger.warning(f"智谱AI连接验证失败: {e}")
            return False
    
    def _init_baidu_client(self):
        """初始化百度文心一言客户端"""
        try:
            # 获取配置
            baidu_config = self.config.get_section('models.baidu')
            api_key = baidu_config.get('api_key', os.getenv('BAIDU_API_KEY', ''))
            secret_key = baidu_config.get('secret_key', os.getenv('BAIDU_SECRET_KEY', ''))
            
            if not api_key or not secret_key:
                logger.warning("未配置百度API密钥，跳过百度客户端初始化")
                return
            
            # 注册HTTP客户端（百度使用自定义HTTP请求）
            baidu_models = ['ernie-bot-4', 'ernie-bot']
            for model in baidu_models:
                self.clients[model] = {
                    'client': {
                        'api_key': api_key,
                        'secret_key': secret_key,
                        'url': baidu_config.get('api_url', 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/')
                    },
                    'type': 'baidu',
                    'provider': '百度智能云',
                    'max_tokens': 4096
                }
            
            logger.info(f"百度文心一言客户端初始化成功，已注册模型: {baidu_models}")
                
        except Exception as e:
            logger.error(f"初始化百度文心一言客户端失败: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout))
    )
    @circuit_breaker(failure_threshold=5, recovery_time=60)
    @rate_limiter(max_calls=60, time_period=60)
    @track_llm_metrics(query_type="health_management")
    async def generate_chat_completion(self, 
                                      model: str, 
                                      messages: List[Dict[str, str]], 
                                      temperature: float = 0.7,
                                      max_tokens: int = 2048) -> Tuple[str, Dict[str, Any]]:
        """
        生成聊天完成
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成令牌数
            
        Returns:
            Tuple[str, Dict[str, Any]]: 生成的文本和元数据
        """
        start_time = time.time()
        prompt_tokens = 0
        completion_tokens = 0
        
        # 判断模型是否可用
        if model not in self.clients:
            available_models = list(self.clients.keys())
            logger.warning(f"请求的模型 {model} 不可用，尝试使用 {self.fallback_model if self.fallback_model in available_models else available_models[0]}")
            
            # 使用备用模型
            if self.fallback_model in self.clients:
                model = self.fallback_model
            elif available_models:
                model = available_models[0]
            else:
                raise ValueError("没有可用的大模型服务")
        
        # 获取模型客户端
        client_info = self.clients[model]
        client = client_info['client']
        client_type = client_info['type']
        
        try:
            # 根据客户端类型调用不同的API
            if client_type == 'openai' or client_type == 'local_llm':
                return await self._call_openai_compatible_api(client, model, messages, temperature, max_tokens)
            elif client_type == 'zhipu':
                return await self._call_zhipu_api(client, model, messages, temperature, max_tokens)
            elif client_type == 'baidu':
                return await self._call_baidu_api(client_info, model, messages, temperature, max_tokens)
            else:
                raise ValueError(f"不支持的客户端类型: {client_type}")
                
        except Exception as e:
            logger.error(f"调用{client_info['provider']}模型 {model} 失败: {e}")
            
            # 记录模型调用失败指标
            self.metrics.track_llm_error(model, str(e))
            
            # 如果是主模型失败，尝试使用备用模型
            if model == self.primary_model and model != self.fallback_model and self.fallback_model in self.clients:
                logger.info(f"尝试使用备用模型 {self.fallback_model}")
                return await self.generate_chat_completion(self.fallback_model, messages, temperature, max_tokens)
            
            # 返回错误信息
            return f"很抱歉，我暂时无法处理您的请求。错误: {str(e)}", {
                'model': model,
                'provider': client_info['provider'],
                'error': str(e),
                'success': False
            }
    
    async def _call_openai_compatible_api(self, client, model, messages, temperature, max_tokens):
        """调用OpenAI兼容的API（包括OpenAI和本地LLM）"""
        start_time = time.time()
        
        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                formatted_messages.append(ChatCompletionSystemMessageParam(role="system", content=msg['content']))
            elif msg['role'] == 'user':
                formatted_messages.append(ChatCompletionUserMessageParam(role="user", content=msg['content']))
            elif msg['role'] == 'assistant':
                formatted_messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=msg['content']))
        
        # 调用API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.3
        )
        
        # 提取响应文本
        response_text = response.choices[0].message.content
        
        # 获取token计数
        if hasattr(response, 'usage'):
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
        else:
            # 估算token数量
            prompt_tokens = sum(len(m['content'].split()) * 1.3 for m in messages)
            completion_tokens = len(response_text.split()) * 1.3
        
        # 计算响应时间
        latency = time.time() - start_time
        
        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)
        
        # 元数据
        metadata = {
            'model': model,
            'provider': self.clients[model]['provider'],
            'confidence': 0.95,  # OpenAI不提供置信度，使用默认值
            'latency': latency,
            'token_count': {
                'prompt': prompt_tokens,
                'completion': completion_tokens
            },
            'success': True
        }
        
        return response_text, metadata
    
    async def _call_zhipu_api(self, client, model, messages, temperature, max_tokens):
        """调用智谱API"""
        start_time = time.time()
        
        # 调用API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 提取响应文本
        response_text = response.choices[0].message.content
        
        # 获取token计数
        if hasattr(response, 'usage'):
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
        else:
            # 估算token数量
            prompt_tokens = sum(len(m['content'].split()) * 1.3 for m in messages)
            completion_tokens = len(response_text.split()) * 1.3
        
        # 计算响应时间
        latency = time.time() - start_time
        
        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)
        
        # 元数据
        metadata = {
            'model': model,
            'provider': '智谱AI',
            'confidence': 0.95,
            'latency': latency,
            'token_count': {
                'prompt': prompt_tokens,
                'completion': completion_tokens
            },
            'success': True
        }
        
        return response_text, metadata
    
    async def _call_baidu_api(self, client_info, model, messages, temperature, max_tokens):
        """调用百度文心一言API"""
        start_time = time.time()
        
        # 获取客户端配置
        api_key = client_info['client']['api_key']
        secret_key = client_info['client']['secret_key']
        base_url = client_info['client']['url']
        
        # 获取访问令牌
        access_token = await self._get_baidu_access_token(api_key, secret_key)
        
        # 准备请求数据
        url = f"{base_url}{model}?access_token={access_token}"
        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens
        }
        
        # 发送请求
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        # 处理响应
        if "error_code" in result:
            raise ValueError(f"百度API错误: {result.get('error_msg', '未知错误')}")
        
        # 提取响应文本
        response_text = result['result']
        
        # 获取token计数
        prompt_tokens = result.get('usage', {}).get('prompt_tokens', 0)
        completion_tokens = result.get('usage', {}).get('completion_tokens', 0)
        
        # 计算响应时间
        latency = time.time() - start_time
        
        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)
        
        # 元数据
        metadata = {
            'model': model,
            'provider': '百度智能云',
            'confidence': 0.95,
            'latency': latency,
            'token_count': {
                'prompt': prompt_tokens,
                'completion': completion_tokens
            },
            'success': True
        }
        
        return response_text, metadata
    
    async def _get_baidu_access_token(self, api_key, secret_key):
        """获取百度API访问令牌"""
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            response.raise_for_status()
            result = response.json()
            
            if "access_token" not in result:
                raise ValueError("无法获取百度API访问令牌")
                
            return result["access_token"]
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的模型列表
        
        Returns:
            List[Dict[str, Any]]: 可用模型列表
        """
        models = []
        for model_name, info in self.clients.items():
            models.append({
                'name': model_name,
                'provider': info['provider'],
                'max_tokens': info['max_tokens']
            })
        return models
    
    def is_model_available(self, model_name: str) -> bool:
        """
        检查模型是否可用
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 模型是否可用
        """
        return model_name in self.clients
    
    async def close(self):
        """关闭所有客户端连接"""
        # 目前大多数客户端不需要显式关闭
        logger.info("关闭所有模型客户端连接") 