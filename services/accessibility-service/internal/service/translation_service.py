"""
实时语音翻译服务 - 提供多语言之间的实时语音翻译
"""

import logging
import time
import uuid
from typing import Any

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    MBartForConditionalGeneration,
    MBartTokenizer,
)

logger = logging.getLogger(__name__)


class TranslationService:
    """实时语音翻译服务 - 支持多语言和方言之间的实时语音翻译"""

    def __init__(self, config: dict[str, Any]):
        """初始化翻译服务

        Args:
            config: 应用配置对象
        """
        self.config = config
        logger.info("初始化语音翻译服务")

        # 服务依赖
        self.dialect_service = None  # 由主服务注入

        # 加载翻译模型
        self.translation_models = self._load_translation_models()

        # 支持的语言列表
        self.supported_languages = self._get_supported_languages()
        logger.info(f"支持的翻译语言数量: {len(self.supported_languages)}")

        # 活跃的翻译会话
        self.active_sessions = {}

    def _load_translation_models(self) -> dict[str, Any]:
        """加载翻译模型

        Returns:
            Dict[str, Any]: 翻译模型字典
        """
        models = {}
        try:
            logger.info("加载翻译模型")

            # 通用翻译模型 (多语言)
            model_name = (
                self.config.translation.model_name
                if hasattr(self.config, "translation")
                and hasattr(self.config.translation, "model_name")
                else "facebook/mbart-large-50-many-to-many-mmt"
            )
            logger.info(f"使用翻译模型: {model_name}")

            tokenizer = MBartTokenizer.from_pretrained(model_name)
            model = MBartForConditionalGeneration.from_pretrained(model_name)

            models["general"] = {"tokenizer": tokenizer, "model": model}

            # 特殊语言对的专用模型 (如中英翻译)
            # 这里可以根据需要加载其他专用模型
            special_pairs = (
                self.config.translation.special_pairs
                if hasattr(self.config, "translation")
                and hasattr(self.config.translation, "special_pairs")
                else {}
            )

            for pair, model_info in special_pairs.items():
                src, tgt = pair.split("-")
                logger.info(
                    f"加载专用翻译模型: {src}-{tgt}, 模型: {model_info['model_name']}"
                )

                special_tokenizer = AutoTokenizer.from_pretrained(
                    model_info["model_name"]
                )
                special_model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_info["model_name"]
                )

                models[pair] = {"tokenizer": special_tokenizer, "model": special_model}

            logger.info(f"成功加载 {len(models)} 个翻译模型")

        except Exception as e:
            logger.error(f"加载翻译模型失败: {e!s}", exc_info=True)
            # 加载失败时至少提供一个占位模型
            models["fallback"] = {"tokenizer": None, "model": None}

        return models

    def _get_supported_languages(self) -> list[dict[str, str]]:
        """获取支持的语言列表

        Returns:
            List[Dict[str, str]]: 支持的语言信息列表
        """
        # MBart-50支持的语言
        mbart_languages = {
            "ar_AR": "阿拉伯语",
            "cs_CZ": "捷克语",
            "de_DE": "德语",
            "en_XX": "英语",
            "es_XX": "西班牙语",
            "et_EE": "爱沙尼亚语",
            "fi_FI": "芬兰语",
            "fr_XX": "法语",
            "gu_IN": "古吉拉特语",
            "hi_IN": "印地语",
            "it_IT": "意大利语",
            "ja_XX": "日语",
            "kk_KZ": "哈萨克语",
            "ko_KR": "韩语",
            "lt_LT": "立陶宛语",
            "lv_LV": "拉脱维亚语",
            "my_MM": "缅甸语",
            "ne_NP": "尼泊尔语",
            "nl_XX": "荷兰语",
            "ro_RO": "罗马尼亚语",
            "ru_RU": "俄语",
            "si_LK": "僧伽罗语",
            "tr_TR": "土耳其语",
            "vi_VN": "越南语",
            "zh_CN": "中文",
        }

        # 构建完整的语言信息
        result = []
        for code, name in mbart_languages.items():
            language_info = {
                "code": code,
                "name": name,
                "supports_speech": self._check_speech_support(code),
            }
            result.append(language_info)

        return result

    def _check_speech_support(self, language_code: str) -> bool:
        """检查语言是否支持语音转写和合成

        Args:
            language_code: 语言代码

        Returns:
            bool: 是否支持语音
        """
        # 这里应该根据实际支持的语音语言进行检查
        # 简化实现，假设部分语言支持语音
        supported_speech_languages = [
            "en_XX",
            "zh_CN",
            "ja_XX",
            "ko_KR",
            "fr_XX",
            "de_DE",
            "es_XX",
            "ru_RU",
            "ar_AR",
            "hi_IN",
        ]
        return language_code in supported_speech_languages

    def _get_model_for_language_pair(
        self, source_lang: str, target_lang: str
    ) -> dict[str, Any]:
        """根据语言对获取合适的翻译模型

        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码

        Returns:
            Dict[str, Any]: 翻译模型信息
        """
        # 检查是否有专用的语言对模型
        pair_key = f"{source_lang}-{target_lang}"
        if pair_key in self.translation_models:
            return self.translation_models[pair_key]

        # 使用通用模型
        if "general" in self.translation_models:
            return self.translation_models["general"]

        # 使用任何可用模型
        if self.translation_models:
            return next(iter(self.translation_models.values()))

        # 无可用模型
        logger.error(f"没有找到适用于 {source_lang} → {target_lang} 的翻译模型")
        return None

    def translate_speech(
        self,
        audio_data: bytes,
        source_language: str,
        target_language: str,
        source_dialect: str | None = None,
        target_dialect: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """语音翻译主功能：语音 → 文本 → 翻译 → 语音

        Args:
            audio_data: 语音数据
            source_language: 源语言代码
            target_language: 目标语言代码
            source_dialect: 源方言代码
            target_dialect: 目标方言代码
            preferences: 用户偏好设置

        Returns:
            Dict[str, Any]: 翻译结果，包含源文本、翻译文本和翻译语音
        """
        start_time = time.time()
        logger.info(f"处理语音翻译请求: {source_language} → {target_language}")

        try:
            # 1. 语音识别(ASR) - 使用方言服务或回退到标准ASR
            recognized_text = ""
            if source_dialect and self.dialect_service:
                # 使用方言服务进行语音识别
                transcription_result = self.dialect_service.transcribe_with_dialect(
                    audio_data, source_dialect
                )
                recognized_text = transcription_result.get("text", "")
                source_confidence = transcription_result.get("confidence", 0.0)
                logger.info(
                    f"方言识别结果: {recognized_text[:30]}... (置信度: {source_confidence:.2f})"
                )
            else:
                # 这里应该使用通用ASR模型
                # 由于这是示例代码，我们使用占位实现
                recognized_text = "这是示例语音识别文本"
                source_confidence = 0.9
                logger.info(f"标准语音识别结果: {recognized_text[:30]}...")

            if not recognized_text:
                raise ValueError("无法识别语音内容")

            # 2. 文本翻译
            translated_text = self.translate_text(
                recognized_text, source_language, target_language
            )
            if not translated_text:
                raise ValueError("翻译失败")

            # 3. 语音合成(TTS)
            translated_audio = b""
            if target_dialect and self.dialect_service:
                # 使用方言服务进行语音合成
                voice_type = (
                    preferences.get("voice_type", "default")
                    if preferences
                    else "default"
                )
                tts_result = self.dialect_service.synthesize_speech_with_dialect(
                    translated_text, target_dialect, voice_type
                )
                translated_audio = tts_result.get("audio_data", b"")
                logger.info(f"方言语音合成完成: {target_dialect}")
            else:
                # 这里应该使用通用TTS模型
                # 由于这是示例代码，我们使用占位实现
                translated_audio = b"audio_placeholder"
                logger.info("标准语音合成完成")

            processing_time = time.time() - start_time
            logger.info(f"翻译处理完成，耗时: {processing_time:.2f}秒")

            # 4. 返回结果
            return {
                "source_text": recognized_text,
                "translated_text": translated_text,
                "translated_audio": translated_audio,
                "source_confidence": source_confidence,
                "translation_confidence": 0.9,  # 示例值，实际应该从翻译模型获取
                "processing_time_ms": int(processing_time * 1000),
            }

        except Exception as e:
            logger.error(f"语音翻译失败: {e!s}", exc_info=True)
            return {
                "error": str(e),
                "source_text": "",
                "translated_text": "",
                "translated_audio": b"",
                "source_confidence": 0.0,
                "translation_confidence": 0.0,
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

    def translate_text(
        self, text: str, source_language: str, target_language: str
    ) -> str:
        """文本翻译功能

        Args:
            text: 源文本
            source_language: 源语言代码
            target_language: 目标语言代码

        Returns:
            str: 翻译后的文本
        """
        logger.info(f"文本翻译: {source_language} → {target_language}")

        # 获取适合的翻译模型
        translation_model = self._get_model_for_language_pair(
            source_language, target_language
        )
        if not translation_model or not translation_model["model"]:
            logger.warning("未找到合适的翻译模型，使用模拟翻译")
            return self._mock_translate(text, source_language, target_language)

        try:
            # 使用transformers进行翻译
            tokenizer = translation_model["tokenizer"]
            model = translation_model["model"]

            # 设置适当的语言标记
            tokenizer.src_lang = source_language

            # 编码输入文本
            encoded = tokenizer(text, return_tensors="pt")

            # 生成翻译
            with torch.no_grad():
                generated_tokens = model.generate(
                    **encoded,
                    forced_bos_token_id=tokenizer.lang_code_to_id[target_language],
                    max_length=128,
                    num_beams=4,
                    length_penalty=0.6,
                    early_stopping=True,
                )

            # 解码生成的token
            translated_text = tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]
            logger.info(f"翻译完成: {text[:20]}... → {translated_text[:20]}...")

            return translated_text

        except Exception as e:
            logger.error(f"翻译过程出错: {e!s}", exc_info=True)
            # 回退到模拟翻译
            return self._mock_translate(text, source_language, target_language)

    def _mock_translate(
        self, text: str, source_language: str, target_language: str
    ) -> str:
        """模拟翻译（用于开发和测试）

        Args:
            text: 源文本
            source_language: 源语言代码
            target_language: 目标语言代码

        Returns:
            str: 翻译后的文本
        """
        # 提供一些固定的测试翻译
        translation_samples = {
            "zh_CN-en_XX": {
                "我需要看医生": "I need to see a doctor",
                "我的头很痛": "I have a headache",
                "请问附近有药店吗": "Is there a pharmacy nearby?",
                "我想了解痰湿体质的特点": "I want to know the characteristics of phlegm-dampness constitution",
            },
            "en_XX-zh_CN": {
                "I need to see a doctor": "我需要看医生",
                "I have a headache": "我的头很痛",
                "Is there a pharmacy nearby?": "请问附近有药店吗",
                "I want to know the characteristics of phlegm-dampness constitution": "我想了解痰湿体质的特点",
            },
        }

        # 获取样本词典
        pair_key = f"{source_language}-{target_language}"
        if pair_key in translation_samples and text in translation_samples[pair_key]:
            return translation_samples[pair_key][text]

        # 如果没有精确匹配，添加标记指示翻译
        return f"[{target_language}]{text}"

    def create_streaming_session(
        self,
        user_id: str,
        source_language: str,
        target_language: str,
        source_dialect: str | None = None,
        target_dialect: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> str:
        """创建流式翻译会话

        Args:
            user_id: 用户ID
            source_language: 源语言代码
            target_language: 目标语言代码
            source_dialect: 源方言代码
            target_dialect: 目标方言代码
            preferences: 用户偏好设置

        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())

        # 创建会话
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "source_language": source_language,
            "target_language": target_language,
            "source_dialect": source_dialect,
            "target_dialect": target_dialect,
            "preferences": preferences,
            "created_at": time.time(),
            "last_activity": time.time(),
            "audio_buffer": b"",
            "text_buffer": "",
            "segments": [],
            "is_active": True,
        }

        logger.info(
            f"创建流式翻译会话: {session_id}, 用户: {user_id}, 语言: {source_language} → {target_language}"
        )
        return session_id

    def process_streaming_chunk(
        self, session_id: str, audio_chunk: bytes, is_final: bool = False
    ) -> dict[str, Any] | None:
        """处理流式翻译的音频数据块

        Args:
            session_id: 会话ID
            audio_chunk: 音频数据块
            is_final: 是否为最后一块

        Returns:
            Optional[Dict[str, Any]]: 处理结果
        """
        if session_id not in self.active_sessions:
            logger.warning(f"未找到会话: {session_id}")
            return None

        session = self.active_sessions[session_id]
        session["last_activity"] = time.time()

        # 累积音频数据
        session["audio_buffer"] += audio_chunk

        # 如果是最后一块或者积累了足够的数据，进行处理
        if is_final or len(session["audio_buffer"]) >= 32000:  # 约2秒的16kHz 16-bit音频
            result = self._process_audio_buffer(session)

            # 如果是最后一块，清理会话
            if is_final:
                session["is_active"] = False
                # 不立即删除会话，以便客户端可以查询最终结果
                # 实际实现可以添加定时清理任务

            return result

        return None

    def _process_audio_buffer(self, session: dict[str, Any]) -> dict[str, Any]:
        """处理会话中的音频缓冲区

        Args:
            session: 会话信息

        Returns:
            Dict[str, Any]: 处理结果
        """
        audio_data = session["audio_buffer"]
        source_language = session["source_language"]
        target_language = session["target_language"]
        source_dialect = session.get("source_dialect")
        target_dialect = session.get("target_dialect")
        preferences = session.get("preferences", {})

        # 使用完整的翻译流程处理音频
        result = self.translate_speech(
            audio_data,
            source_language,
            target_language,
            source_dialect,
            target_dialect,
            preferences,
        )

        # 生成段ID
        segment_id = str(len(session["segments"]) + 1)

        # 添加结果到会话
        segment_result = {
            "segment_id": segment_id,
            "source_text": result.get("source_text", ""),
            "translated_text": result.get("translated_text", ""),
            "translated_audio": result.get("translated_audio", b""),
            "timestamp": time.time(),
            "is_final": True,
        }

        session["segments"].append(segment_result)

        # 重置音频缓冲区
        session["audio_buffer"] = b""

        # 累积文本，便于后续上下文处理
        if result.get("source_text"):
            if session["text_buffer"]:
                session["text_buffer"] += " " + result["source_text"]
            else:
                session["text_buffer"] = result["source_text"]

        return segment_result

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """获取会话状态

        Args:
            session_id: 会话ID

        Returns:
            Dict[str, Any]: 会话状态
        """
        if session_id not in self.active_sessions:
            return {"error": "session_not_found"}

        session = self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "source_language": session["source_language"],
            "target_language": session["target_language"],
            "is_active": session["is_active"],
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "segment_count": len(session["segments"]),
            "duration_seconds": time.time() - session["created_at"],
        }

    def get_supported_language_pairs(self) -> list[dict[str, str]]:
        """获取支持的语言对

        Returns:
            List[Dict[str, str]]: 支持的语言对列表
        """
        language_pairs = []

        # 生成所有可能的语言对组合
        for source in self.supported_languages:
            for target in self.supported_languages:
                if source["code"] != target["code"]:
                    pair = {
                        "source_code": source["code"],
                        "source_name": source["name"],
                        "target_code": target["code"],
                        "target_name": target["name"],
                        "supports_speech": source["supports_speech"]
                        and target["supports_speech"],
                    }
                    language_pairs.append(pair)

        return language_pairs

    def cleanup_inactive_sessions(self, max_age_seconds: int = 3600) -> int:
        """清理不活跃的会话

        Args:
            max_age_seconds: 最大会话寿命（秒）

        Returns:
            int: 清理的会话数量
        """
        now = time.time()
        to_remove = []

        for session_id, session in self.active_sessions.items():
            # 检查会话是否超过最大寿命或者不活跃且已完成
            if now - session["created_at"] > max_age_seconds or (
                not session["is_active"] and now - session["last_activity"] > 300
            ):
                to_remove.append(session_id)

        # 删除过期会话
        for session_id in to_remove:
            del self.active_sessions[session_id]

        logger.info(f"清理了 {len(to_remove)} 个不活跃的翻译会话")
        return len(to_remove)
