#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from internal.model.medical_record import MedicalRecord, Attachment

logger = logging.getLogger(__name__)


class MedicalRecordService:
    """医疗记录服务实现"""
    
    def __init__(self, repository):
        """
        初始化医疗记录服务
        
        Args:
            repository: 医疗记录仓库
        """
        self.repository = repository
    
    def create_medical_record(self, user_id: str, record_type: str, record_date: datetime,
                             doctor_id: Optional[str] = None, doctor_name: Optional[str] = None,
                             institution: Optional[str] = None, chief_complaint: Optional[str] = None,
                             diagnosis: Optional[str] = None, treatment: Optional[str] = None,
                             notes: Optional[str] = None, attachments: Optional[List[Dict[str, Any]]] = None,
                             metadata: Optional[Dict[str, str]] = None) -> MedicalRecord:
        """
        创建医疗记录
        
        Args:
            user_id: 用户ID
            record_type: 记录类型
            record_date: 记录日期
            doctor_id: 医生ID
            doctor_name: 医生姓名
            institution: 医疗机构
            chief_complaint: 主诉
            diagnosis: 诊断
            treatment: 治疗方案
            notes: 备注
            attachments: 附件列表
            metadata: 元数据
            
        Returns:
            MedicalRecord: 创建的医疗记录
        """
        logger.info(f"Creating medical record for user {user_id}")
        
        # 处理附件
        attachment_objects = []
        if attachments:
            for att in attachments:
                attachment_objects.append(
                    Attachment.create(
                        name=att["name"],
                        content_type=att["content_type"],
                        url=att["url"],
                        size=att["size"]
                    )
                )
        
        # 创建记录模型
        record = MedicalRecord.create(
            user_id=user_id,
            record_type=record_type,
            record_date=record_date,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            institution=institution,
            chief_complaint=chief_complaint,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            attachments=attachment_objects,
            metadata=metadata
        )
        
        # 保存到仓库
        saved_record = self.repository.create(record)
        logger.info(f"Created medical record with ID {saved_record.id}")
        
        return saved_record
    
    def get_medical_record(self, record_id: str) -> Optional[MedicalRecord]:
        """
        获取医疗记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[MedicalRecord]: 医疗记录，如果不存在则返回None
        """
        logger.info(f"Getting medical record with ID {record_id}")
        return self.repository.get_by_id(record_id)
    
    def list_medical_records(self, filters: Dict[str, Any], page: int = 1, page_size: int = 10) -> Tuple[List[MedicalRecord], int]:
        """
        列出医疗记录
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[MedicalRecord], int]: 医疗记录列表和总记录数
        """
        user_id = filters.get("user_id")
        logger.info(f"Listing medical records for user {user_id}, page {page}, page_size {page_size}")
        
        return self.repository.list(filters, page, page_size)
    
    def update_medical_record(self, record_id: str, record_type: Optional[str] = None,
                             record_date: Optional[datetime] = None, doctor_id: Optional[str] = None,
                             doctor_name: Optional[str] = None, institution: Optional[str] = None,
                             chief_complaint: Optional[str] = None, diagnosis: Optional[str] = None,
                             treatment: Optional[str] = None, notes: Optional[str] = None,
                             attachments: Optional[List[Dict[str, Any]]] = None,
                             metadata: Optional[Dict[str, str]] = None) -> Optional[MedicalRecord]:
        """
        更新医疗记录
        
        Args:
            record_id: 记录ID
            record_type: 记录类型
            record_date: 记录日期
            doctor_id: 医生ID
            doctor_name: 医生姓名
            institution: 医疗机构
            chief_complaint: 主诉
            diagnosis: 诊断
            treatment: 治疗方案
            notes: 备注
            attachments: 附件列表
            metadata: 元数据
            
        Returns:
            Optional[MedicalRecord]: 更新后的医疗记录，如果记录不存在则返回None
        """
        logger.info(f"Updating medical record with ID {record_id}")
        
        # 获取现有记录
        record = self.repository.get_by_id(record_id)
        if not record:
            logger.warning(f"Medical record with ID {record_id} not found")
            return None
        
        # 处理附件
        attachment_objects = None
        if attachments is not None:
            attachment_objects = []
            for att in attachments:
                attachment_objects.append(
                    Attachment.create(
                        name=att["name"],
                        content_type=att["content_type"],
                        url=att["url"],
                        size=att["size"]
                    )
                )
        
        # 更新记录
        record.update(
            record_type=record_type,
            record_date=record_date,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            institution=institution,
            chief_complaint=chief_complaint,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            attachments=attachment_objects,
            metadata=metadata
        )
        
        # 保存到仓库
        updated_record = self.repository.update(record)
        logger.info(f"Updated medical record with ID {updated_record.id}")
        
        return updated_record
    
    def delete_medical_record(self, record_id: str) -> bool:
        """
        删除医疗记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 是否成功删除
        """
        logger.info(f"Deleting medical record with ID {record_id}")
        return self.repository.delete(record_id) 