#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any


class SourceReference:
    """源引用信息"""
    
    def __init__(self, title: Optional[str] = None, author: Optional[str] = None,
                 publication: Optional[str] = None, url: Optional[str] = None,
                 citation: Optional[str] = None):
        """
        初始化源引用信息
        
        Args:
            title: 标题
            author: 作者
            publication: 出版物
            url: 链接
            citation: 引用格式
        """
        self.title = title
        self.author = author
        self.publication = publication
        self.url = url
        self.citation = citation
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典格式的源引用信息
        """
        return {
            'title': self.title,
            'author': self.author,
            'publication': self.publication,
            'url': self.url,
            'citation': self.citation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SourceReference':
        """
        从字典创建源引用信息
        
        Args:
            data: 字典格式的源引用信息
            
        Returns:
            源引用信息对象
        """
        return cls(
            title=data.get('title'),
            author=data.get('author'),
            publication=data.get('publication'),
            url=data.get('url'),
            citation=data.get('citation')
        )


class MedicalQuery:
    """医疗查询模型"""
    
    def __init__(self, user_id: str, query_text: str, answer: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None, id: Optional[str] = None,
                 is_emergency_advice: bool = False, disclaimer: Optional[str] = None,
                 follow_up_questions: Optional[List[str]] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        """
        初始化医疗查询模型
        
        Args:
            user_id: 用户ID
            query_text: 查询文本
            answer: 回答内容
            sources: 信息来源列表
            id: 查询ID，如果为空则生成新ID
            is_emergency_advice: 是否紧急建议
            disclaimer: 免责声明
            follow_up_questions: 后续问题列表
            created_at: 创建时间
            updated_at: 更新时间
        """
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.query_text = query_text
        self.answer = answer
        self.sources = sources or []
        self.is_emergency_advice = is_emergency_advice
        self.disclaimer = disclaimer
        self.follow_up_questions = follow_up_questions or []
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典格式的医疗查询
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query_text': self.query_text,
            'answer': self.answer,
            'sources': [s.to_dict() for s in self.sources] if self.sources else [],
            'is_emergency_advice': self.is_emergency_advice,
            'disclaimer': self.disclaimer,
            'follow_up_questions': self.follow_up_questions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MedicalQuery':
        """
        从字典创建医疗查询对象
        
        Args:
            data: 字典格式的医疗查询
            
        Returns:
            医疗查询对象
        """
        sources = []
        for source_data in data.get('sources', []):
            sources.append(SourceReference.from_dict(source_data))
        
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']
                
        updated_at = None
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            else:
                updated_at = data['updated_at']
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            query_text=data.get('query_text'),
            answer=data.get('answer'),
            sources=sources,
            is_emergency_advice=data.get('is_emergency_advice', False),
            disclaimer=data.get('disclaimer'),
            follow_up_questions=data.get('follow_up_questions', []),
            created_at=created_at,
            updated_at=updated_at
        ) 