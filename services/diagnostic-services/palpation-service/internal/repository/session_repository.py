#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
会话存储库
负责管理切诊会话数据的存储与检索
"""

import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SessionRepository:
    """会话存储库，管理脉诊会话数据"""
    
    def __init__(self, db_config):
        """
        初始化会话存储库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_client = self._init_db_client()
        self.db = self.db_client[db_config.get('name', 'palpation_db')]
        
        # 获取集合名
        collections = db_config.get('collections', {})
        self.pulse_sessions_collection = self.db[collections.get('sessions', 'pulse_sessions')]
        self.abdominal_analyses_collection = self.db[collections.get('analyses', 'pulse_analyses')]
        self.skin_analyses_collection = self.db[collections.get('analyses', 'pulse_analyses')]
        self.reports_collection = self.db[collections.get('reports', 'palpation_reports')]
        
        # 创建索引
        self._create_indexes()
        
        logger.info("会话存储库初始化完成")
    
    def _init_db_client(self):
        # This method is mentioned in __init__ but not implemented in the provided code block.
        # It's assumed to exist as it's called in the __init__ method.
        # If it's not implemented, it should be implemented here.
        pass
    
    def _create_indexes(self):
        # This method is mentioned in __init__ but not implemented in the provided code block.
        # It's assumed to exist as it's called in the __init__ method.
        # If it's not implemented, it should be implemented here.
        pass
    
    def create_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        创建新的脉诊会话
        
        Args:
            session_id: 会话ID
            session_data: 会话数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in session_data:
                session_data['created_at'] = time.time()
            
            # 存储会话数据
            result = self.pulse_sessions_collection.insert_one(session_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建脉诊会话失败: {str(e)}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取脉诊会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据，不存在时返回None
        """
        try:
            session = self.pulse_sessions_collection.find_one({'session_id': session_id})
            return session
        except Exception as e:
            logger.exception(f"获取脉诊会话失败: {str(e)}")
            return None
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        更新脉诊会话
        
        Args:
            session_id: 会话ID
            session_data: 新的会话数据
            
        Returns:
            更新是否成功
        """
        try:
            # 添加更新时间
            session_data['updated_at'] = time.time()
            
            # 更新会话数据
            result = self.pulse_sessions_collection.replace_one(
                {'session_id': session_id},
                session_data
            )
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"更新脉诊会话失败: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除脉诊会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除是否成功
        """
        try:
            result = self.pulse_sessions_collection.delete_one({'session_id': session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.exception(f"删除脉诊会话失败: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户的脉诊会话列表
        
        Args:
            user_id: 用户ID
            limit: 返回的最大会话数
            skip: 跳过的会话数
            
        Returns:
            会话列表
        """
        try:
            sessions = list(self.pulse_sessions_collection.find(
                {'user_id': user_id},
                {'data_packets': 0}  # 不返回数据包，减少数据量
            ).sort('created_at', -1).skip(skip).limit(limit))
            
            return sessions
        except Exception as e:
            logger.exception(f"获取用户脉诊会话列表失败: {str(e)}")
            return []
    
    def create_abdominal_analysis(self, analysis_id: str, analysis_data: Dict[str, Any]) -> bool:
        """
        创建腹诊分析记录
        
        Args:
            analysis_id: 分析ID
            analysis_data: 分析数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in analysis_data:
                analysis_data['created_at'] = time.time()
            
            # 存储分析数据
            result = self.abdominal_analyses_collection.insert_one(analysis_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建腹诊分析记录失败: {str(e)}")
            return False
    
    def get_abdominal_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        获取腹诊分析记录
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            分析数据，不存在时返回None
        """
        try:
            analysis = self.abdominal_analyses_collection.find_one({'analysis_id': analysis_id})
            return analysis
        except Exception as e:
            logger.exception(f"获取腹诊分析记录失败: {str(e)}")
            return None
    
    def get_user_abdominal_analyses(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户的腹诊分析记录列表
        
        Args:
            user_id: 用户ID
            limit: 返回的最大记录数
            skip: 跳过的记录数
            
        Returns:
            分析记录列表
        """
        try:
            analyses = list(self.abdominal_analyses_collection.find(
                {'user_id': user_id}
            ).sort('created_at', -1).skip(skip).limit(limit))
            
            return analyses
        except Exception as e:
            logger.exception(f"获取用户腹诊分析记录列表失败: {str(e)}")
            return []
    
    def create_skin_analysis(self, analysis_id: str, analysis_data: Dict[str, Any]) -> bool:
        """
        创建皮肤触诊分析记录
        
        Args:
            analysis_id: 分析ID
            analysis_data: 分析数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in analysis_data:
                analysis_data['created_at'] = time.time()
            
            # 存储分析数据
            result = self.skin_analyses_collection.insert_one(analysis_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建皮肤触诊分析记录失败: {str(e)}")
            return False
    
    def get_skin_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        获取皮肤触诊分析记录
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            分析数据，不存在时返回None
        """
        try:
            analysis = self.skin_analyses_collection.find_one({'analysis_id': analysis_id})
            return analysis
        except Exception as e:
            logger.exception(f"获取皮肤触诊分析记录失败: {str(e)}")
            return None
    
    def get_user_skin_analyses(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户的皮肤触诊分析记录列表
        
        Args:
            user_id: 用户ID
            limit: 返回的最大记录数
            skip: 跳过的记录数
            
        Returns:
            分析记录列表
        """
        try:
            analyses = list(self.skin_analyses_collection.find(
                {'user_id': user_id}
            ).sort('created_at', -1).skip(skip).limit(limit))
            
            return analyses
        except Exception as e:
            logger.exception(f"获取用户皮肤触诊分析记录列表失败: {str(e)}")
            return []
    
    def create_report(self, report_id: str, report_data: Dict[str, Any]) -> bool:
        """
        创建切诊报告
        
        Args:
            report_id: 报告ID
            report_data: 报告数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in report_data:
                report_data['created_at'] = time.time()
            
            # 存储报告数据
            result = self.reports_collection.insert_one(report_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建切诊报告失败: {str(e)}")
            return False
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        获取切诊报告
        
        Args:
            report_id: 报告ID
            
        Returns:
            报告数据，不存在时返回None
        """
        try:
            report = self.reports_collection.find_one({'report_id': report_id})
            return report
        except Exception as e:
            logger.exception(f"获取切诊报告失败: {str(e)}")
            return None
    
    def get_user_reports(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户的切诊报告列表
        
        Args:
            user_id: 用户ID
            limit: 返回的最大报告数
            skip: 跳过的报告数
            
        Returns:
            报告列表
        """
        try:
            reports = list(self.reports_collection.find(
                {'user_id': user_id}
            ).sort('created_at', -1).skip(skip).limit(limit))
            
            return reports
        except Exception as e:
            logger.exception(f"获取用户切诊报告列表失败: {str(e)}")
            return []
    
    def ping(self):
        """
        检查数据库连接状态
        
        Returns:
            bool: 如果数据库连接正常则返回True
            
        Raises:
            Exception: 如果数据库连接失败则抛出异常
        """
        try:
            # 执行简单的命令检查连接状态
            self.db.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"数据库连接检查失败: {e}")
            raise 