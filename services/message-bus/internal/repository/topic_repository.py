from abc import ABC, abstractmethod
import os
import json
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple

import redis

from internal.model.topic import Topic
from config.settings import Settings

logger = logging.getLogger(__name__)

class TopicRepository(ABC):
    """主题存储库接口"""
    
    @abstractmethod
    async def save_topic(self, topic: Topic) -> bool:
        """
        保存主题
        
        Args:
            topic: 主题对象
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    async def get_topic(self, name: str) -> Optional[Topic]:
        """
        获取主题
        
        Args:
            name: 主题名称
            
        Returns:
            Optional[Topic]: 主题对象，如不存在则返回None
        """
        pass
    
    @abstractmethod
    async def topic_exists(self, name: str) -> bool:
        """
        检查主题是否存在
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 主题是否存在
        """
        pass
    
    @abstractmethod
    async def delete_topic(self, name: str) -> bool:
        """
        删除主题
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    async def list_topics(
        self, 
        page_size: int = 100, 
        page_token: Optional[str] = None
    ) -> Tuple[List[Topic], Optional[str], int]:
        """
        获取主题列表
        
        Args:
            page_size: 每页大小
            page_token: 分页标记
            
        Returns:
            Tuple[List[Topic], Optional[str], int]: 主题列表, 下一页标记, 总主题数
        """
        pass

class RedisTopicRepository(TopicRepository):
    """Redis实现的主题存储库"""
    
    # Redis键前缀
    TOPIC_KEY_PREFIX = "suoke:topic:"
    ALL_TOPICS_KEY = "suoke:all_topics"
    
    def __init__(self, settings: Settings):
        """
        初始化Redis主题存储库
        
        Args:
            settings: 应用配置
        """
        self.settings = settings
        self.redis_settings = settings.redis
        self.redis_client = self._create_redis_client()
    
    def _create_redis_client(self) -> redis.Redis:
        """
        创建Redis客户端
        
        Returns:
            redis.Redis: Redis客户端实例
        """
        return redis.Redis(
            host=self.redis_settings.host,
            port=self.redis_settings.port,
            db=self.redis_settings.db,
            password=self.redis_settings.password,
            ssl=self.redis_settings.use_ssl,
            decode_responses=False  # 不自动解码，我们会手动处理
        )
    
    def _topic_key(self, name: str) -> str:
        """
        获取主题的Redis键
        
        Args:
            name: 主题名称
            
        Returns:
            str: Redis键
        """
        return f"{self.TOPIC_KEY_PREFIX}{name}"
    
    def _serialize_topic(self, topic: Topic) -> bytes:
        """
        序列化主题对象
        
        Args:
            topic: 主题对象
            
        Returns:
            bytes: 序列化后的字节
        """
        topic_dict = topic.to_dict()
        return json.dumps(topic_dict).encode('utf-8')
    
    def _deserialize_topic(self, data: bytes) -> Optional[Topic]:
        """
        反序列化主题对象
        
        Args:
            data: 序列化的主题数据
            
        Returns:
            Optional[Topic]: 主题对象，如数据无效则返回None
        """
        if not data:
            return None
            
        try:
            topic_dict = json.loads(data.decode('utf-8'))
            return Topic.from_dict(topic_dict)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"反序列化主题失败: {str(e)}")
            return None
    
    async def save_topic(self, topic: Topic) -> bool:
        """
        保存主题到Redis
        
        Args:
            topic: 主题对象
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 序列化主题
            topic_data = self._serialize_topic(topic)
            
            # 将主题保存到Redis
            topic_key = self._topic_key(topic.name)
            self.redis_client.set(topic_key, topic_data)
            
            # 将主题名称添加到主题列表集合
            self.redis_client.sadd(self.ALL_TOPICS_KEY, topic.name.encode('utf-8'))
            
            logger.info(f"保存主题: {topic}")
            return True
        except Exception as e:
            logger.error(f"保存主题失败: {str(e)}", exc_info=True)
            return False
    
    async def get_topic(self, name: str) -> Optional[Topic]:
        """
        从Redis获取主题
        
        Args:
            name: 主题名称
            
        Returns:
            Optional[Topic]: 主题对象，如不存在则返回None
        """
        try:
            # 获取主题数据
            topic_key = self._topic_key(name)
            topic_data = self.redis_client.get(topic_key)
            
            if not topic_data:
                return None
                
            # 反序列化主题
            return self._deserialize_topic(topic_data)
        except Exception as e:
            logger.error(f"获取主题失败: {str(e)}", exc_info=True)
            return None
    
    async def topic_exists(self, name: str) -> bool:
        """
        检查主题是否存在于Redis
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 主题是否存在
        """
        try:
            topic_key = self._topic_key(name)
            return bool(self.redis_client.exists(topic_key))
        except Exception as e:
            logger.error(f"检查主题存在性失败: {str(e)}", exc_info=True)
            return False
    
    async def delete_topic(self, name: str) -> bool:
        """
        从Redis删除主题
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 删除主题数据
            topic_key = self._topic_key(name)
            self.redis_client.delete(topic_key)
            
            # 从主题列表集合中移除
            self.redis_client.srem(self.ALL_TOPICS_KEY, name.encode('utf-8'))
            
            logger.info(f"删除主题: {name}")
            return True
        except Exception as e:
            logger.error(f"删除主题失败: {str(e)}", exc_info=True)
            return False
    
    async def list_topics(
        self, 
        page_size: int = 100, 
        page_token: Optional[str] = None
    ) -> Tuple[List[Topic], Optional[str], int]:
        """
        从Redis获取主题列表
        
        Args:
            page_size: 每页大小
            page_token: 分页标记
            
        Returns:
            Tuple[List[Topic], Optional[str], int]: 主题列表, 下一页标记, 总主题数
        """
        try:
            # 获取所有主题名称
            all_topic_names = list(map(
                lambda x: x.decode('utf-8'),
                self.redis_client.smembers(self.ALL_TOPICS_KEY)
            ))
            
            # 计算总主题数
            total_count = len(all_topic_names)
            
            # 根据分页标记计算起始索引
            start_index = 0
            if page_token:
                try:
                    # 解码分页标记获取起始索引
                    decoded = base64.b64decode(page_token).decode('utf-8')
                    start_index = int(decoded)
                except (ValueError, base64.binascii.Error):
                    start_index = 0
            
            # 获取当前页的主题名称
            end_index = min(start_index + page_size, total_count)
            current_page_names = all_topic_names[start_index:end_index]
            
            # 计算下一页标记
            next_page_token = None
            if end_index < total_count:
                next_page_token = base64.b64encode(str(end_index).encode('utf-8')).decode('utf-8')
            
            # 获取主题详情
            topics = []
            for name in current_page_names:
                topic = await self.get_topic(name)
                if topic:
                    topics.append(topic)
            
            return topics, next_page_token, total_count
        except Exception as e:
            logger.error(f"获取主题列表失败: {str(e)}", exc_info=True)
            return [], None, 0

class FileTopicRepository(TopicRepository):
    """文件系统实现的主题存储库"""
    
    def __init__(self, settings: Settings):
        """
        初始化文件系统主题存储库
        
        Args:
            settings: 应用配置
        """
        self.settings = settings
        self.base_dir = os.path.join(settings.base_dir, 'data', 'topics')
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _topic_path(self, name: str) -> str:
        """
        获取主题的文件路径
        
        Args:
            name: 主题名称
            
        Returns:
            str: 文件路径
        """
        return os.path.join(self.base_dir, f"{name}.json")
    
    def _index_path(self) -> str:
        """
        获取主题索引文件路径
        
        Returns:
            str: 索引文件路径
        """
        return os.path.join(self.base_dir, "index.json")
    
    def _update_index(self, topic_name: str, remove: bool = False) -> None:
        """
        更新主题索引
        
        Args:
            topic_name: 主题名称
            remove: 是否从索引中移除
        """
        index_path = self._index_path()
        
        # 读取当前索引
        index = {}
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except json.JSONDecodeError:
                index = {}
        
        # 更新索引
        if 'topics' not in index:
            index['topics'] = []
            
        topics = index['topics']
        
        if remove:
            # 如果是移除操作
            if topic_name in topics:
                topics.remove(topic_name)
        else:
            # 如果是添加操作
            if topic_name not in topics:
                topics.append(topic_name)
        
        # 保存索引
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    async def save_topic(self, topic: Topic) -> bool:
        """
        保存主题到文件系统
        
        Args:
            topic: 主题对象
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 获取主题文件路径
            file_path = self._topic_path(topic.name)
            
            # 保存主题到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(topic.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 更新索引
            self._update_index(topic.name)
            
            logger.info(f"保存主题: {topic}")
            return True
        except Exception as e:
            logger.error(f"保存主题失败: {str(e)}", exc_info=True)
            return False
    
    async def get_topic(self, name: str) -> Optional[Topic]:
        """
        从文件系统获取主题
        
        Args:
            name: 主题名称
            
        Returns:
            Optional[Topic]: 主题对象，如不存在则返回None
        """
        file_path = self._topic_path(name)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Topic.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"读取主题失败: {str(e)}", exc_info=True)
            return None
    
    async def topic_exists(self, name: str) -> bool:
        """
        检查主题是否存在于文件系统
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 主题是否存在
        """
        file_path = self._topic_path(name)
        return os.path.exists(file_path)
    
    async def delete_topic(self, name: str) -> bool:
        """
        从文件系统删除主题
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 是否删除成功
        """
        file_path = self._topic_path(name)
        
        if not os.path.exists(file_path):
            return False
            
        try:
            # 删除主题文件
            os.remove(file_path)
            
            # 更新索引
            self._update_index(name, remove=True)
            
            logger.info(f"删除主题: {name}")
            return True
        except IOError as e:
            logger.error(f"删除主题失败: {str(e)}", exc_info=True)
            return False
    
    async def list_topics(
        self, 
        page_size: int = 100, 
        page_token: Optional[str] = None
    ) -> Tuple[List[Topic], Optional[str], int]:
        """
        从文件系统获取主题列表
        
        Args:
            page_size: 每页大小
            page_token: 分页标记
            
        Returns:
            Tuple[List[Topic], Optional[str], int]: 主题列表, 下一页标记, 总主题数
        """
        try:
            # 读取主题索引
            index_path = self._index_path()
            if not os.path.exists(index_path):
                return [], None, 0
                
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
                
            # 获取所有主题名称
            all_topic_names = index.get('topics', [])
            
            # 计算总主题数
            total_count = len(all_topic_names)
            
            # 根据分页标记计算起始索引
            start_index = 0
            if page_token:
                try:
                    decoded = base64.b64decode(page_token).decode('utf-8')
                    start_index = int(decoded)
                except (ValueError, base64.binascii.Error):
                    start_index = 0
            
            # 获取当前页的主题名称
            end_index = min(start_index + page_size, total_count)
            current_page_names = all_topic_names[start_index:end_index]
            
            # 计算下一页标记
            next_page_token = None
            if end_index < total_count:
                next_page_token = base64.b64encode(str(end_index).encode('utf-8')).decode('utf-8')
            
            # 获取主题详情
            topics = []
            for name in current_page_names:
                topic = await self.get_topic(name)
                if topic:
                    topics.append(topic)
            
            return topics, next_page_token, total_count
        except Exception as e:
            logger.error(f"获取主题列表失败: {str(e)}", exc_info=True)
            return [], None, 0 