#!/usr/bin/env python

"""
老克(laoke)智能体的无障碍服务客户端适配器
支持知识内容和学习材料的无障碍转换
"""

import asyncio
import logging

# 导入配置
import os
import sys
from typing import Any

import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 实际项目中需要导入生成的proto文件
# from accessibility_service.api.grpc import accessibility_pb2 as pb2
# from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)

class AccessibilityClient:
    """无障碍服务客户端适配器，为老克智能体提供无障碍能力"""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        初始化客户端

        Args:
            config: 配置字典，包含无障碍服务的连接信息
        """
        self.config = config or {}
        self.channel = None
        self.stub = None
        self._connect()
        logger.info("老克智能体无障碍服务客户端初始化完成")

    def _connect(self):
        """连接到无障碍服务"""
        try:
            # 从配置获取服务地址
            host = self.config.get('accessibility_service', {}).get('host', 'accessibility-service')
            port = self.config.get('accessibility_service', {}).get('port', 50051)

            # 创建gRPC通道
            self.channel = grpc.insecure_channel(f'{host}:{port}')

            # 导入生成的proto文件（实际项目中需要正确的导入路径）
            # from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc
            # self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)

            # 模拟stub（实际项目中替换为真实的stub）
            self.stub = MockAccessibilityStub()

            logger.info(f"已连接到无障碍服务: {host}:{port}")

        except Exception as e:
            logger.error(f"连接无障碍服务失败: {e}")
            self.stub = MockAccessibilityStub()  # 使用模拟客户端作为降级

    async def convert_knowledge_content_to_accessible(self, knowledge_info: dict[str, Any],
                                                    user_id: str, target_format: str = "audio") -> dict[str, Any]:
        """
        将知识内容转换为无障碍格式

        Args:
            knowledge_info: 知识内容信息
            user_id: 用户ID
            target_format: 目标格式（audio/simplified/braille）

        Returns:
            无障碍格式的知识内容
        """
        try:
            logger.info(f"转换知识内容: 用户={user_id}, 内容={knowledge_info.get('title', 'unknown')}")

            # 构建请求
            request = {
                'content_id': f"knowledge_{knowledge_info.get('knowledge_id', 'unknown')}",
                'content_type': 'knowledge_content',
                'user_id': user_id,
                'target_format': target_format,
                'preferences': {
                    'language': 'zh-CN',
                    'voice_type': 'educational',
                    'speech_rate': 0.9,  # 稍慢的语速便于学习
                    'include_examples': True,
                    'educational_context': True
                }
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理知识内容特定信息
            accessible_info = self._format_knowledge_content(knowledge_info, response, target_format)

            return {
                'accessible_content': accessible_info,
                'content_url': response.get('content_url', ''),
                'audio_content': response.get('audio_content', b''),
                'tactile_content': response.get('tactile_content', b''),
                'learning_aids': self._generate_learning_aids(knowledge_info, target_format),
                'success': True
            }

        except Exception as e:
            logger.error(f"知识内容无障碍转换失败: {e}")
            return {
                'accessible_content': f'知识内容转换失败: {str(e)}',
                'content_url': '',
                'audio_content': b'',
                'tactile_content': b'',
                'learning_aids': [],
                'success': False,
                'error': str(e)
            }

    async def convert_learning_path_to_accessible(self, learning_path: dict[str, Any],
                                                user_id: str, target_format: str = "audio") -> dict[str, Any]:
        """
        将学习路径转换为无障碍格式

        Args:
            learning_path: 学习路径信息
            user_id: 用户ID
            target_format: 目标格式

        Returns:
            无障碍格式的学习路径
        """
        try:
            logger.info(f"转换学习路径: 用户={user_id}, 路径={learning_path.get('path_name', 'unknown')}")

            # 构建请求
            request = {
                'content_id': f"learning_path_{learning_path.get('path_id', 'unknown')}",
                'content_type': 'learning_path',
                'user_id': user_id,
                'target_format': target_format,
                'preferences': {
                    'language': 'zh-CN',
                    'voice_type': 'educational',
                    'speech_rate': 1.0,
                    'include_progress': True,
                    'structured_content': True
                }
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理学习路径特定信息
            accessible_info = self._format_learning_path_content(learning_path, response, target_format)

            return {
                'accessible_content': accessible_info,
                'content_url': response.get('content_url', ''),
                'audio_content': response.get('audio_content', b''),
                'tactile_content': response.get('tactile_content', b''),
                'navigation_structure': self._generate_path_navigation(learning_path),
                'success': True
            }

        except Exception as e:
            logger.error(f"学习路径无障碍转换失败: {e}")
            return {
                'accessible_content': f'学习路径转换失败: {str(e)}',
                'content_url': '',
                'audio_content': b'',
                'tactile_content': b'',
                'navigation_structure': [],
                'success': False,
                'error': str(e)
            }

    async def provide_content_review_accessibility(self, content_data: dict[str, Any],
                                                 user_id: str, review_type: str = "quality") -> dict[str, Any]:
        """
        为内容审核提供无障碍支持

        Args:
            content_data: 待审核内容数据
            user_id: 用户ID
            review_type: 审核类型

        Returns:
            无障碍审核结果
        """
        try:
            logger.info(f"提供内容审核无障碍支持: 用户={user_id}, 类型={review_type}")

            # 构建请求
            request = {
                'screen_data': content_data.get('content_screenshot', b''),
                'user_id': user_id,
                'context': f"content_review_{review_type}",
                'preferences': {
                    'language': 'zh-CN',
                    'detail_level': 'high',
                    'review_context': True,
                    'highlight_issues': True
                }
            }

            # 调用无障碍服务的屏幕阅读接口
            response = await self._call_screen_reading(request)

            # 处理审核特定信息
            review_analysis = self._analyze_content_for_review(content_data, response, review_type)

            return {
                'content_description': response.get('screen_description', ''),
                'accessibility_issues': review_analysis.get('accessibility_issues', []),
                'quality_assessment': review_analysis.get('quality_assessment', {}),
                'recommendations': review_analysis.get('recommendations', []),
                'audio_summary': response.get('audio_description', b''),
                'success': True
            }

        except Exception as e:
            logger.error(f"内容审核无障碍支持失败: {e}")
            return {
                'content_description': f'内容审核失败: {str(e)}',
                'accessibility_issues': [],
                'quality_assessment': {},
                'recommendations': [],
                'audio_summary': b'',
                'success': False,
                'error': str(e)
            }

    async def convert_npc_interaction_to_accessible(self, npc_info: dict[str, Any],
                                                  user_id: str, interaction_type: str = "dialogue") -> dict[str, Any]:
        """
        将NPC交互转换为无障碍格式

        Args:
            npc_info: NPC信息
            user_id: 用户ID
            interaction_type: 交互类型

        Returns:
            无障碍格式的NPC交互
        """
        try:
            logger.info(f"转换NPC交互: 用户={user_id}, NPC={npc_info.get('npc_name', 'unknown')}")

            # 构建请求
            request = {
                'content_id': f"npc_{npc_info.get('npc_id', 'unknown')}",
                'content_type': 'npc_interaction',
                'user_id': user_id,
                'target_format': 'audio',  # NPC交互主要使用音频格式
                'preferences': {
                    'language': 'zh-CN',
                    'voice_type': npc_info.get('voice_type', 'friendly'),
                    'speech_rate': 1.0,
                    'character_personality': True,
                    'interactive_context': True
                }
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理NPC交互特定信息
            accessible_info = self._format_npc_interaction_content(npc_info, response, interaction_type)

            return {
                'accessible_content': accessible_info,
                'audio_dialogue': response.get('audio_content', b''),
                'interaction_options': self._generate_interaction_options(npc_info),
                'character_description': self._generate_character_description(npc_info),
                'success': True
            }

        except Exception as e:
            logger.error(f"NPC交互无障碍转换失败: {e}")
            return {
                'accessible_content': f'NPC交互转换失败: {str(e)}',
                'audio_dialogue': b'',
                'interaction_options': [],
                'character_description': '',
                'success': False,
                'error': str(e)
            }

    async def provide_knowledge_graph_navigation(self, graph_data: dict[str, Any],
                                               user_id: str, navigation_mode: str = "audio") -> dict[str, Any]:
        """
        为知识图谱提供无障碍导航

        Args:
            graph_data: 知识图谱数据
            user_id: 用户ID
            navigation_mode: 导航模式

        Returns:
            无障碍导航信息
        """
        try:
            logger.info(f"提供知识图谱导航: 用户={user_id}, 模式={navigation_mode}")

            # 构建请求
            request = {
                'screen_data': graph_data.get('graph_visualization', b''),
                'user_id': user_id,
                'context': 'knowledge_graph_navigation',
                'preferences': {
                    'language': 'zh-CN',
                    'detail_level': 'medium',
                    'graph_context': True,
                    'relationship_focus': True
                }
            }

            # 调用无障碍服务的屏幕阅读接口
            response = await self._call_screen_reading(request)

            # 处理知识图谱特定信息
            navigation_info = self._generate_graph_navigation_info(graph_data, response)

            return {
                'graph_description': response.get('screen_description', ''),
                'navigation_instructions': navigation_info.get('instructions', []),
                'node_descriptions': navigation_info.get('nodes', []),
                'relationship_descriptions': navigation_info.get('relationships', []),
                'audio_guidance': response.get('audio_description', b''),
                'keyboard_shortcuts': self._generate_graph_shortcuts(),
                'success': True
            }

        except Exception as e:
            logger.error(f"知识图谱导航失败: {e}")
            return {
                'graph_description': f'知识图谱导航失败: {str(e)}',
                'navigation_instructions': [],
                'node_descriptions': [],
                'relationship_descriptions': [],
                'audio_guidance': b'',
                'keyboard_shortcuts': [],
                'success': False,
                'error': str(e)
            }

    async def convert_educational_content_to_sign_language(self, content: str, user_id: str,
                                                         content_type: str = "lesson") -> dict[str, Any]:
        """
        将教育内容转换为手语

        Args:
            content: 教育内容文本
            user_id: 用户ID
            content_type: 内容类型

        Returns:
            手语转换结果
        """
        try:
            logger.info(f"转换教育内容为手语: 用户={user_id}, 类型={content_type}")

            # 构建请求（这里模拟手语生成请求）
            request = {
                'text_content': content,
                'user_id': user_id,
                'language': 'csl',  # 中国手语
                'content_type': content_type
            }

            # 调用无障碍服务的手语生成接口（模拟）
            response = await self._call_sign_language_generation(request)

            return {
                'sign_language_video': response.get('video_data', b''),
                'sign_language_description': response.get('description', ''),
                'key_signs': response.get('key_signs', []),
                'learning_notes': self._generate_sign_learning_notes(content),
                'success': True
            }

        except Exception as e:
            logger.error(f"教育内容手语转换失败: {e}")
            return {
                'sign_language_video': b'',
                'sign_language_description': f'手语转换失败: {str(e)}',
                'key_signs': [],
                'learning_notes': [],
                'success': False,
                'error': str(e)
            }

    def _format_knowledge_content(self, knowledge_info: dict[str, Any],
                                response: dict[str, Any], target_format: str) -> str:
        """格式化知识内容"""
        title = knowledge_info.get('title', '未知标题')
        category = knowledge_info.get('category', '未知分类')
        difficulty = knowledge_info.get('difficulty', '未知难度')
        content = knowledge_info.get('content', '无内容')

        if target_format == "simplified":
            return f"{title}（{category}，{difficulty}）：{content[:100]}..."
        elif target_format == "audio":
            return f"知识内容：{title}。分类：{category}。难度：{difficulty}。内容：{content}"
        else:
            return response.get('accessible_content', f"知识内容：{title}")

    def _format_learning_path_content(self, learning_path: dict[str, Any],
                                    response: dict[str, Any], target_format: str) -> str:
        """格式化学习路径内容"""
        path_name = learning_path.get('path_name', '未知路径')
        total_lessons = learning_path.get('total_lessons', 0)
        completed_lessons = learning_path.get('completed_lessons', 0)
        estimated_time = learning_path.get('estimated_time', '未知')

        progress = f"{completed_lessons}/{total_lessons}"

        if target_format == "simplified":
            return f"{path_name}，进度{progress}，预计{estimated_time}"
        elif target_format == "audio":
            return f"学习路径：{path_name}。总课程数：{total_lessons}。已完成：{completed_lessons}。预计学习时间：{estimated_time}。"
        else:
            return response.get('accessible_content', f"学习路径：{path_name}")

    def _format_npc_interaction_content(self, npc_info: dict[str, Any],
                                      response: dict[str, Any], interaction_type: str) -> str:
        """格式化NPC交互内容"""
        npc_name = npc_info.get('npc_name', '未知NPC')
        role = npc_info.get('role', '未知角色')
        current_dialogue = npc_info.get('current_dialogue', '无对话')

        if interaction_type == "dialogue":
            return f"{npc_name}（{role}）说：{current_dialogue}"
        elif interaction_type == "introduction":
            return f"这是{npc_name}，角色是{role}。{npc_info.get('description', '无描述')}"
        else:
            return response.get('accessible_content', f"NPC交互：{npc_name}")

    def _generate_learning_aids(self, knowledge_info: dict[str, Any], target_format: str) -> list[dict[str, Any]]:
        """生成学习辅助工具"""
        aids = []

        # 根据知识类型生成不同的学习辅助
        category = knowledge_info.get('category', '')

        if '中医' in category:
            aids.append({
                'type': 'mnemonic',
                'content': '记忆口诀：望闻问切算五诊法',
                'format': target_format
            })
            aids.append({
                'type': 'example',
                'content': '实例：舌红苔黄表示热证',
                'format': target_format
            })

        if '药材' in category:
            aids.append({
                'type': 'classification',
                'content': '分类：按功效分为补益类、清热类等',
                'format': target_format
            })

        return aids

    def _generate_path_navigation(self, learning_path: dict[str, Any]) -> list[dict[str, Any]]:
        """生成学习路径导航结构"""
        navigation = []

        lessons = learning_path.get('lessons', [])
        for i, lesson in enumerate(lessons):
            nav_item = {
                'lesson_number': i + 1,
                'title': lesson.get('title', f'第{i+1}课'),
                'status': lesson.get('status', 'not_started'),
                'accessibility_hint': f"第{i+1}课：{lesson.get('title', '未知标题')}"
            }

            if lesson.get('status') == 'completed':
                nav_item['accessibility_hint'] += '（已完成）'
            elif lesson.get('status') == 'in_progress':
                nav_item['accessibility_hint'] += '（进行中）'
            else:
                nav_item['accessibility_hint'] += '（未开始）'

            navigation.append(nav_item)

        return navigation

    def _analyze_content_for_review(self, content_data: dict[str, Any],
                                  response: dict[str, Any], review_type: str) -> dict[str, Any]:
        """分析内容进行审核"""
        analysis = {
            'accessibility_issues': [],
            'quality_assessment': {},
            'recommendations': []
        }

        # 检查无障碍问题
        if not content_data.get('alt_text'):
            analysis['accessibility_issues'].append('缺少图片替代文本')

        if not content_data.get('audio_description'):
            analysis['accessibility_issues'].append('缺少音频描述')

        # 质量评估
        content_length = len(content_data.get('content', ''))
        analysis['quality_assessment'] = {
            'content_length': content_length,
            'readability': 'medium' if content_length > 100 else 'high',
            'completeness': 'complete' if content_length > 200 else 'incomplete'
        }

        # 推荐建议
        if review_type == 'accessibility':
            analysis['recommendations'].append('添加更多无障碍标记')
            analysis['recommendations'].append('提供多种格式的内容')
        elif review_type == 'quality':
            analysis['recommendations'].append('增加实例和图表')
            analysis['recommendations'].append('优化内容结构')

        return analysis

    def _generate_interaction_options(self, npc_info: dict[str, Any]) -> list[dict[str, Any]]:
        """生成交互选项"""
        options = []

        npc_role = npc_info.get('role', '')

        if '老师' in npc_role or '导师' in npc_role:
            options.extend([
                {'option': '请教问题', 'action': 'ask_question', 'hint': '向老师请教学习问题'},
                {'option': '查看课程', 'action': 'view_courses', 'hint': '查看可学习的课程'},
                {'option': '获取建议', 'action': 'get_advice', 'hint': '获取学习建议'}
            ])

        if '医生' in npc_role:
            options.extend([
                {'option': '咨询症状', 'action': 'consult_symptoms', 'hint': '咨询健康症状'},
                {'option': '了解治疗', 'action': 'learn_treatment', 'hint': '了解治疗方法'}
            ])

        # 通用选项
        options.extend([
            {'option': '打招呼', 'action': 'greet', 'hint': '与NPC打招呼'},
            {'option': '结束对话', 'action': 'end_conversation', 'hint': '结束当前对话'}
        ])

        return options

    def _generate_character_description(self, npc_info: dict[str, Any]) -> str:
        """生成角色描述"""
        name = npc_info.get('npc_name', '未知角色')
        role = npc_info.get('role', '未知职业')
        personality = npc_info.get('personality', '友善')
        appearance = npc_info.get('appearance', '普通外观')

        return f"{name}是一位{role}，性格{personality}，{appearance}。"

    def _generate_graph_navigation_info(self, graph_data: dict[str, Any],
                                      response: dict[str, Any]) -> dict[str, Any]:
        """生成知识图谱导航信息"""
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])

        navigation_info = {
            'instructions': [
                '使用Tab键在节点间导航',
                '按回车键选择节点',
                '使用方向键探索关联节点',
                '按Escape键返回上级视图'
            ],
            'nodes': [],
            'relationships': []
        }

        # 处理节点信息
        for node in nodes[:10]:  # 限制显示前10个节点
            node_desc = {
                'id': node.get('id', ''),
                'label': node.get('label', '未知节点'),
                'type': node.get('type', '未知类型'),
                'description': f"{node.get('label', '未知节点')}（{node.get('type', '未知类型')}）"
            }
            navigation_info['nodes'].append(node_desc)

        # 处理关系信息
        for edge in edges[:10]:  # 限制显示前10个关系
            rel_desc = {
                'source': edge.get('source', ''),
                'target': edge.get('target', ''),
                'relationship': edge.get('relationship', '相关'),
                'description': f"{edge.get('source', '')} {edge.get('relationship', '相关')} {edge.get('target', '')}"
            }
            navigation_info['relationships'].append(rel_desc)

        return navigation_info

    def _generate_graph_shortcuts(self) -> list[dict[str, str]]:
        """生成知识图谱快捷键"""
        return [
            {'key': 'Tab', 'action': '在节点间导航'},
            {'key': 'Enter', 'action': '选择当前节点'},
            {'key': '方向键', 'action': '探索相邻节点'},
            {'key': 'Space', 'action': '展开/折叠节点'},
            {'key': 'Ctrl+F', 'action': '搜索节点'},
            {'key': 'Escape', 'action': '返回上级视图'}
        ]

    def _generate_sign_learning_notes(self, content: str) -> list[str]:
        """生成手语学习笔记"""
        notes = []

        # 提取关键词
        if '中医' in content:
            notes.append('中医相关手语需要注意传统文化背景')

        if '诊断' in content:
            notes.append('诊断类手语要准确表达医学概念')

        if '治疗' in content:
            notes.append('治疗手语需要清晰表达操作步骤')

        # 通用学习建议
        notes.extend([
            '注意手语的节奏和表情',
            '重复练习关键手势',
            '结合语境理解手语含义'
        ])

        return notes

    # 模拟的服务调用方法（实际项目中替换为真实的gRPC调用）
    async def _call_accessible_content(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用无障碍内容转换服务"""
        await asyncio.sleep(0.1)
        content_type = request.get('content_type', 'unknown')

        if content_type == 'knowledge_content':
            return {
                'accessible_content': '中医五诊法包括望、闻、问、切、算五种诊断方法，是中医诊断的基础',
                'content_url': 'https://accessibility.suoke.life/knowledge/123',
                'audio_content': b'mock_knowledge_audio',
                'tactile_content': b'mock_knowledge_braille'
            }
        elif content_type == 'learning_path':
            return {
                'accessible_content': '中医基础学习路径包含10个课程，当前进度3/10',
                'content_url': 'https://accessibility.suoke.life/path/456',
                'audio_content': b'mock_path_audio',
                'tactile_content': b'mock_path_braille'
            }
        elif content_type == 'npc_interaction':
            return {
                'accessible_content': '老中医张大夫正在为您讲解脉诊要点',
                'content_url': 'https://accessibility.suoke.life/npc/789',
                'audio_content': b'mock_npc_audio',
                'tactile_content': b'mock_npc_braille'
            }
        else:
            return {
                'accessible_content': '内容已转换为无障碍格式',
                'content_url': 'https://accessibility.suoke.life/content/general',
                'audio_content': b'mock_audio_content',
                'tactile_content': b'mock_braille_content'
            }

    async def _call_screen_reading(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用屏幕阅读服务"""
        await asyncio.sleep(0.1)
        context = request.get('context', '')

        if 'content_review' in context:
            return {
                'screen_description': '当前显示待审核的教育内容，包含文本、图片和音频元素',
                'elements': [
                    {
                        'element_type': 'text',
                        'content': '中医基础理论',
                        'action': 'read',
                        'location': {'x': 100, 'y': 50, 'width': 200, 'height': 30}
                    },
                    {
                        'element_type': 'image',
                        'content': '经络图',
                        'action': 'describe',
                        'location': {'x': 100, 'y': 100, 'width': 300, 'height': 200}
                    }
                ],
                'audio_description': b'mock_review_audio'
            }
        elif 'knowledge_graph' in context:
            return {
                'screen_description': '知识图谱显示中医理论体系，包含多个相互关联的概念节点',
                'elements': [
                    {
                        'element_type': 'node',
                        'content': '阴阳理论',
                        'action': 'select',
                        'location': {'x': 200, 'y': 150, 'width': 80, 'height': 40}
                    },
                    {
                        'element_type': 'node',
                        'content': '五行学说',
                        'action': 'select',
                        'location': {'x': 300, 'y': 200, 'width': 80, 'height': 40}
                    }
                ],
                'audio_description': b'mock_graph_audio'
            }
        else:
            return {
                'screen_description': '当前显示老克学习界面',
                'elements': [],
                'audio_description': b'mock_screen_audio'
            }

    async def _call_sign_language_generation(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用手语生成服务（模拟）"""
        await asyncio.sleep(0.2)
        return {
            'video_data': b'mock_sign_language_video',
            'description': '手语视频：中医五诊法的手语表达',
            'key_signs': [
                {'sign': '中医', 'description': '双手合十表示传统医学'},
                {'sign': '诊断', 'description': '手指指向眼睛表示观察'},
                {'sign': '治疗', 'description': '双手做按摩动作'}
            ]
        }

    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
        logger.info("老克无障碍服务客户端连接已关闭")


class MockAccessibilityStub:
    """模拟的无障碍服务存根（用于开发和测试）"""

    def __init__(self):
        logger.info("使用模拟无障碍服务存根")

    async def AccessibleContent(self, request):
        """模拟无障碍内容转换"""
        await asyncio.sleep(0.1)
        return type('Response', (), {
            'accessible_content': '模拟教育内容无障碍转换',
            'content_url': 'https://mock.url',
            'audio_content': b'mock_educational_audio',
            'tactile_content': b'mock_educational_braille'
        })()
