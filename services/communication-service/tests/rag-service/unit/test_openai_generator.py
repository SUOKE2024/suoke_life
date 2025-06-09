from typing import Dict, List, Any, Optional, Union

"""
test_openai_generator - 索克生活项目模块
"""

from services.rag_service.internal.generator.openai_generator import OpenAIGenerator
from services.rag_service.internal.model.document import Document, DocumentReference, GenerateResult
from unittest.mock import AsyncMock, MagicMock, patch
import json
import pytest
import unittest

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
OpenAI生成器单元测试
"""




class TestOpenAIGenerator(unittest.TestCase):
    """OpenAI生成器单元测试类"""

    def setUp(self) - > None:
        """设置测试环境"""
        self.mock_openai_client = MagicMock()
        self.mock_cache_service = AsyncMock()

        # 模拟OpenAI响应
        mock_completion = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "这是由AI生成的回答，参考了文档1和文档2。"

        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "get_references"
        mock_tool_call.function.arguments = json.dumps({
            "references": [
                {
                    "id": "doc1",
                    "title": "测试文档1",
                    "source": "测试源1",
                    "url": "http: / /test1.com",
                    "snippet": "文档1片段"
                },
                {
                    "id": "doc2",
                    "title": "测试文档2",
                    "source": "测试源2",
                    "url": "http: / /test2.com",
                    "snippet": "文档2片段"
                }
            ]
        })

        mock_message.tool_calls = [mock_tool_call]
        mock_completion.choices = [MagicMock(message = mock_message)]
        self.mock_openai_client.chat.completions.create.return_value = mock_completion

        # 配置参数
        self.config = {
            "generator": {
                "openai": {
                    "model": "gpt - 3.5 - turbo",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                "local_fallback": True,
                "cache_ttl": 3600,
                "system_prompt_template": "你是一个专业医疗顾问，请回答以下问题：\n\n{context}\n\n问题：{query}"
            }
        }

        # 测试文档
        self.test_documents = [
            Document(
                id = "doc1",
                content = "文档1的内容，包含一些医学知识。",
                metadata = {"source": "测试源1"},
                score = 0.9
            ),
            Document(
                id = "doc2",
                content = "文档2的内容，包含相关的医学知识。",
                metadata = {"source": "测试源2"},
                score = 0.8
            )
        ]

        # 创建生成器实例
        self.generator = OpenAIGenerator(
            openai_client = self.mock_openai_client,
            cache_service = self.mock_cache_service,
            config = self.config
        )

    @pytest.mark.asyncio
    async def test_generate_with_cache_hit(self) - > None:
        """测试缓存命中情况下的生成"""
        # 设置缓存命中
        mock_result = GenerateResult(
            answer = "缓存的回答",
            references = [
                DocumentReference(
                    id = "doc1",
                    title = "测试文档1",
                    source = "测试源1",
                    url = "http: / /test1.com",
                    snippet = "文档1片段"
                )
            ],
            latency_ms = 10.5
        )
        self.mock_cache_service.get.return_value = mock_result

        # 执行生成
        query = "这是一个医学问题"
        result = await self.generator.generate(query, self.test_documents)

        # 验证结果
        self.assertEqual(result.answer, "缓存的回答")
        self.assertEqual(len(result.references), 1)

        # 验证缓存调用
        self.mock_cache_service.get.assert_called_once()
        self.mock_openai_client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_with_cache_miss(self) - > None:
        """测试缓存未命中情况下的生成"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行生成
        query = "这是一个医学问题"
        result = await self.generator.generate(query, self.test_documents)

        # 验证结果
        self.assertEqual(result.answer, "这是由AI生成的回答，参考了文档1和文档2。")
        self.assertEqual(len(result.references), 2)
        self.assertEqual(result.references[0].id, "doc1")

        # 验证调用
        self.mock_cache_service.get.assert_called_once()
        self.mock_openai_client.chat.completions.create.assert_called_once()
        self.mock_cache_service.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_custom_system_prompt(self) - > None:
        """测试自定义系统提示的生成"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行生成，带自定义系统提示
        query = "这是一个医学问题"
        custom_prompt = "你是中医专家，请用中医理论回答问题"
        result = await self.generator.generate(query, self.test_documents, system_prompt = custom_prompt)

        # 验证OpenAI调用参数
        self.mock_openai_client.chat.completions.create.assert_called_once()
        _, kwargs = self.mock_openai_client.chat.completions.create.call_args
        messages = kwargs.get("messages", [])

        # 找到系统消息并验证内容
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        self.assertTrue(len(system_messages) > 0)
        self.assertIn(custom_prompt, system_messages[0].get("content", ""))

    @pytest.mark.asyncio
    async def test_generate_with_custom_parameters(self) - > None:
        """测试自定义生成参数的生成"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行生成，带自定义参数
        query = "这是一个医学问题"
        generation_params = {
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 500
        }
        result = await self.generator.generate(
            query,
            self.test_documents,
            generation_params = generation_params
        )

        # 验证OpenAI调用参数
        self.mock_openai_client.chat.completions.create.assert_called_once()
        _, kwargs = self.mock_openai_client.chat.completions.create.call_args
        self.assertEqual(kwargs.get("temperature"), 0.2)
        self.assertEqual(kwargs.get("top_p"), 0.9)
        self.assertEqual(kwargs.get("max_tokens"), 500)

    @pytest.mark.asyncio
    async def test_error_handling(self) - > None:
        """测试错误处理"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 设置OpenAI抛出异常
        self.mock_openai_client.chat.completions.create.side_effect = Exception("模拟API错误")

        # 执行生成，预期会返回错误信息而不是抛出异常
        query = "这是一个医学问题"
        result = await self.generator.generate(query, self.test_documents)

        # 验证结果包含错误信息
        self.assertIn("生成回答失败", result.answer)
        self.assertEqual(len(result.references), 0)

    @pytest.mark.asyncio
    async def test_context_formatting(self) - > None:
        """测试上下文格式化"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行生成
        query = "这是一个医学问题"
        result = await self.generator.generate(query, self.test_documents)

        # 验证OpenAI调用参数
        self.mock_openai_client.chat.completions.create.assert_called_once()
        _, kwargs = self.mock_openai_client.chat.completions.create.call_args
        messages = kwargs.get("messages", [])

        # 找到用户消息并验证内容
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        self.assertTrue(len(user_messages) > 0)
        user_content = user_messages[0].get("content", "")

        # 验证上下文包含了文档内容
        for doc in self.test_documents:
            self.assertIn(doc.content, user_content)

    @pytest.mark.asyncio
    async def test_stream_generate(self) - > None:
        """测试流式生成"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 模拟流式响应
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock(delta = MagicMock(content = "这是流式"))]

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock(delta = MagicMock(content = "回答的"))]

        mock_chunk3 = MagicMock()
        mock_chunk3.choices = [MagicMock(delta = MagicMock(content = "一部分"))]

        self.mock_openai_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]

        # 执行流式生成
        query = "这是一个医学问题"

        # 收集流式响应
        chunks = []
        async for chunk in self.generator.stream_generate(query, self.test_documents):
            chunks.append(chunk)

        # 验证结果
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "这是流式")
        self.assertEqual(chunks[1], "回答的")
        self.assertEqual(chunks[2], "一部分")

    @pytest.mark.asyncio
    async def test_close_method(self) - > None:
        """测试关闭方法"""
        await self.generator.close()
        # 验证资源释放


if __name__ == "__main__":
    unittest.main()