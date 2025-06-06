"""
test_model_factory - 索克生活项目模块
"""

from internal.agent.model_factory import ModelFactory
from unittest.mock import AsyncMock, MagicMock, patch
import os
import pytest
import sys
import unittest

#!/usr/bin/env python

"""
模型工厂单元测试
"""



# 添加项目根路径到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))



class TestModelFactory(unittest.TestCase):
    """模型工厂单元测试类"""

    def setUp(self):
        """测试前初始化"""
        # 模拟配置
        self.mock_config = {
            'models': {
                'llm': {
                    'primary_model': 'gpt-4o-mini',
                    'fallback_model': 'llama-3-8b',
                    'providers': {
                        'openai': {
                            'api_key': 'mock-api-key',
                            'base_url': 'https://api.openai.com/v1',
                            'max_tokens': 2048,
                            'timeout': 60,
                            'retries': 3
                        },
                        'ollama': {
                            'base_url': 'http://ollama:11434',
                            'max_tokens': 2048,
                            'timeout': 120
                        }
                    },
                    'caching': {
                        'enabled': True,
                        'ttl': 3600
                    }
                }
            }
        }

        # 模拟OpenAI客户端
        self.mock_openai_client = MagicMock()
        self.mock_openai_client.chat.completions.create = AsyncMock()

        # 模拟Ollama客户端
        self.mock_ollama_client = MagicMock()
        self.mock_ollama_client.chat = AsyncMock()

        # 初始化模型工厂
        with patch('internal.agent.model_factory.Config', return_value=self.mock_config), \
             patch('internal.agent.model_factory.AsyncOpenAI', return_value=self.mock_openai_client), \
             patch('internal.agent.model_factory.OllamaAPI'):
            self.model_factory = ModelFactory()
            self.model_factory._ollama_client = self.mock_ollama_client

    @pytest.mark.asyncio
    async def test_get_model_client_openai(self):
        """测试获取OpenAI模型客户端"""
        # 调用被测试的方法
        client = await self.model_factory.get_model_client('openai')

        # 断言
        assert client == self.mock_openai_client

    @pytest.mark.asyncio
    async def test_get_model_client_ollama(self):
        """测试获取Ollama模型客户端"""
        # 调用被测试的方法
        client = await self.model_factory.get_model_client('ollama')

        # 断言
        assert client == self.mock_ollama_client

    @pytest.mark.asyncio
    async def test_get_model_client_invalid(self):
        """测试获取无效模型客户端"""
        # 调用被测试的方法
        with pytest.raises(ValueError) as excinfo:
            await self.model_factory.get_model_client('invalid_provider')

        # 断言
        assert "不支持的模型提供者" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text_openai(self):
        """测试使用OpenAI生成文本"""
        # 设置模拟返回值
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这是OpenAI生成的回复内容"
        self.mock_openai_client.chat.completions.create.return_value = mock_response

        # 调用被测试的方法
        prompt = "请解释一下中医的阴阳五行理论"
        result = await self.model_factory.generate_text(
            provider='openai',
            model='gpt-4o-mini',
            prompt=prompt,
            system_prompt="你是老克，索克生活APP探索频道的智能体"
        )

        # 断言
        assert result == "这是OpenAI生成的回复内容"
        self.mock_openai_client.chat.completions.create.assert_called_once()

        # 检查调用参数
        call_args = self.mock_openai_client.chat.completions.create.call_args[1]
        assert call_args['model'] == 'gpt-4o-mini'
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]['role'] == 'system'
        assert call_args['messages'][1]['role'] == 'user'
        assert call_args['messages'][1]['content'] == prompt

    @pytest.mark.asyncio
    async def test_generate_text_ollama(self):
        """测试使用Ollama生成文本"""
        # 设置模拟返回值
        self.mock_ollama_client.chat.return_value = {
            'message': {'content': '这是Ollama生成的回复内容'}
        }

        # 调用被测试的方法
        prompt = "请解释一下中医的经络学说"
        result = await self.model_factory.generate_text(
            provider='ollama',
            model='llama-3-8b',
            prompt=prompt,
            system_prompt="你是老克，索克生活APP探索频道的智能体"
        )

        # 断言
        assert result == "这是Ollama生成的回复内容"
        self.mock_ollama_client.chat.assert_called_once()

        # 检查调用参数
        call_args = self.mock_ollama_client.chat.call_args[1]
        assert call_args['model'] == 'llama-3-8b'
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]['role'] == 'system'
        assert call_args['messages'][1]['role'] == 'user'
        assert call_args['messages'][1]['content'] == prompt

    @pytest.mark.asyncio
    async def test_generate_text_with_cache_hit(self):
        """测试带缓存命中的文本生成"""
        # 设置模拟缓存
        mock_cache = MagicMock()
        mock_cache.get = MagicMock(return_value="来自缓存的回复内容")
        self.model_factory._cache = mock_cache

        # 调用被测试的方法
        prompt = "这是一个会命中缓存的提示"
        result = await self.model_factory.generate_text(
            provider='openai',
            model='gpt-4o-mini',
            prompt=prompt,
            system_prompt="你是老克，索克生活APP探索频道的智能体"
        )

        # 断言
        assert result == "来自缓存的回复内容"
        mock_cache.get.assert_called_once()
        self.mock_openai_client.chat.completions.create.assert_not_called()  # 不应调用API

    @pytest.mark.asyncio
    async def test_generate_text_with_cache_miss(self):
        """测试带缓存未命中的文本生成"""
        # 设置模拟缓存
        mock_cache = MagicMock()
        mock_cache.get = MagicMock(return_value=None)  # 缓存未命中
        mock_cache.set = MagicMock()
        self.model_factory._cache = mock_cache

        # 设置模拟API返回值
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这是新生成的回复内容"
        self.mock_openai_client.chat.completions.create.return_value = mock_response

        # 调用被测试的方法
        prompt = "这是一个不会命中缓存的提示"
        result = await self.model_factory.generate_text(
            provider='openai',
            model='gpt-4o-mini',
            prompt=prompt,
            system_prompt="你是老克，索克生活APP探索频道的智能体"
        )

        # 断言
        assert result == "这是新生成的回复内容"
        mock_cache.get.assert_called_once()
        self.mock_openai_client.chat.completions.create.assert_called_once()
        mock_cache.set.assert_called_once()  # 应保存新结果到缓存

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_provider(self):
        """测试从主要提供者回退到次要提供者"""
        # 设置主要提供者(OpenAI)失败
        self.mock_openai_client.chat.completions.create.side_effect = Exception("API错误")

        # 设置次要提供者(Ollama)成功
        self.mock_ollama_client.chat.return_value = {
            'message': {'content': '这是Ollama备用模型生成的回复内容'}
        }

        # 调用被测试的方法，使用自动回退
        prompt = "请解释中医的辨证论治"
        result = await self.model_factory.generate_text_with_fallback(
            prompt=prompt,
            system_prompt="你是老克，索克生活APP探索频道的智能体"
        )

        # 断言
        assert result == "这是Ollama备用模型生成的回复内容"
        self.mock_openai_client.chat.completions.create.assert_called_once()
        self.mock_ollama_client.chat.assert_called_once()


if __name__ == '__main__':
    unittest.main()
