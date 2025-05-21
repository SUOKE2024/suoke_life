#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import psycopg2
from psycopg2.extras import DictCursor, Json

from internal.model.medical_query import MedicalQuery, SourceReference

logger = logging.getLogger(__name__)

class MedicalQueryRepository:
    """医疗查询存储库，用于存储和检索医疗查询历史"""

    def __init__(self, db_config):
        """
        初始化医疗查询存储库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config

    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.user,
            password=self.db_config.password,
            dbname=self.db_config.dbname
        )

    def save_query(self, query: MedicalQuery) -> str:
        """
        保存医疗查询记录
        
        Args:
            query: 医疗查询对象
            
        Returns:
            查询ID
        """
        query_id = str(uuid.uuid4()) if not query.id else query.id
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 将来源引用转换为JSON格式
                    sources_json = [s.to_dict() for s in query.sources] if query.sources else []
                    
                    # 检查是否存在相同ID的查询
                    cur.execute(
                        "SELECT id FROM medical_queries WHERE id = %s",
                        (query_id,)
                    )
                    result = cur.fetchone()
                    
                    if result:
                        # 更新现有查询
                        cur.execute(
                            """
                            UPDATE medical_queries
                            SET user_id = %s,
                                query_text = %s,
                                answer = %s,
                                sources = %s,
                                is_emergency_advice = %s,
                                disclaimer = %s,
                                follow_up_questions = %s,
                                updated_at = %s
                            WHERE id = %s
                            """,
                            (
                                query.user_id,
                                query.query_text,
                                query.answer,
                                Json(sources_json),
                                query.is_emergency_advice,
                                query.disclaimer,
                                query.follow_up_questions,
                                datetime.utcnow(),
                                query_id
                            )
                        )
                    else:
                        # 创建新查询记录
                        cur.execute(
                            """
                            INSERT INTO medical_queries (
                                id, user_id, query_text, answer, sources,
                                is_emergency_advice, disclaimer, follow_up_questions,
                                created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                query_id,
                                query.user_id,
                                query.query_text,
                                query.answer,
                                Json(sources_json),
                                query.is_emergency_advice,
                                query.disclaimer,
                                query.follow_up_questions,
                                datetime.utcnow(),
                                datetime.utcnow()
                            )
                        )
                    
                    conn.commit()
                    logger.info(f"保存医疗查询记录: {query_id}")
                    return query_id
                    
        except Exception as e:
            logger.error(f"保存医疗查询记录失败: {str(e)}")
            raise

    def get_query_by_id(self, query_id: str) -> Optional[MedicalQuery]:
        """
        根据ID获取医疗查询记录
        
        Args:
            query_id: 查询ID
            
        Returns:
            医疗查询对象，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        """
                        SELECT id, user_id, query_text, answer, sources,
                               is_emergency_advice, disclaimer, follow_up_questions,
                               created_at, updated_at
                        FROM medical_queries
                        WHERE id = %s
                        """,
                        (query_id,)
                    )
                    result = cur.fetchone()
                    
                    if not result:
                        return None
                    
                    # 将JSON格式的来源引用转换为对象列表
                    sources = []
                    if result['sources']:
                        for source_dict in result['sources']:
                            sources.append(SourceReference(
                                title=source_dict.get('title'),
                                author=source_dict.get('author'),
                                publication=source_dict.get('publication'),
                                url=source_dict.get('url'),
                                citation=source_dict.get('citation')
                            ))
                    
                    return MedicalQuery(
                        id=result['id'],
                        user_id=result['user_id'],
                        query_text=result['query_text'],
                        answer=result['answer'],
                        sources=sources,
                        is_emergency_advice=result['is_emergency_advice'],
                        disclaimer=result['disclaimer'],
                        follow_up_questions=result['follow_up_questions'],
                        created_at=result['created_at'],
                        updated_at=result['updated_at']
                    )
                    
        except Exception as e:
            logger.error(f"获取医疗查询记录失败: {str(e)}")
            raise

    def list_queries_by_user(self, user_id: str, limit: int = 10, offset: int = 0) -> List[MedicalQuery]:
        """
        获取用户的医疗查询历史记录
        
        Args:
            user_id: 用户ID
            limit: 每页记录数，默认10条
            offset: 偏移量，用于分页
            
        Returns:
            医疗查询对象列表
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        """
                        SELECT id, user_id, query_text, answer, sources,
                               is_emergency_advice, disclaimer, follow_up_questions,
                               created_at, updated_at
                        FROM medical_queries
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, limit, offset)
                    )
                    results = cur.fetchall()
                    
                    queries = []
                    for result in results:
                        # 将JSON格式的来源引用转换为对象列表
                        sources = []
                        if result['sources']:
                            for source_dict in result['sources']:
                                sources.append(SourceReference(
                                    title=source_dict.get('title'),
                                    author=source_dict.get('author'),
                                    publication=source_dict.get('publication'),
                                    url=source_dict.get('url'),
                                    citation=source_dict.get('citation')
                                ))
                        
                        queries.append(MedicalQuery(
                            id=result['id'],
                            user_id=result['user_id'],
                            query_text=result['query_text'],
                            answer=result['answer'],
                            sources=sources,
                            is_emergency_advice=result['is_emergency_advice'],
                            disclaimer=result['disclaimer'],
                            follow_up_questions=result['follow_up_questions'],
                            created_at=result['created_at'],
                            updated_at=result['updated_at']
                        ))
                    
                    return queries
                    
        except Exception as e:
            logger.error(f"获取用户医疗查询历史记录失败: {str(e)}")
            raise

    def get_query_count_by_user(self, user_id: str) -> int:
        """
        获取用户的医疗查询历史记录总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            查询记录总数
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM medical_queries WHERE user_id = %s",
                        (user_id,)
                    )
                    result = cur.fetchone()
                    return result[0] if result else 0
                    
        except Exception as e:
            logger.error(f"获取用户医疗查询历史记录总数失败: {str(e)}")
            raise

    def delete_query(self, query_id: str) -> bool:
        """
        删除医疗查询记录
        
        Args:
            query_id: 查询ID
            
        Returns:
            删除是否成功
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM medical_queries WHERE id = %s",
                        (query_id,)
                    )
                    rows_affected = cur.rowcount
                    conn.commit()
                    logger.info(f"删除医疗查询记录: {query_id}, 影响行数: {rows_affected}")
                    return rows_affected > 0
                    
        except Exception as e:
            logger.error(f"删除医疗查询记录失败: {str(e)}")
            raise

    def search_queries(self, user_id: str, keyword: str, limit: int = 10, offset: int = 0) -> List[MedicalQuery]:
        """
        搜索用户的医疗查询历史记录
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            limit: 每页记录数，默认10条
            offset: 偏移量，用于分页
            
        Returns:
            医疗查询对象列表
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # 使用模糊匹配搜索查询文本或回答中包含关键词的记录
                    search_pattern = f"%{keyword}%"
                    cur.execute(
                        """
                        SELECT id, user_id, query_text, answer, sources,
                               is_emergency_advice, disclaimer, follow_up_questions,
                               created_at, updated_at
                        FROM medical_queries
                        WHERE user_id = %s AND (query_text ILIKE %s OR answer ILIKE %s)
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, search_pattern, search_pattern, limit, offset)
                    )
                    results = cur.fetchall()
                    
                    queries = []
                    for result in results:
                        # 将JSON格式的来源引用转换为对象列表
                        sources = []
                        if result['sources']:
                            for source_dict in result['sources']:
                                sources.append(SourceReference(
                                    title=source_dict.get('title'),
                                    author=source_dict.get('author'),
                                    publication=source_dict.get('publication'),
                                    url=source_dict.get('url'),
                                    citation=source_dict.get('citation')
                                ))
                        
                        queries.append(MedicalQuery(
                            id=result['id'],
                            user_id=result['user_id'],
                            query_text=result['query_text'],
                            answer=result['answer'],
                            sources=sources,
                            is_emergency_advice=result['is_emergency_advice'],
                            disclaimer=result['disclaimer'],
                            follow_up_questions=result['follow_up_questions'],
                            created_at=result['created_at'],
                            updated_at=result['updated_at']
                        ))
                    
                    return queries
                    
        except Exception as e:
            logger.error(f"搜索用户医疗查询历史记录失败: {str(e)}")
            raise 