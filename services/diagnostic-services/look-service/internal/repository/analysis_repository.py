#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析结果存储库模块

负责存储和检索望诊分析结果，包括面色分析和形体分析等结果的持久化存储。
使用SQLite作为轻量级数据库，支持历史记录查询和趋势分析。
"""

import os
import json
import sqlite3
import time
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Union

from structlog import get_logger

from pkg.utils.exceptions import DatabaseError, ResourceNotFoundError


# 设置日志
logger = get_logger()


class AnalysisType(str, Enum):
    """分析类型枚举"""
    FACE = "face"
    BODY = "body"
    TONGUE = "tongue"


class AnalysisRepository:
    """
    分析结果存储库类
    
    负责管理望诊分析结果的数据存储和检索，使用SQLite作为后端存储。
    提供CRUD操作和高级查询功能，支持结果缓存和批量操作。
    """
    
    def __init__(self, db_path: str = None):
        """
        初始化分析结果存储库
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        from config.config import get_config
        
        config = get_config()
        self.db_path = db_path or config.get("database.uri", "look_service.db")
        self.max_cache_size = config.get("database.max_cache_size", 100)
        self.enable_cache = config.get("database.enable_cache", True)
        self.cache = {}
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        
        # 初始化数据库
        self._init_db()
        
        logger.info("分析结果存储库初始化完成", db_path=self.db_path)
    
    def _init_db(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建分析记录表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_records (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    summary TEXT,
                    metadata TEXT,
                    thumbnail BLOB,
                    created_at INTEGER NOT NULL
                )
                ''')
                
                # 创建分析详情表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    detail_data TEXT NOT NULL,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_records (id) ON DELETE CASCADE
                )
                ''')
                
                # 创建分析特征表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    feature_value TEXT,
                    confidence REAL,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_records (id) ON DELETE CASCADE
                )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_user_id ON analysis_records (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_type ON analysis_records (analysis_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_timestamp ON analysis_records (timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_features_analysis_id ON analysis_features (analysis_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_features_name ON analysis_features (feature_name)')
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error("初始化数据库失败", error=str(e))
            raise DatabaseError(f"初始化数据库失败: {str(e)}")
    
    def save_analysis(self, 
                     analysis_id: str, 
                     user_id: str,
                     analysis_type: Union[str, AnalysisType],
                     timestamp: int,
                     summary: str,
                     detail_data: Dict[str, Any],
                     features: List[Dict[str, Any]],
                     thumbnail: Optional[bytes] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        保存分析结果
        
        Args:
            analysis_id: 分析记录ID
            user_id: 用户ID
            analysis_type: 分析类型
            timestamp: 分析时间戳
            summary: 分析总结
            detail_data: 详细分析数据
            features: 分析特征列表
            thumbnail: 缩略图二进制数据（可选）
            metadata: 元数据（可选）
            
        Returns:
            分析记录ID
            
        Raises:
            DatabaseError: 当数据库操作失败时
        """
        try:
            # 如果analysis_type是枚举，转换为字符串
            if isinstance(analysis_type, AnalysisType):
                analysis_type = analysis_type.value
                
            # 序列化元数据
            metadata_json = json.dumps(metadata) if metadata else None
            
            # 序列化详细数据
            detail_json = json.dumps(detail_data)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('BEGIN TRANSACTION')
                cursor = conn.cursor()
                
                # 插入分析记录
                cursor.execute('''
                INSERT INTO analysis_records 
                (id, user_id, analysis_type, timestamp, summary, metadata, thumbnail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis_id, 
                    user_id, 
                    analysis_type, 
                    timestamp, 
                    summary, 
                    metadata_json, 
                    thumbnail, 
                    int(time.time())
                ))
                
                # 插入详细数据
                cursor.execute('''
                INSERT INTO analysis_details 
                (analysis_id, detail_data)
                VALUES (?, ?)
                ''', (analysis_id, detail_json))
                
                # 插入特征数据
                for feature in features:
                    feature_name = feature.get('feature_name')
                    feature_value = feature.get('value')
                    confidence = feature.get('confidence', 1.0)
                    
                    # 如果feature_value是字典或列表，序列化为JSON
                    if isinstance(feature_value, (dict, list)):
                        feature_value = json.dumps(feature_value)
                        
                    cursor.execute('''
                    INSERT INTO analysis_features 
                    (analysis_id, feature_name, feature_value, confidence)
                    VALUES (?, ?, ?, ?)
                    ''', (analysis_id, feature_name, feature_value, confidence))
                
                conn.commit()
                
                # 更新缓存
                if self.enable_cache:
                    self.cache[analysis_id] = {
                        'id': analysis_id,
                        'user_id': user_id,
                        'analysis_type': analysis_type,
                        'timestamp': timestamp,
                        'summary': summary,
                        'detail_data': detail_data,
                        'features': features,
                        'metadata': metadata,
                        # 不缓存缩略图以节省内存
                    }
                    
                    # 管理缓存大小
                    if len(self.cache) > self.max_cache_size:
                        # 移除最先添加的项（简单的FIFO策略）
                        oldest_key = next(iter(self.cache))
                        del self.cache[oldest_key]
                
                logger.info("保存分析结果成功", 
                          analysis_id=analysis_id, 
                          user_id=user_id, 
                          analysis_type=analysis_type)
                
                return analysis_id
                
        except sqlite3.Error as e:
            logger.error("保存分析结果失败", 
                       error=str(e), 
                       analysis_id=analysis_id, 
                       user_id=user_id)
            raise DatabaseError(f"保存分析结果失败: {str(e)}")
    
    def get_analysis(self, analysis_id: str, include_thumbnail: bool = False) -> Dict[str, Any]:
        """
        获取单个分析记录
        
        Args:
            analysis_id: 分析记录ID
            include_thumbnail: 是否包含缩略图
            
        Returns:
            分析记录字典
            
        Raises:
            ResourceNotFoundError: 当记录不存在时
            DatabaseError: 当数据库操作失败时
        """
        # 检查缓存
        if self.enable_cache and analysis_id in self.cache and not include_thumbnail:
            return self.cache[analysis_id]
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 查询基本记录
                if include_thumbnail:
                    query = '''
                    SELECT id, user_id, analysis_type, timestamp, summary, metadata, thumbnail, created_at
                    FROM analysis_records
                    WHERE id = ?
                    '''
                else:
                    query = '''
                    SELECT id, user_id, analysis_type, timestamp, summary, metadata, created_at
                    FROM analysis_records
                    WHERE id = ?
                    '''
                
                cursor.execute(query, (analysis_id,))
                record = cursor.fetchone()
                
                if not record:
                    raise ResourceNotFoundError(f"分析记录不存在: {analysis_id}")
                
                # 转换为字典
                result = dict(record)
                
                # 解析元数据
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])
                
                # 查询详细数据
                cursor.execute('''
                SELECT detail_data
                FROM analysis_details
                WHERE analysis_id = ?
                ''', (analysis_id,))
                
                detail_row = cursor.fetchone()
                if detail_row:
                    result['detail_data'] = json.loads(detail_row['detail_data'])
                
                # 查询特征数据
                cursor.execute('''
                SELECT feature_name, feature_value, confidence
                FROM analysis_features
                WHERE analysis_id = ?
                ''', (analysis_id,))
                
                features = []
                for feature_row in cursor.fetchall():
                    feature_value = feature_row['feature_value']
                    
                    # 尝试解析JSON值
                    try:
                        if feature_value and (
                            feature_value.startswith('{') or 
                            feature_value.startswith('[')
                        ):
                            feature_value = json.loads(feature_value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                        
                    features.append({
                        'feature_name': feature_row['feature_name'],
                        'value': feature_value,
                        'confidence': feature_row['confidence']
                    })
                
                result['features'] = features
                
                # 更新缓存（不包含缩略图）
                if self.enable_cache:
                    cache_result = result.copy()
                    if 'thumbnail' in cache_result:
                        del cache_result['thumbnail']
                    self.cache[analysis_id] = cache_result
                
                return result
                
        except ResourceNotFoundError:
            raise
        except sqlite3.Error as e:
            logger.error("获取分析记录失败", error=str(e), analysis_id=analysis_id)
            raise DatabaseError(f"获取分析记录失败: {str(e)}")
    
    def get_analysis_history(
        self,
        user_id: str,
        analysis_type: Optional[Union[str, AnalysisType]] = None,
        limit: int = 10,
        offset: int = 0,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户分析历史记录
        
        Args:
            user_id: 用户ID
            analysis_type: 分析类型过滤
            limit: 返回记录数量限制
            offset: 分页偏移量
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            分析记录列表
            
        Raises:
            DatabaseError: 当数据库操作失败时
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 构建查询条件
                query = '''
                SELECT id, user_id, analysis_type, timestamp, summary, created_at
                FROM analysis_records
                WHERE user_id = ?
                '''
                params = [user_id]
                
                if analysis_type:
                    # 如果analysis_type是枚举，转换为字符串
                    if isinstance(analysis_type, AnalysisType):
                        analysis_type = analysis_type.value
                    query += " AND analysis_type = ?"
                    params.append(analysis_type)
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                # 添加排序和分页
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    record = dict(row)
                    results.append(record)
                
                return results
                
        except sqlite3.Error as e:
            logger.error("获取分析历史记录失败", 
                       error=str(e), 
                       user_id=user_id, 
                       analysis_type=analysis_type)
            raise DatabaseError(f"获取分析历史记录失败: {str(e)}")
    
    def count_analysis_records(
        self,
        user_id: Optional[str] = None,
        analysis_type: Optional[Union[str, AnalysisType]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> int:
        """
        统计分析记录数量
        
        Args:
            user_id: 用户ID过滤
            analysis_type: 分析类型过滤
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            记录数量
            
        Raises:
            DatabaseError: 当数据库操作失败时
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                query = 'SELECT COUNT(*) FROM analysis_records WHERE 1=1'
                params = []
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if analysis_type:
                    # 如果analysis_type是枚举，转换为字符串
                    if isinstance(analysis_type, AnalysisType):
                        analysis_type = analysis_type.value
                    query += " AND analysis_type = ?"
                    params.append(analysis_type)
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                cursor.execute(query, params)
                count = cursor.fetchone()[0]
                
                return count
                
        except sqlite3.Error as e:
            logger.error("统计分析记录失败", 
                       error=str(e), 
                       user_id=user_id, 
                       analysis_type=analysis_type)
            raise DatabaseError(f"统计分析记录失败: {str(e)}")
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        删除分析记录
        
        Args:
            analysis_id: 分析记录ID
            
        Returns:
            删除是否成功
            
        Raises:
            ResourceNotFoundError: 当记录不存在时
            DatabaseError: 当数据库操作失败时
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查记录是否存在
                cursor.execute('SELECT id FROM analysis_records WHERE id = ?', (analysis_id,))
                if not cursor.fetchone():
                    raise ResourceNotFoundError(f"分析记录不存在: {analysis_id}")
                
                # 删除记录（相关表的记录会通过外键级联删除）
                cursor.execute('DELETE FROM analysis_records WHERE id = ?', (analysis_id,))
                
                conn.commit()
                
                # 从缓存中移除
                if self.enable_cache and analysis_id in self.cache:
                    del self.cache[analysis_id]
                
                logger.info("删除分析记录成功", analysis_id=analysis_id)
                
                return True
                
        except ResourceNotFoundError:
            raise
        except sqlite3.Error as e:
            logger.error("删除分析记录失败", error=str(e), analysis_id=analysis_id)
            raise DatabaseError(f"删除分析记录失败: {str(e)}")
    
    def get_feature_trend(
        self,
        user_id: str,
        feature_name: str,
        analysis_type: Optional[Union[str, AnalysisType]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取特征趋势数据
        
        Args:
            user_id: 用户ID
            feature_name: 特征名称
            analysis_type: 分析类型过滤
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 返回记录数量限制
            
        Returns:
            趋势数据列表，包含时间戳和特征值
            
        Raises:
            DatabaseError: 当数据库操作失败时
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 构建查询条件
                query = '''
                SELECT r.timestamp, f.feature_value, f.confidence
                FROM analysis_records r
                JOIN analysis_features f ON r.id = f.analysis_id
                WHERE r.user_id = ? AND f.feature_name = ?
                '''
                params = [user_id, feature_name]
                
                if analysis_type:
                    # 如果analysis_type是枚举，转换为字符串
                    if isinstance(analysis_type, AnalysisType):
                        analysis_type = analysis_type.value
                    query += " AND r.analysis_type = ?"
                    params.append(analysis_type)
                
                if start_time is not None:
                    query += " AND r.timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND r.timestamp <= ?"
                    params.append(end_time)
                
                # 添加排序和分页
                query += " ORDER BY r.timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    feature_value = row['feature_value']
                    
                    # 尝试解析JSON值
                    try:
                        if feature_value and (
                            feature_value.startswith('{') or 
                            feature_value.startswith('[')
                        ):
                            feature_value = json.loads(feature_value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                    
                    results.append({
                        'timestamp': row['timestamp'],
                        'value': feature_value,
                        'confidence': row['confidence']
                    })
                
                # 反转结果，使其按时间从早到晚排序
                results.reverse()
                
                return results
                
        except sqlite3.Error as e:
            logger.error("获取特征趋势数据失败", 
                       error=str(e), 
                       user_id=user_id, 
                       feature_name=feature_name)
            raise DatabaseError(f"获取特征趋势数据失败: {str(e)}")
    
    def compare_analyses(self, first_analysis_id: str, second_analysis_id: str) -> Dict[str, Any]:
        """
        比较两次分析结果
        
        Args:
            first_analysis_id: 第一个分析记录ID
            second_analysis_id: 第二个分析记录ID
            
        Returns:
            比较结果字典
            
        Raises:
            ResourceNotFoundError: 当记录不存在时
            DatabaseError: 当数据库操作失败时
        """
        try:
            # 获取两次分析记录
            first = self.get_analysis(first_analysis_id)
            second = self.get_analysis(second_analysis_id)
            
            # 确保分析类型相同
            if first['analysis_type'] != second['analysis_type']:
                raise ValueError("只能比较相同类型的分析记录")
            
            # 提取特征进行比较
            first_features = {f['feature_name']: f for f in first.get('features', [])}
            second_features = {f['feature_name']: f for f in second.get('features', [])}
            
            # 所有特征名称的集合
            all_features = set(first_features.keys()) | set(second_features.keys())
            
            feature_comparisons = []
            improvements = []
            deteriorations = []
            unchanged = []
            
            for feature_name in all_features:
                first_value = first_features.get(feature_name, {}).get('value')
                second_value = second_features.get(feature_name, {}).get('value')
                
                if feature_name in first_features and feature_name in second_features:
                    # 两次分析都有该特征
                    is_numeric = False
                    change_percentage = None
                    
                    # 检查是否可以计算数值变化
                    try:
                        if isinstance(first_value, (int, float)) and isinstance(second_value, (int, float)):
                            # 数值类型特征
                            is_numeric = True
                            if first_value != 0:
                                change_percentage = (second_value - first_value) / first_value * 100
                            else:
                                change_percentage = 0 if second_value == 0 else 100
                    except (TypeError, ValueError):
                        pass
                    
                    # 确定变化方向
                    if is_numeric:
                        if abs(change_percentage) < 5:  # 小于5%视为未变化
                            change_direction = "unchanged"
                            unchanged.append(feature_name)
                        elif change_percentage > 0:
                            # 根据特征含义，增加可能是改善也可能是恶化
                            # 这里简化处理，假设所有数值增加都是改善
                            change_direction = "improved"
                            improvements.append(feature_name)
                        else:
                            change_direction = "deteriorated"
                            deteriorations.append(feature_name)
                    else:
                        # 非数值类型，只判断是否相同
                        if first_value == second_value:
                            change_direction = "unchanged"
                            unchanged.append(feature_name)
                        else:
                            # 对于非数值类型，无法直接判断是改善还是恶化
                            # 需要根据特征的具体含义来确定，这里简化处理
                            change_direction = "changed"
                            # 暂时归类为未变化
                            unchanged.append(feature_name)
                    
                    feature_comparisons.append({
                        'feature_name': feature_name,
                        'first_value': first_value,
                        'second_value': second_value,
                        'change_percentage': change_percentage,
                        'change_direction': change_direction
                    })
                    
                elif feature_name in first_features:
                    # 新分析缺少该特征，通常视为恶化
                    feature_comparisons.append({
                        'feature_name': feature_name,
                        'first_value': first_value,
                        'second_value': None,
                        'change_percentage': -100,
                        'change_direction': "deteriorated"
                    })
                    deteriorations.append(feature_name)
                    
                else:
                    # 新分析新增该特征，通常视为改善
                    feature_comparisons.append({
                        'feature_name': feature_name,
                        'first_value': None,
                        'second_value': second_value,
                        'change_percentage': 100,
                        'change_direction': "improved"
                    })
                    improvements.append(feature_name)
            
            # 生成比较总结
            first_time = datetime.fromtimestamp(first['timestamp']).strftime('%Y-%m-%d')
            second_time = datetime.fromtimestamp(second['timestamp']).strftime('%Y-%m-%d')
            
            improvement_count = len(improvements)
            deterioration_count = len(deteriorations)
            unchanged_count = len(unchanged)
            
            if improvement_count > deterioration_count:
                overall_trend = "改善"
            elif improvement_count < deterioration_count:
                overall_trend = "恶化"
            else:
                overall_trend = "保持稳定"
            
            comparison_summary = (
                f"从{first_time}到{second_time}，整体状况{overall_trend}。"
                f"共有{improvement_count}项指标改善，{deterioration_count}项指标恶化，{unchanged_count}项指标保持稳定。"
            )
            
            return {
                'first_analysis_id': first_analysis_id,
                'second_analysis_id': second_analysis_id,
                'first_timestamp': first['timestamp'],
                'second_timestamp': second['timestamp'],
                'analysis_type': first['analysis_type'],
                'feature_comparisons': feature_comparisons,
                'improvements': improvements,
                'deteriorations': deteriorations,
                'unchanged': unchanged,
                'comparison_summary': comparison_summary
            }
                
        except (ResourceNotFoundError, ValueError) as e:
            logger.error("比较分析记录失败", 
                       error=str(e), 
                       first_id=first_analysis_id, 
                       second_id=second_analysis_id)
            raise
        except sqlite3.Error as e:
            logger.error("比较分析记录失败", 
                       error=str(e), 
                       first_id=first_analysis_id, 
                       second_id=second_analysis_id)
            raise DatabaseError(f"比较分析记录失败: {str(e)}")
    
    def clear_cache(self):
        """清除结果缓存"""
        if self.enable_cache:
            self.cache.clear()
            logger.info("已清除分析结果缓存")
    
    def get_db_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {
                    'total_records': 0,
                    'records_by_type': {},
                    'user_count': 0,
                    'oldest_record': None,
                    'newest_record': None,
                    'db_size_bytes': 0
                }
                
                # 总记录数
                cursor.execute('SELECT COUNT(*) FROM analysis_records')
                stats['total_records'] = cursor.fetchone()[0]
                
                # 按类型统计
                cursor.execute('''
                SELECT analysis_type, COUNT(*) as count
                FROM analysis_records
                GROUP BY analysis_type
                ''')
                
                for row in cursor.fetchall():
                    stats['records_by_type'][row[0]] = row[1]
                
                # 用户数
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM analysis_records')
                stats['user_count'] = cursor.fetchone()[0]
                
                # 最早记录
                cursor.execute('''
                SELECT MIN(timestamp) FROM analysis_records
                ''')
                oldest = cursor.fetchone()[0]
                stats['oldest_record'] = oldest
                
                # 最新记录
                cursor.execute('''
                SELECT MAX(timestamp) FROM analysis_records
                ''')
                newest = cursor.fetchone()[0]
                stats['newest_record'] = newest
                
                # 数据库文件大小
                if os.path.exists(self.db_path):
                    stats['db_size_bytes'] = os.path.getsize(self.db_path)
                
                return stats
                
        except sqlite3.Error as e:
            logger.error("获取数据库统计信息失败", error=str(e))
            raise DatabaseError(f"获取数据库统计信息失败: {str(e)}")
            
    def get_thumbnail(self, analysis_id: str) -> Optional[bytes]:
        """
        获取分析记录的缩略图
        
        Args:
            analysis_id: 分析记录ID
            
        Returns:
            缩略图二进制数据，如果不存在则返回None
            
        Raises:
            ResourceNotFoundError: 当记录不存在时
            DatabaseError: 当数据库操作失败时
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 查询缩略图
                cursor.execute('''
                SELECT thumbnail
                FROM analysis_records
                WHERE id = ?
                ''', (analysis_id,))
                
                row = cursor.fetchone()
                if not row:
                    raise ResourceNotFoundError(f"分析记录不存在: {analysis_id}")
                
                return row[0]
                
        except ResourceNotFoundError:
            raise
        except sqlite3.Error as e:
            logger.error("获取缩略图失败", error=str(e), analysis_id=analysis_id)
            raise DatabaseError(f"获取缩略图失败: {str(e)}") 