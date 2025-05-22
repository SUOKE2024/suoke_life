#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译服务测试客户端
"""

import argparse
import asyncio
import logging
import os
import time
from typing import Optional, Iterator, AsyncIterator

import grpc
from google.protobuf.json_format import MessageToDict

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.grpc import accessibility_pb2 as pb2
from api.grpc import accessibility_pb2_grpc as pb2_grpc


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TranslationTestClient:
    """翻译服务测试客户端"""

    def __init__(self, host: str, port: int):
        """初始化客户端

        Args:
            host: 服务器地址
            port: 服务器端口
        """
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)
        logger.info(f"已连接到服务器: {host}:{port}")

    async def close(self):
        """关闭客户端连接"""
        await self.channel.close()
        logger.info("已关闭连接")

    async def test_speech_translation(self, audio_file: str, user_id: str,
                                     source_language: str, target_language: str,
                                     source_dialect: Optional[str] = None,
                                     target_dialect: Optional[str] = None) -> None:
        """测试语音翻译API

        Args:
            audio_file: 音频文件路径
            user_id: 用户ID
            source_language: 源语言代码
            target_language: 目标语言代码
            source_dialect: 源方言代码
            target_dialect: 目标方言代码
        """
        logger.info(f"测试语音翻译API: {source_language} → {target_language}")
        try:
            # 读取音频文件
            with open(audio_file, "rb") as f:
                audio_data = f.read()

            # 构建请求
            request = pb2.SpeechTranslationRequest(
                audio_data=audio_data,
                user_id=user_id,
                source_language=source_language,
                target_language=target_language
            )

            # 设置方言（如果提供）
            if source_dialect:
                request.source_dialect = source_dialect
            if target_dialect:
                request.target_dialect = target_dialect

            # 设置用户偏好
            preferences = pb2.UserPreferences(
                voice_type="female",
                speech_rate=1.0,
                language=target_language
            )
            request.preferences.CopyFrom(preferences)

            # 调用API
            start_time = time.time()
            response = await self.stub.SpeechTranslation(request)
            elapsed_time = time.time() - start_time

            # 输出结果
            logger.info(f"翻译请求完成，耗时: {elapsed_time:.2f}秒")
            logger.info(f"源文本: {response.source_text}")
            logger.info(f"翻译文本: {response.translated_text}")
            logger.info(f"源置信度: {response.source_confidence:.2f}")
            logger.info(f"翻译置信度: {response.translation_confidence:.2f}")
            logger.info(f"处理时间: {response.processing_time_ms}ms")

            # 保存翻译后的音频（如果有）
            if response.translated_audio:
                output_file = f"translated_{int(time.time())}.wav"
                with open(output_file, "wb") as f:
                    f.write(response.translated_audio)
                logger.info(f"翻译音频已保存到: {output_file}")

        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC错误: {e.code()} - {e.details()}")
        except Exception as e:
            logger.error(f"测试异常: {str(e)}", exc_info=True)

    async def test_streaming_translation(self, audio_file: str, user_id: str,
                                       source_language: str, target_language: str,
                                       source_dialect: Optional[str] = None,
                                       target_dialect: Optional[str] = None,
                                       chunk_size: int = 32000) -> None:
        """测试流式翻译API

        Args:
            audio_file: 音频文件路径
            user_id: 用户ID
            source_language: 源语言代码
            target_language: 目标语言代码
            source_dialect: 源方言代码
            target_dialect: 目标方言代码
            chunk_size: 音频块大小（字节）
        """
        logger.info(f"测试流式翻译API: {source_language} → {target_language}")
        try:
            # 读取音频文件
            with open(audio_file, "rb") as f:
                audio_data = f.read()

            # 创建配置
            config = pb2.TranslationConfig(
                source_language=source_language,
                target_language=target_language
            )

            # 设置方言（如果提供）
            if source_dialect:
                config.source_dialect = source_dialect
            if target_dialect:
                config.target_dialect = target_dialect

            # 设置用户偏好
            preferences = pb2.UserPreferences(
                voice_type="female",
                speech_rate=1.0,
                language=target_language
            )
            config.preferences.CopyFrom(preferences)

            # 分割音频数据为块
            chunks = [audio_data[i:i + chunk_size] for i in range(0, len(audio_data), chunk_size)]
            total_chunks = len(chunks)
            logger.info(f"音频已分割为 {total_chunks} 个块")

            # 创建会话ID
            session_id = f"test_session_{int(time.time())}"

            # 定义生成器函数
            async def request_generator() -> AsyncIterator[pb2.SpeechTranslationChunk]:
                for i, chunk in enumerate(chunks):
                    is_final = (i == total_chunks - 1)
                    
                    # 创建请求
                    request = pb2.SpeechTranslationChunk(
                        audio_chunk=chunk,
                        user_id=user_id,
                        session_id=session_id,
                        is_final=is_final
                    )
                    
                    # 只在第一个块中设置配置
                    if i == 0:
                        request.config.CopyFrom(config)
                    
                    yield request
                    logger.info(f"已发送块 {i+1}/{total_chunks}, 大小: {len(chunk)}字节")
                    
                    # 模拟流式处理的延迟
                    await asyncio.sleep(0.1)

            # 调用流式API
            start_time = time.time()
            responses = self.stub.StreamingSpeechTranslation(request_generator())
            
            # 处理响应
            segment_count = 0
            async for response in responses:
                segment_count += 1
                logger.info(f"收到翻译结果 #{segment_count}:")
                logger.info(f"  源文本: {response.source_text}")
                logger.info(f"  翻译文本: {response.translated_text}")
                logger.info(f"  是否最终结果: {response.is_final}")
                logger.info(f"  片段ID: {response.segment_id}")
                
                # 保存翻译后的音频（如果有）
                if response.translated_audio:
                    output_file = f"translated_stream_{session_id}_{response.segment_id}.wav"
                    with open(output_file, "wb") as f:
                        f.write(response.translated_audio)
                    logger.info(f"  翻译音频已保存到: {output_file}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"流式翻译请求完成，总耗时: {elapsed_time:.2f}秒，收到 {segment_count} 个结果")

        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC错误: {e.code()} - {e.details()}")
        except Exception as e:
            logger.error(f"测试异常: {str(e)}", exc_info=True)

    async def test_supported_languages(self, user_id: str, include_dialects: bool = True) -> None:
        """测试获取支持的语言API

        Args:
            user_id: 用户ID
            include_dialects: 是否包含方言信息
        """
        logger.info(f"测试获取支持的语言API: 包含方言={include_dialects}")
        try:
            # 构建请求
            request = pb2.SupportedLanguagesRequest(
                user_id=user_id,
                include_dialects=include_dialects
            )

            # 调用API
            response = await self.stub.GetSupportedLanguages(request)

            # 输出结果
            logger.info(f"支持的语言数量: {len(response.languages)}")
            for i, lang in enumerate(response.languages):
                logger.info(f"  语言 #{i+1}: {lang.name} ({lang.code}), 支持语音: {lang.supports_speech}")

            logger.info(f"支持的语言对数量: {len(response.language_pairs)}")
            for i, pair in enumerate(response.language_pairs[:5]):  # 只显示前5个
                logger.info(f"  语言对 #{i+1}: {pair.source_name} → {pair.target_name}, 支持语音: {pair.supports_speech}")
            
            if include_dialects:
                logger.info(f"支持的方言数量: {len(response.supported_dialects)}")
                for i, dialect in enumerate(response.supported_dialects):
                    logger.info(f"  方言 #{i+1}: {dialect}")

        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC错误: {e.code()} - {e.details()}")
        except Exception as e:
            logger.error(f"测试异常: {str(e)}", exc_info=True)


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="翻译服务测试客户端")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--port", type=int, default=50051, help="服务器端口")
    parser.add_argument("--audio", default="test.wav", help="测试音频文件路径")
    parser.add_argument("--user_id", default="test_user", help="用户ID")
    parser.add_argument("--source_lang", default="zh_CN", help="源语言代码")
    parser.add_argument("--target_lang", default="en_XX", help="目标语言代码")
    parser.add_argument("--source_dialect", help="源方言代码")
    parser.add_argument("--target_dialect", help="目标方言代码")
    parser.add_argument("--test", choices=["simple", "stream", "languages", "all"], default="all", help="测试类型")
    
    args = parser.parse_args()
    
    # 创建客户端
    client = TranslationTestClient(args.host, args.port)
    
    try:
        # 根据测试类型执行测试
        if args.test in ["simple", "all"]:
            logger.info("=== 测试简单翻译API ===")
            await client.test_speech_translation(
                args.audio, args.user_id, args.source_lang, args.target_lang,
                args.source_dialect, args.target_dialect
            )
        
        if args.test in ["stream", "all"]:
            logger.info("\n=== 测试流式翻译API ===")
            await client.test_streaming_translation(
                args.audio, args.user_id, args.source_lang, args.target_lang,
                args.source_dialect, args.target_dialect
            )
        
        if args.test in ["languages", "all"]:
            logger.info("\n=== 测试获取支持的语言API ===")
            await client.test_supported_languages(args.user_id)
    
    finally:
        # 关闭客户端
        await client.close()


if __name__ == "__main__":
    asyncio.run(main()) 