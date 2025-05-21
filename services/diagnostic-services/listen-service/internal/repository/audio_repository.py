"""
音频数据存储库 - 管理音频分析结果的存储和检索
"""
import os
import json
import time
import logging
import pymongo
from typing import Dict, List, Optional, Any, Union
from bson.objectid import ObjectId
from datetime import datetime, timedelta

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class AudioRepository:
    """音频数据存储库，负责音频分析结果的持久化存储"""
    
    def __init__(self):
        """初始化音频存储库"""
        self.config = get_config()
        self.db_config = self.config.get("database", {})
        
        # 数据库连接参数
        self.db_host = self.db_config.get("host", "localhost")
        self.db_port = self.db_config.get("port", 27017)
        self.db_name = self.db_config.get("database", "listen_service")
        self.db_username = self.db_config.get("username")
        self.db_password = self.db_config.get("password")
        self.db_auth_source = self.db_config.get("auth_source", "admin")
        self.collection_prefix = self.db_config.get("collection_prefix", "listen_")
        
        # 集合名称
        self.voice_collection = f"{self.collection_prefix}voice_analysis"
        self.sound_collection = f"{self.collection_prefix}sound_analysis"
        self.emotion_collection = f"{self.collection_prefix}emotion_analysis"
        self.dialect_collection = f"{self.collection_prefix}dialect_detection"
        self.transcription_collection = f"{self.collection_prefix}transcription"
        self.batch_collection = f"{self.collection_prefix}batch_analysis"
        
        # 初始化数据库连接
        self.client = None
        self.db = None
        self.connect()
        
        logger.info("音频存储库初始化完成")
    
    def connect(self) -> None:
        """建立数据库连接"""
        try:
            # 构建连接URI
            if self.db_username and self.db_password:
                uri = f"mongodb://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?authSource={self.db_auth_source}"
            else:
                uri = f"mongodb://{self.db_host}:{self.db_port}/{self.db_name}"
            
            # 连接MongoDB
            self.client = pymongo.MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                maxPoolSize=self.db_config.get("connection_pool_size", 10),
                retryWrites=self.db_config.get("retry_writes", True),
                retryReads=self.db_config.get("retry_reads", True)
            )
            
            # 测试连接
            self.client.server_info()
            
            # 获取数据库
            self.db = self.client[self.db_name]
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"已连接到MongoDB: {self.db_host}:{self.db_port}/{self.db_name}")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            # 不抛出异常，让服务继续运行，后续再次尝试连接
            self.client = None
            self.db = None
    
    def _create_indexes(self) -> None:
        """创建数据库索引"""
        if not self.db:
            return
            
        try:
            # 语音分析索引
            self.db[self.voice_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.voice_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.voice_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            # 声音分析索引
            self.db[self.sound_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.sound_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.sound_collection].create_index([("sound_type", pymongo.ASCENDING)])
            self.db[self.sound_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            # 情绪分析索引
            self.db[self.emotion_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.emotion_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.emotion_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            # 方言检测索引
            self.db[self.dialect_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.dialect_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.dialect_collection].create_index([("primary_dialect", pymongo.ASCENDING)])
            self.db[self.dialect_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            # 转写索引
            self.db[self.transcription_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.transcription_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.transcription_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            # 批量分析索引
            self.db[self.batch_collection].create_index([("user_id", pymongo.ASCENDING)])
            self.db[self.batch_collection].create_index([("session_id", pymongo.ASCENDING)])
            self.db[self.batch_collection].create_index([("timestamp", pymongo.DESCENDING)])
            
            logger.info("数据库索引创建成功")
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
    
    def save_voice_analysis(self, analysis: Dict[str, Any], 
                          user_id: str, session_id: str) -> str:
        """
        保存语音分析结果
        
        Args:
            analysis: 分析结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存语音分析结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "analysis_id": analysis.get("analysis_id", f"voice_{int(time.time()*1000)}"),
                "speech_rate": analysis.get("speech_rate", 0.0),
                "pitch_avg": analysis.get("pitch_avg", 0.0),
                "pitch_range": analysis.get("pitch_range", 0.0),
                "volume_avg": analysis.get("volume_avg", 0.0),
                "voice_stability": analysis.get("voice_stability", 0.0),
                "breathiness": analysis.get("breathiness", 0.0),
                "features": analysis.get("features", []),
                "tcm_relevance": analysis.get("tcm_relevance", {}),
                "diagnostic_hint": analysis.get("diagnostic_hint", ""),
                "confidence": analysis.get("confidence", 0.0),
                "timestamp": analysis.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.voice_collection].insert_one(doc)
            
            logger.debug(f"保存语音分析结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存语音分析结果失败: {str(e)}")
            return ""
    
    def save_sound_analysis(self, analysis: Dict[str, Any], 
                          user_id: str, session_id: str) -> str:
        """
        保存声音分析结果
        
        Args:
            analysis: 分析结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存声音分析结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "analysis_id": analysis.get("analysis_id", f"sound_{int(time.time()*1000)}"),
                "sound_type": analysis.get("sound_type", "SOUND_UNKNOWN"),
                "duration": analysis.get("duration", 0.0),
                "amplitude": analysis.get("amplitude", 0.0),
                "regularity": analysis.get("regularity", 0.0),
                "moisture": analysis.get("moisture", 0.5),
                "patterns": analysis.get("patterns", []),
                "tcm_relevance": analysis.get("tcm_relevance", {}),
                "diagnostic_hint": analysis.get("diagnostic_hint", ""),
                "confidence": analysis.get("confidence", 0.0),
                "timestamp": analysis.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.sound_collection].insert_one(doc)
            
            logger.debug(f"保存声音分析结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存声音分析结果失败: {str(e)}")
            return ""
    
    def save_emotion_analysis(self, analysis: Dict[str, Any], 
                            user_id: str, session_id: str) -> str:
        """
        保存情绪分析结果
        
        Args:
            analysis: 分析结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存情绪分析结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "analysis_id": analysis.get("analysis_id", f"emotion_{int(time.time()*1000)}"),
                "emotions": analysis.get("emotions", {}),
                "emotional_stability": analysis.get("emotional_stability", 0.5),
                "tcm_emotions": analysis.get("tcm_emotions", {}),
                "trend": analysis.get("trend", "STABLE"),
                "diagnostic_hint": analysis.get("diagnostic_hint", ""),
                "confidence": analysis.get("confidence", 0.0),
                "timestamp": analysis.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.emotion_collection].insert_one(doc)
            
            logger.debug(f"保存情绪分析结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存情绪分析结果失败: {str(e)}")
            return ""
    
    def save_dialect_detection(self, detection: Dict[str, Any], 
                             user_id: str, session_id: str) -> str:
        """
        保存方言检测结果
        
        Args:
            detection: 检测结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存方言检测结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "detection_id": detection.get("detection_id", f"dialect_{int(time.time()*1000)}"),
                "primary_dialect": detection.get("primary_dialect", ""),
                "primary_dialect_region": detection.get("primary_dialect_region", ""),
                "primary_dialect_confidence": detection.get("primary_dialect_confidence", 0.0),
                "candidates": detection.get("candidates", []),
                "timestamp": detection.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.dialect_collection].insert_one(doc)
            
            logger.debug(f"保存方言检测结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存方言检测结果失败: {str(e)}")
            return ""
    
    def save_transcription(self, transcription: Dict[str, Any], 
                         user_id: str, session_id: str) -> str:
        """
        保存语音转写结果
        
        Args:
            transcription: 转写结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存语音转写结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "transcription_id": transcription.get("transcription_id", f"trans_{int(time.time()*1000)}"),
                "text": transcription.get("text", ""),
                "language": transcription.get("language", ""),
                "dialect": transcription.get("dialect", ""),
                "confidence": transcription.get("confidence", 0.0),
                "segments": transcription.get("segments", []),
                "timestamp": transcription.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.transcription_collection].insert_one(doc)
            
            logger.debug(f"保存语音转写结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存语音转写结果失败: {str(e)}")
            return ""
    
    def save_batch_analysis(self, analysis: Dict[str, Any], 
                          user_id: str, session_id: str) -> str:
        """
        保存批量分析结果
        
        Args:
            analysis: 分析结果
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            str: 记录ID
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法保存批量分析结果")
                return ""
        
        try:
            # 准备文档
            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "batch_id": analysis.get("batch_id", f"batch_{int(time.time()*1000)}"),
                "voice_analysis": analysis.get("voice_analysis", {}),
                "sound_analysis": analysis.get("sound_analysis", {}),
                "dialect": analysis.get("dialect", {}),
                "emotion": analysis.get("emotion", {}),
                "transcription": analysis.get("transcription", {}),
                "diagnosis": analysis.get("diagnosis", {}),
                "timestamp": analysis.get("timestamp", int(time.time())),
                "created_at": datetime.now()
            }
            
            # 插入文档
            result = self.db[self.batch_collection].insert_one(doc)
            
            logger.debug(f"保存批量分析结果成功: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存批量分析结果失败: {str(e)}")
            return ""
    
    def get_voice_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        获取语音分析结果
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            Optional[Dict[str, Any]]: 分析结果，不存在则返回None
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法获取语音分析结果")
                return None
        
        try:
            # 查询文档
            doc = self.db[self.voice_collection].find_one({"analysis_id": analysis_id})
            
            if doc:
                # 转换ObjectId为字符串
                doc["_id"] = str(doc["_id"])
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"获取语音分析结果失败: {str(e)}")
            return None
    
    def get_voice_analyses_by_session(self, session_id: str, 
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取会话的语音分析结果列表
        
        Args:
            session_id: 会话ID
            limit: 最大返回数量
            
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法获取语音分析结果列表")
                return []
        
        try:
            # 查询文档
            cursor = self.db[self.voice_collection].find(
                {"session_id": session_id}
            ).sort("timestamp", -1).limit(limit)
            
            # 转换结果
            result = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                result.append(doc)
            
            return result
            
        except Exception as e:
            logger.error(f"获取语音分析结果列表失败: {str(e)}")
            return []
    
    def get_user_recent_analyses(self, user_id: str, 
                               limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取用户最近的各类分析结果
        
        Args:
            user_id: 用户ID
            limit: 每种类型的最大返回数量
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 分析结果字典，键为分析类型
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法获取用户最近分析结果")
                return {}
        
        try:
            result = {}
            
            # 获取语音分析结果
            voice_cursor = self.db[self.voice_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["voice_analyses"] = []
            for doc in voice_cursor:
                doc["_id"] = str(doc["_id"])
                result["voice_analyses"].append(doc)
            
            # 获取声音分析结果
            sound_cursor = self.db[self.sound_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["sound_analyses"] = []
            for doc in sound_cursor:
                doc["_id"] = str(doc["_id"])
                result["sound_analyses"].append(doc)
            
            # 获取情绪分析结果
            emotion_cursor = self.db[self.emotion_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["emotion_analyses"] = []
            for doc in emotion_cursor:
                doc["_id"] = str(doc["_id"])
                result["emotion_analyses"].append(doc)
            
            # 获取方言检测结果
            dialect_cursor = self.db[self.dialect_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["dialect_detections"] = []
            for doc in dialect_cursor:
                doc["_id"] = str(doc["_id"])
                result["dialect_detections"].append(doc)
            
            # 获取转写结果
            transcription_cursor = self.db[self.transcription_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["transcriptions"] = []
            for doc in transcription_cursor:
                doc["_id"] = str(doc["_id"])
                result["transcriptions"].append(doc)
            
            # 获取批量分析结果
            batch_cursor = self.db[self.batch_collection].find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            result["batch_analyses"] = []
            for doc in batch_cursor:
                doc["_id"] = str(doc["_id"])
                result["batch_analyses"].append(doc)
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户最近分析结果失败: {str(e)}")
            return {}
    
    def delete_old_records(self, days: int = 30) -> Dict[str, int]:
        """
        删除指定天数前的旧记录
        
        Args:
            days: 天数
            
        Returns:
            Dict[str, int]: 各类型删除的记录数
        """
        if not self.db:
            self.connect()
            if not self.db:
                logger.error("数据库连接失败，无法删除旧记录")
                return {}
        
        try:
            # 计算截止时间
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 删除各集合中的旧记录
            voice_result = self.db[self.voice_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            sound_result = self.db[self.sound_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            emotion_result = self.db[self.emotion_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            dialect_result = self.db[self.dialect_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            transcription_result = self.db[self.transcription_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            batch_result = self.db[self.batch_collection].delete_many(
                {"created_at": {"$lt": cutoff_date}}
            )
            
            # 返回删除计数
            result = {
                "voice_analyses": voice_result.deleted_count,
                "sound_analyses": sound_result.deleted_count,
                "emotion_analyses": emotion_result.deleted_count,
                "dialect_detections": dialect_result.deleted_count,
                "transcriptions": transcription_result.deleted_count,
                "batch_analyses": batch_result.deleted_count
            }
            
            logger.info(f"删除{days}天前的旧记录: {result}")
            return result
            
        except Exception as e:
            logger.error(f"删除旧记录失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            try:
                self.client.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {str(e)}")


# 全局存储库实例
global_audio_repository = None

def get_audio_repository() -> AudioRepository:
    """
    获取全局音频存储库实例
    
    Returns:
        AudioRepository: 音频存储库实例
    """
    global global_audio_repository
    
    if global_audio_repository is None:
        global_audio_repository = AudioRepository()
    
    return global_audio_repository 