#!/usr/bin/env python

"""
LLM客户端模块，负责与大语言模型交互，生成问诊响应
"""

import json
import logging
import os
import time
from typing import Any

# 条件导入aiohttp和httpx
try:
    import aiohttp

    EXTERNAL_LIBS_AVAILABLE = True
except ImportError:
    EXTERNAL_LIBS_AVAILABLE = False
    logging.warning("aiohttp或httpx库未安装，LLM客户端将仅在Mock模式下工作")

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM客户端类，负责与大语言模型交互"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化LLM客户端

        Args:
            config: 配置信息
        """
        self.config = config
        self.llm_config = config.get("llm", {})

        # LLM配置
        self.model_type = self.llm_config.get("model_type", "llama3")
        self.temperature = self.llm_config.get("temperature", 0.7)
        self.top_p = self.llm_config.get("top_p", 0.95)
        self.response_max_tokens = self.llm_config.get("response_max_tokens", 1024)
        self.context_window = self.llm_config.get("context_window", 8192)
        self.timeout_seconds = self.llm_config.get("timeout_seconds", 30)

        # 系统提示词
        self.system_prompt_path = self.llm_config.get("system_prompt_path", "")
        self.system_prompt = self._load_system_prompt()

        # 默认使用mock模式，避免外部依赖
        self.use_mock_mode = self.llm_config.get("use_mock_mode", True)

        # 推理模式配置（只有在非mock模式下才会实际使用）
        self.local_inference = False
        self.local_model_path = ""
        self.remote_endpoint = ""

        # 只有在不使用mock模式时，才加载这些配置
        if not self.use_mock_mode:
            self.local_inference = self.llm_config.get("local_inference", True)
            self.local_model_path = self.llm_config.get("local_model_path", "")
            self.remote_endpoint = self.llm_config.get("remote_endpoint", "")

            # 接口配置
            self.api_key = os.environ.get("LLM_API_KEY", "")

            # 模型加载（本地推理模式）
            self.model = None
            self.tokenizer = None
            if self.local_inference and self.local_model_path:
                self._load_local_model()

        logger.info(
            f"LLM客户端初始化完成，模型类型: {self.model_type}, 使用Mock模式: {self.use_mock_mode}"
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本响应（兼容测试）
        
        Args:
            prompt: 输入提示词
            **kwargs: 其他参数
            
        Returns:
            生成的文本响应
        """
        if self.use_mock_mode:
            return self._get_fallback_response(prompt)
        
        # 构建请求
        request = {
            "history": [{"role": "user", "content": prompt}],
            "user_profile": kwargs.get("user_profile", {})
        }
        
        # 调用主要生成方法
        response = await self.generate_response(request)
        return response.get("response_text", "")

    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        try:
            if self.system_prompt_path and os.path.exists(self.system_prompt_path):
                with open(self.system_prompt_path, encoding="utf-8") as file:
                    return file.read()
            else:
                # 使用默认提示词
                return """你是索克生活APP的健康顾问，专注于中医问诊。以四诊合参理念为基础，通过问诊理解用户症状，
提供专业、准确而有温度的健康建议。请根据用户描述，提取相关症状信息，并在回答中注意以下几点：
1. 保持专业：基于中医理论回答问题，但避免使用过于专业的术语
2. 有同理心：理解用户的健康困扰，提供温暖支持
3. 注重个性化：根据用户的具体情况给出量身定制的建议
4. 提取症状：准确识别用户描述中的症状，并记录在返回数据中
5. 适当追问：当信息不足时，提出有针对性的跟进问题
记住，你不是在替代医生诊断或治疗，而是帮助用户理解自己的健康状况，并在必要时建议就医。"""
        except Exception as e:
            logger.error(f"加载系统提示词失败: {e!s}")
            return """你是索克生活APP的健康顾问，专注于中医问诊，帮助用户理解自己的症状和健康状况。"""

    def _load_local_model(self):
        """加载本地模型（如果使用本地推理）"""
        if not self.local_inference:
            return

        try:
            # 根据不同模型类型加载
            if self.model_type == "llama3":
                # 使用transformers库加载模型
                try:
                    from transformers import AutoModelForCausalLM, AutoTokenizer

                    logger.info(f"正在加载本地模型: {self.local_model_path}")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.local_model_path
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.local_model_path,
                        device_map="auto",
                        torch_dtype="auto",
                        trust_remote_code=True,
                    )
                    logger.info("本地模型加载成功")
                except ImportError:
                    logger.error("未安装transformers库，无法加载本地模型")
                    self.local_inference = False
                except Exception as e:
                    logger.error(f"加载本地模型失败: {e!s}")
                    self.local_inference = False

            elif self.model_type == "glm":
                # ChatGLM模型加载
                try:
                    from transformers import AutoModel, AutoTokenizer

                    logger.info(f"正在加载ChatGLM模型: {self.local_model_path}")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.local_model_path, trust_remote_code=True
                    )
                    self.model = AutoModel.from_pretrained(
                        self.local_model_path, trust_remote_code=True, device_map="auto"
                    )
                    logger.info("ChatGLM模型加载成功")
                except ImportError:
                    logger.error("未安装必要的库，无法加载ChatGLM模型")
                    self.local_inference = False
                except Exception as e:
                    logger.error(f"加载ChatGLM模型失败: {e!s}")
                    self.local_inference = False

            else:
                logger.warning(f"不支持的模型类型: {self.model_type}，将使用远程推理")
                self.local_inference = False

        except Exception as e:
            logger.error(f"初始化本地模型失败: {e!s}")
            self.local_inference = False

    async def generate_response(self, request: dict) -> dict:
        """
        生成问诊响应

        Args:
            request: 包含会话历史、用户ID、会话ID等信息的请求

        Returns:
            Dict: 包含回复文本、回复类型、检测到的症状等信息
        """
        start_time = time.time()

        try:
            # 准备推理输入
            history = request.get("history", [])
            user_profile = request.get("user_profile", {})

            # 构建提示词
            prompt = self._build_prompt(history, user_profile)

            # 如果使用mock模式，直接返回备用响应
            if self.use_mock_mode:
                raw_response = self._get_fallback_response(prompt)
                parsed_response = self._parse_response(raw_response)

                latency = time.time() - start_time
                logger.info(f"LLM响应生成完成(Mock模式)，耗时: {latency:.2f}秒")

                return parsed_response

            # 获取响应
            if self.local_inference and self.model is not None:
                # 本地模型推理
                raw_response = await self._generate_local(prompt)
            else:
                # 远程API调用
                raw_response = await self._generate_remote(prompt)

            # 解析响应
            parsed_response = self._parse_response(raw_response)

            # 记录延迟
            latency = time.time() - start_time
            logger.info(f"LLM响应生成完成，耗时: {latency:.2f}秒")

            return parsed_response

        except Exception as e:
            logger.error(f"生成LLM响应失败: {e!s}")
            latency = time.time() - start_time
            logger.warning(f"LLM响应生成失败，耗时: {latency:.2f}秒")

            # 返回一个简单的错误响应
            return {
                "response_text": "抱歉，我暂时无法处理您的请求，请稍后再试。",
                "response_type": "TEXT",
                "detected_symptoms": [],
                "follow_up_questions": [
                    "您能换个方式描述您的问题吗？",
                    "您可以尝试问一些其他问题。",
                ],
            }

    def _build_prompt(self, history: list[dict], user_profile: dict) -> str:
        """构建提示词"""
        # 构建系统提示词
        system_prompt = self.system_prompt

        # 添加用户画像信息
        user_info = ""
        if user_profile:
            user_info += "用户信息：\n"
            if "constitution_type" in user_profile:
                constitution_map = {
                    "BALANCED": "平和质",
                    "QI_DEFICIENCY": "气虚质",
                    "YANG_DEFICIENCY": "阳虚质",
                    "YIN_DEFICIENCY": "阴虚质",
                    "PHLEGM_DAMPNESS": "痰湿质",
                    "DAMP_HEAT": "湿热质",
                    "BLOOD_STASIS": "血瘀质",
                    "QI_STAGNATION": "气郁质",
                    "SPECIAL_CONSTITUTION": "特禀质",
                }
                constitution = constitution_map.get(
                    user_profile.get("constitution_type"), "未知体质"
                )
                user_info += f"- 体质类型：{constitution}\n"

            if "common_patterns" in user_profile:
                common_patterns = user_profile.get("common_patterns", [])
                if common_patterns:
                    pattern_names = [p.get("pattern_name", "") for p in common_patterns]
                    user_info += f"- 常见证型：{', '.join(pattern_names)}\n"

            if "lifestyle" in user_profile:
                lifestyle = user_profile.get("lifestyle", {})
                if "dietary_habits" in lifestyle:
                    dietary = lifestyle.get("dietary_habits", {})
                    preferences = dietary.get("preferences", [])
                    if preferences:
                        user_info += f"- 饮食偏好：{', '.join(preferences[:3])}\n"

                if "emotional_tendency" in lifestyle:
                    emotions = lifestyle.get("emotional_tendency", {}).get(
                        "dominant_emotions", []
                    )
                    if emotions:
                        user_info += f"- 情绪倾向：{', '.join(emotions[:2])}\n"

            if "health_goals" in user_profile:
                goals = user_profile.get("health_goals", [])
                if goals:
                    user_info += f"- 健康目标：{', '.join(goals[:2])}\n"

        # 构建对话历史
        chat_history = ""
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                chat_history += f"用户：{content}\n"
            elif role == "system":
                chat_history += f"健康顾问：{content}\n"

        # 组装最终提示词
        final_prompt = f"{system_prompt}\n\n"

        if user_info:
            final_prompt += f"{user_info}\n"

        final_prompt += f"对话历史：\n{chat_history}\n"
        final_prompt += "健康顾问："

        return final_prompt

    async def _generate_local(self, prompt: str) -> str:
        """使用本地模型生成回复"""
        try:
            # 如果模型或者tokenizer未加载，直接使用备用响应
            if self.model is None or self.tokenizer is None:
                logger.warning("本地模型未加载，使用备用响应")
                return self._get_fallback_response(prompt)

            if self.model_type == "llama3":
                try:
                    import torch

                    # 编码输入
                    inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(
                        self.model.device
                    )

                    # 生成输出
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs,
                            max_new_tokens=self.response_max_tokens,
                            do_sample=True,
                            temperature=self.temperature,
                            top_p=self.top_p,
                            pad_token_id=self.tokenizer.eos_token_id,
                        )

                    # 解码输出
                    response = self.tokenizer.decode(
                        outputs[0][inputs.shape[1] :], skip_special_tokens=True
                    )

                    return response
                except ImportError:
                    logger.warning("torch库未安装，无法使用本地模型，使用备用响应")
                    return self._get_fallback_response(prompt)

            elif self.model_type == "glm":
                try:
                    # ChatGLM模型生成
                    response, _ = self.model.chat(self.tokenizer, prompt, history=[])
                    return response
                except Exception as e:
                    logger.error(f"ChatGLM模型推理失败: {e!s}")
                    return self._get_fallback_response(prompt)

            else:
                logger.warning(f"不支持的模型类型: {self.model_type}，使用备用响应")
                return self._get_fallback_response(prompt)

        except Exception as e:
            logger.error(f"本地模型推理失败: {e!s}")
            return self._get_fallback_response(prompt)

    async def _generate_remote(self, prompt: str) -> str:
        """调用远程API生成回复"""
        try:
            # 检查是否有外部依赖库
            if not EXTERNAL_LIBS_AVAILABLE:
                logger.error("无法调用远程API，因为aiohttp或httpx库未安装")
                return self._get_fallback_response(prompt)

            # 检查是否有配置远程端点
            if not self.remote_endpoint:
                logger.warning("未配置远程API端点，使用备用响应")
                return self._get_fallback_response(prompt)

            # 准备OpenAI API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            # 构建请求体
            payload = {
                "model": "gpt-4" if self.model_type == "gpt4" else "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.response_max_tokens,
                "top_p": self.top_p,
                "stream": False,
            }

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.remote_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # 提取回复内容
                        if "choices" in result and len(result["choices"]) > 0:
                            message = result["choices"][0].get("message", {})
                            content = message.get("content", "")
                            return content
                        else:
                            logger.error(f"API响应格式错误: {result}")
                            return self._get_fallback_response(prompt)
                    else:
                        error_text = await response.text()
                        logger.error(f"API调用失败: {response.status}, {error_text}")
                        return self._get_fallback_response(prompt)

        except NameError:
            logger.error("无法调用远程API，因为aiohttp或httpx库未安装")
            return self._get_fallback_response(prompt)
        except Exception as e:
            # 更通用的异常处理，不依赖于aiohttp
            if "ClientError" in str(type(e)):
                logger.error(f"API请求失败: {e!s}")
            elif "TimeoutError" in str(type(e)):
                logger.error("API请求超时")
            else:
                logger.error(f"远程API调用未知错误: {e!s}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """获取备用回复"""
        # 智能化的备用回复逻辑
        response_data = {}

        if "头痛" in prompt:
            response_text = "您好，您提到的头痛症状可能与多种因素有关。从中医角度看，头痛可能与肝阳上亢、风邪犯表或痰浊上扰等证型相关。建议您关注以下几点：\n\n1. 规律作息，避免熬夜和过度疲劳\n2. 饮食清淡，多喝水，少吃辛辣刺激食物\n3. 适当放松，减轻精神压力\n4. 可以按摩太阳穴和风池穴缓解症状\n\n请问您的头痛是持续性的还是间歇性的？头痛部位在哪里？是否伴有其他症状如眩晕、耳鸣等？"
            response_data = {
                "response_text": response_text,
                "detected_symptoms": ["头痛"],
                "response_type": "SYMPTOM_CONFIRMATION",
                "follow_up_questions": [
                    "您的头痛是持续性的还是间歇性的？",
                    "头痛部位在哪里？",
                    "是否伴有眩晕、耳鸣等症状？",
                ],
            }
        elif "失眠" in prompt:
            response_text = "关于您提到的失眠问题，从中医角度看可能与心神不安、肝郁化火或阴虚内热等证型有关。建议您尝试以下调理方法：\n\n1. 保持规律作息，固定睡眠时间\n2. 睡前避免使用电子产品，减少蓝光刺激\n3. 睡前可以泡脚或喝一杯温热的牛奶，帮助安神\n4. 白天适当运动，但避免睡前剧烈运动\n5. 保持良好心态，避免过度焦虑\n\n您的失眠主要表现为难以入睡、易醒，还是早醒？是否有心烦、口干等伴随症状？"
            response_data = {
                "response_text": response_text,
                "detected_symptoms": ["失眠"],
                "response_type": "RECOMMENDATION",
                "follow_up_questions": [
                    "您的失眠主要表现为难以入睡、易醒，还是早醒？",
                    "是否有心烦、口干等伴随症状？",
                ],
            }
        elif "胃痛" in prompt:
            response_text = "您提到的胃痛问题，从中医角度可能与脾胃虚弱、肝气犯胃或胃寒等证型有关。针对胃痛，建议您注意以下几点：\n\n1. 规律饮食，避免暴饮暴食\n2. 注意饮食温度，避免过冷或过热食物\n3. 减少辛辣刺激性食物的摄入\n4. 保持良好情绪，避免过度紧张和焦虑\n5. 可以用热敷腹部缓解不适\n\n请问您的胃痛是持续性还是间歇性的？是否与进食有关？是否伴有反酸、嗳气等症状？"
            response_data = {
                "response_text": response_text,
                "detected_symptoms": ["胃痛"],
                "response_type": "RECOMMENDATION",
                "follow_up_questions": [
                    "您的胃痛是持续性还是间歇性的？",
                    "是否与进食有关？",
                    "是否伴有反酸、嗳气等症状？",
                ],
            }
        elif "腰痛" in prompt:
            response_text = "您好，腰痛在中医看来可能与肾虚、寒湿或气滞血瘀等证型相关。根据您的描述，我建议您：\n\n1. 注意腰部保暖，避免受凉\n2. 维持正确姿势，避免长时间久坐或重体力劳动\n3. 适当进行腰部保健运动，如八段锦中的'两手托天理三焦'\n4. 保证充足睡眠，避免过度劳累\n\n您的腰痛是刺痛、酸痛还是跳痛？疼痛是持续性的还是活动后加重？"
            response_data = {
                "response_text": response_text,
                "detected_symptoms": ["腰痛"],
                "response_type": "RECOMMENDATION",
                "follow_up_questions": [
                    "您的腰痛是刺痛、酸痛还是跳痛？",
                    "疼痛是持续性的还是活动后加重？",
                ],
            }
        else:
            response_text = "您好，感谢您的咨询。为了更好地了解您的健康状况并提供针对性的建议，我需要了解更多信息。\n\n请问您目前有哪些不适症状？这些症状持续了多长时间？平时有什么生活习惯可能与您的症状有关？比如作息、饮食、运动情况等。\n\n越详细的描述，我就能提供越准确的健康建议。"
            response_data = {
                "response_text": response_text,
                "detected_symptoms": [],
                "response_type": "INFO_REQUEST",
                "follow_up_questions": [
                    "您目前有哪些不适症状？",
                    "这些症状持续了多长时间？",
                    "您的日常生活习惯如何？",
                ],
            }

        # 返回JSON字符串
        return json.dumps(response_data)

    def _parse_response(self, raw_response: str) -> dict:
        """解析LLM回复，提取回复文本、回复类型、检测到的症状等"""
        try:
            # 检查是否是JSON格式
            if raw_response.strip().startswith("{") and raw_response.strip().endswith(
                "}"
            ):
                try:
                    parsed_json = json.loads(raw_response)

                    # 提取字段
                    response_text = parsed_json.get("response", "")
                    response_type = parsed_json.get("type", "TEXT")
                    detected_symptoms = parsed_json.get("symptoms", [])
                    follow_up_questions = parsed_json.get("follow_up_questions", [])

                    return {
                        "response_text": response_text,
                        "response_type": response_type,
                        "detected_symptoms": detected_symptoms,
                        "follow_up_questions": follow_up_questions,
                    }
                except json.JSONDecodeError:
                    # 不是有效的JSON，按普通文本处理
                    pass

            # 普通文本处理
            # 尝试从文本中提取症状信息
            detected_symptoms = self._extract_symptoms_from_text(raw_response)

            # 尝试从文本中提取跟进问题
            follow_up_questions = self._extract_follow_up_questions(raw_response)

            # 确定响应类型
            response_type = self._determine_response_type(raw_response)

            return {
                "response_text": raw_response,
                "response_type": response_type,
                "detected_symptoms": detected_symptoms,
                "follow_up_questions": follow_up_questions,
            }

        except Exception as e:
            logger.error(f"解析LLM回复失败: {e!s}")
            return {
                "response_text": raw_response,
                "response_type": "TEXT",
                "detected_symptoms": [],
                "follow_up_questions": [],
            }

    def _extract_symptoms_from_text(self, text: str) -> list[str]:
        """从文本中提取症状信息"""
        # 简单实现，仅基于关键词匹配
        # 实际应用中应使用更复杂的NER模型提取
        symptoms = []

        # 常见症状关键词
        symptom_keywords = [
            "疲劳",
            "乏力",
            "头痛",
            "头晕",
            "失眠",
            "心悸",
            "胸闷",
            "咳嗽",
            "咳痰",
            "气短",
            "胃痛",
            "腹痛",
            "腹泻",
            "便秘",
            "口干",
            "口苦",
            "口臭",
            "恶心",
            "呕吐",
            "食欲不振",
            "潮热",
            "盗汗",
            "手脚冰凉",
            "浮肿",
            "尿频",
            "尿急",
            "腰酸",
            "腰痛",
            "关节疼痛",
            "肌肉酸痛",
            "麻木",
            "刺痛",
            "瘙痒",
            "皮疹",
            "多梦",
            "健忘",
            "焦虑",
            "抑郁",
            "烦躁",
            "痰多",
            "舌苔厚",
            "舌苔白",
            "舌苔黄",
            "舌质红",
            "舌质淡",
        ]

        # 简单的关键词匹配
        for keyword in symptom_keywords:
            if keyword in text:
                symptoms.append(keyword)

        return symptoms[:10]  # 限制返回数量

    def _extract_follow_up_questions(self, text: str) -> list[str]:
        """从文本中提取跟进问题"""
        questions = []

        # 分行并检查每一行是否是问题
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # 检查是否以问号结尾或包含问句关键词
            if ((line.endswith("？") or line.endswith("?")) and len(line) > 5) or (
                "您" in line and ("吗" in line or "呢" in line) and len(line) > 5
            ):
                questions.append(line)

        # 如果没有明确问题，尝试生成一些通用的跟进问题
        if not questions:
            general_questions = [
                "您还有其他不适症状吗？",
                "这种情况持续多久了？",
                "除了这些症状，您的饮食和睡眠情况如何？",
            ]

            # 随机选择1-2个通用问题
            import random

            num_questions = min(2, len(general_questions))
            return random.sample(general_questions, num_questions)

        return questions[:3]  # 限制返回数量

    def _determine_response_type(self, text: str) -> str:
        """确定响应类型"""
        # 简单的启发式判断
        # 检查是否包含问句
        if "?" in text or "？" in text:
            # 如果文本较短且主要是问题，则为跟进问题
            if len(text) < 100 and (text.count("?") + text.count("？")) > 0:
                return "FOLLOW_UP_QUESTION"

        # 检查是否是症状确认
        symptom_confirmation_keywords = [
            "您是否有",
            "您是不是有",
            "您提到的",
            "您所说的症状",
        ]
        for keyword in symptom_confirmation_keywords:
            if keyword in text:
                return "SYMPTOM_CONFIRMATION"

        # 检查是否是建议
        recommendation_keywords = ["建议您", "我建议", "您可以尝试", "您应该"]
        for keyword in recommendation_keywords:
            if keyword in text:
                return "RECOMMENDATION"

        # 检查是否是信息请求
        info_request_keywords = ["能否告诉我", "请您描述", "您能详细说明", "需要了解"]
        for keyword in info_request_keywords:
            if keyword in text:
                return "INFO_REQUEST"

        # 默认为普通文本
        return "TEXT"
