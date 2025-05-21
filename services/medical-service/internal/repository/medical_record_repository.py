#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

from internal.model.medical_record import MedicalRecord, Attachment

logger = logging.getLogger(__name__)


class MedicalRecordRepository:
    """医疗记录仓库实现"""
    
    def __init__(self, db_config):
        """
        初始化医疗记录仓库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.user,
            password=self.db_config.password,
            dbname=self.db_config.dbname
        )
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建医疗记录表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medical_records (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        record_type VARCHAR(100) NOT NULL,
                        record_date TIMESTAMP NOT NULL,
                        doctor_id VARCHAR(36),
                        doctor_name VARCHAR(100),
                        institution VARCHAR(200),
                        chief_complaint TEXT,
                        diagnosis TEXT,
                        treatment TEXT,
                        notes TEXT,
                        attachments JSONB,
                        metadata JSONB,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_medical_records_user_id ON medical_records(user_id);
                    CREATE INDEX IF NOT EXISTS idx_medical_records_record_date ON medical_records(record_date);
                    CREATE INDEX IF NOT EXISTS idx_medical_records_record_type ON medical_records(record_type);
                    ''')
                conn.commit()
                logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def _record_to_entity(self, record: Dict[str, Any]) -> MedicalRecord:
        """将数据库记录转换为实体对象"""
        # 处理附件
        attachments = []
        if record["attachments"]:
            for att in record["attachments"]:
                attachments.append(Attachment(
                    id=att["id"],
                    name=att["name"],
                    content_type=att["content_type"],
                    url=att["url"],
                    size=att["size"]
                ))
        
        return MedicalRecord(
            id=record["id"],
            user_id=record["user_id"],
            record_type=record["record_type"],
            record_date=record["record_date"],
            doctor_id=record["doctor_id"],
            doctor_name=record["doctor_name"],
            institution=record["institution"],
            chief_complaint=record["chief_complaint"],
            diagnosis=record["diagnosis"],
            treatment=record["treatment"],
            notes=record["notes"],
            attachments=attachments,
            metadata=record["metadata"] or {},
            created_at=record["created_at"],
            updated_at=record["updated_at"]
        )
    
    def create(self, record: MedicalRecord) -> MedicalRecord:
        """
        创建医疗记录
        
        Args:
            record: 医疗记录
            
        Returns:
            MedicalRecord: 创建的医疗记录
        """
        try:
            # 序列化附件
            attachments_json = []
            for att in record.attachments:
                attachments_json.append({
                    "id": att.id,
                    "name": att.name,
                    "content_type": att.content_type,
                    "url": att.url,
                    "size": att.size
                })
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO medical_records (
                        id, user_id, record_type, record_date, doctor_id, doctor_name,
                        institution, chief_complaint, diagnosis, treatment, notes,
                        attachments, metadata, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        record.id, record.user_id, record.record_type, record.record_date,
                        record.doctor_id, record.doctor_name, record.institution,
                        record.chief_complaint, record.diagnosis, record.treatment,
                        record.notes, json.dumps(attachments_json), json.dumps(record.metadata),
                        record.created_at, record.updated_at
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            return self._record_to_entity(result)
        except Exception as e:
            logger.error(f"Error creating medical record: {str(e)}")
            raise
    
    def get_by_id(self, record_id: str) -> Optional[MedicalRecord]:
        """
        通过ID获取医疗记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[MedicalRecord]: 医疗记录，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM medical_records WHERE id = %s', (record_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return self._record_to_entity(result)
                    return None
        except Exception as e:
            logger.error(f"Error getting medical record by ID: {str(e)}")
            raise
    
    def list(self, filters: Dict[str, Any], page: int = 1, page_size: int = 10) -> Tuple[List[MedicalRecord], int]:
        """
        列出医疗记录
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[MedicalRecord], int]: 医疗记录列表和总记录数
        """
        try:
            query_conditions = []
            query_params = []
            
            # 处理过滤条件
            if "user_id" in filters:
                query_conditions.append("user_id = %s")
                query_params.append(filters["user_id"])
                
            if "record_type" in filters:
                query_conditions.append("record_type = %s")
                query_params.append(filters["record_type"])
                
            if "start_date" in filters:
                query_conditions.append("record_date >= %s")
                query_params.append(filters["start_date"])
                
            if "end_date" in filters:
                query_conditions.append("record_date <= %s")
                query_params.append(filters["end_date"])
            
            # 构建查询条件
            where_clause = ""
            if query_conditions:
                where_clause = "WHERE " + " AND ".join(query_conditions)
            
            # 计算总记录数
            count_query = f"SELECT COUNT(*) as total FROM medical_records {where_clause}"
            
            # 查询分页数据
            offset = (page - 1) * page_size
            data_query = f'''
            SELECT * FROM medical_records
            {where_clause}
            ORDER BY record_date DESC
            LIMIT %s OFFSET %s
            '''
            query_params.extend([page_size, offset])
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取总记录数
                    cursor.execute(count_query, query_params[:-2] if query_params else None)
                    total = cursor.fetchone()["total"]
                    
                    # 获取分页数据
                    cursor.execute(data_query, query_params)
                    results = cursor.fetchall()
                    
                    records = []
                    for result in results:
                        records.append(self._record_to_entity(result))
                    
                    return records, total
        except Exception as e:
            logger.error(f"Error listing medical records: {str(e)}")
            raise
    
    def update(self, record: MedicalRecord) -> MedicalRecord:
        """
        更新医疗记录
        
        Args:
            record: 医疗记录
            
        Returns:
            MedicalRecord: 更新后的医疗记录
        """
        try:
            # 序列化附件
            attachments_json = []
            for att in record.attachments:
                attachments_json.append({
                    "id": att.id,
                    "name": att.name,
                    "content_type": att.content_type,
                    "url": att.url,
                    "size": att.size
                })
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    UPDATE medical_records SET
                        record_type = %s,
                        record_date = %s,
                        doctor_id = %s,
                        doctor_name = %s,
                        institution = %s,
                        chief_complaint = %s,
                        diagnosis = %s,
                        treatment = %s,
                        notes = %s,
                        attachments = %s,
                        metadata = %s,
                        updated_at = %s
                    WHERE id = %s
                    RETURNING *
                    ''', (
                        record.record_type, record.record_date, record.doctor_id,
                        record.doctor_name, record.institution, record.chief_complaint,
                        record.diagnosis, record.treatment, record.notes,
                        json.dumps(attachments_json), json.dumps(record.metadata),
                        record.updated_at, record.id
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            if result:
                return self._record_to_entity(result)
            raise ValueError(f"Medical record with ID {record.id} not found")
        except Exception as e:
            logger.error(f"Error updating medical record: {str(e)}")
            raise
    
    def delete(self, record_id: str) -> bool:
        """
        删除医疗记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('DELETE FROM medical_records WHERE id = %s', (record_id,))
                    deleted = cursor.rowcount > 0
                conn.commit()
            return deleted
        except Exception as e:
            logger.error(f"Error deleting medical record: {str(e)}")
            raise 