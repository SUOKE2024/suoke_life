#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class Attachment:
    id: str
    name: str
    content_type: str
    url: str
    size: int
    
    @classmethod
    def create(cls, name: str, content_type: str, url: str, size: int) -> 'Attachment':
        """创建新的附件"""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            content_type=content_type,
            url=url,
            size=size
        )


@dataclass
class MedicalRecord:
    id: str
    user_id: str
    record_type: str  # 例如：常规检查，慢性病随访，急诊等
    record_date: datetime
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    institution: Optional[str] = None
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, user_id: str, record_type: str, record_date: datetime,
               doctor_id: Optional[str] = None, doctor_name: Optional[str] = None,
               institution: Optional[str] = None, chief_complaint: Optional[str] = None,
               diagnosis: Optional[str] = None, treatment: Optional[str] = None,
               notes: Optional[str] = None, attachments: Optional[List[Attachment]] = None,
               metadata: Optional[Dict[str, str]] = None) -> 'MedicalRecord':
        """创建新的医疗记录"""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
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
            attachments=attachments or [],
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        )
    
    def update(self, record_type: Optional[str] = None, record_date: Optional[datetime] = None,
               doctor_id: Optional[str] = None, doctor_name: Optional[str] = None,
               institution: Optional[str] = None, chief_complaint: Optional[str] = None,
               diagnosis: Optional[str] = None, treatment: Optional[str] = None,
               notes: Optional[str] = None, attachments: Optional[List[Attachment]] = None,
               metadata: Optional[Dict[str, str]] = None) -> None:
        """更新医疗记录"""
        if record_type is not None:
            self.record_type = record_type
        if record_date is not None:
            self.record_date = record_date
        if doctor_id is not None:
            self.doctor_id = doctor_id
        if doctor_name is not None:
            self.doctor_name = doctor_name
        if institution is not None:
            self.institution = institution
        if chief_complaint is not None:
            self.chief_complaint = chief_complaint
        if diagnosis is not None:
            self.diagnosis = diagnosis
        if treatment is not None:
            self.treatment = treatment
        if notes is not None:
            self.notes = notes
        if attachments is not None:
            self.attachments = attachments
        if metadata is not None:
            self.metadata = metadata
        self.updated_at = datetime.now()
    
    def add_attachment(self, attachment: Attachment) -> None:
        """添加附件"""
        self.attachments.append(attachment)
        self.updated_at = datetime.now()
    
    def remove_attachment(self, attachment_id: str) -> bool:
        """移除附件"""
        initial_length = len(self.attachments)
        self.attachments = [a for a in self.attachments if a.id != attachment_id]
        if len(self.attachments) < initial_length:
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_metadata(self, key: str, value: str) -> None:
        """添加元数据"""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def remove_metadata(self, key: str) -> bool:
        """移除元数据"""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.now()
            return True
        return False 