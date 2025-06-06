"""
python_example - 索克生活项目模块
"""

from typing import Any
import json
import requests

#!/usr/bin/env python3

"""
索克生活无障碍服务 Python SDK 示例
"""




class AccessibilityServiceClient:
    """无障碍服务客户端"""

    def __init__(self, base_url: str, token: str):
        """
        初始化客户端

        Args:
            base_url: API基础URL
            token: 认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'User-Agent': 'SuokeLife-AccessibilityService-Python-SDK/1.0.0'
        })

    def analyze_scene(self, user_id: str, image_path: str,
                     location: dict[str, float] | None = None) -> dict[str, Any]:
        """
        场景分析

        Args:
            user_id: 用户ID
            image_path: 图像文件路径
            location: 位置信息

        Returns:
            场景分析结果
        """
        url = f"{self.base_url}/blind-assistance/analyze-scene"

        data = {'user_id': user_id}
        if location:
            data['location'] = json.dumps(location)

        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = self.session.post(url, data=data, files=files)

        response.raise_for_status()
        return response.json()

    def speech_to_text(self, user_id: str, audio_path: str,
                      language: str = 'zh-CN') -> dict[str, Any]:
        """
        语音转文字

        Args:
            user_id: 用户ID
            audio_path: 音频文件路径
            language: 语言代码

        Returns:
            转换结果
        """
        url = f"{self.base_url}/voice-assistance/speech-to-text"

        data = {
            'user_id': user_id,
            'language': language
        }

        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            response = self.session.post(url, data=data, files=files)

        response.raise_for_status()
        return response.json()

    def text_to_speech(self, user_id: str, text: str,
                      voice: str = 'female', speed: float = 1.0) -> bytes:
        """
        文字转语音

        Args:
            user_id: 用户ID
            text: 要转换的文字
            voice: 语音类型
            speed: 语速

        Returns:
            音频数据
        """
        url = f"{self.base_url}/voice-assistance/text-to-speech"

        data = {
            'user_id': user_id,
            'text': text,
            'voice': voice,
            'speed': speed
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.content

    def check_health(self) -> dict[str, Any]:
        """
        检查服务健康状态

        Returns:
            健康状态信息
        """
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == '__main__':
    # 初始化客户端
    client = AccessibilityServiceClient(
        base_url='https://api.suoke.life/accessibility/v1',
        token='your-jwt-token-here'
    )

    try:
        # 检查服务健康状态
        health = client.check_health()
        print(f"服务状态: {health['status']}")

        # 场景分析示例
        result = client.analyze_scene(
            user_id='user123',
            image_path='scene.jpg',
            location={'latitude': 39.9042, 'longitude': 116.4074}
        )
        print(f"场景分析结果: {result['scene_description']}")

        # 语音转文字示例
        stt_result = client.speech_to_text(
            user_id='user123',
            audio_path='speech.wav'
        )
        print(f"识别文字: {stt_result['text']}")

        # 文字转语音示例
        audio_data = client.text_to_speech(
            user_id='user123',
            text='欢迎使用索克生活无障碍服务'
        )

        with open('output.mp3', 'wb') as f:
            f.write(audio_data)
        print("语音文件已保存为 output.mp3")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"错误: {e}")
