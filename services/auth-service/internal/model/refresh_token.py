#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
刷新令牌模型模块
定义刷新令牌数据模型
"""
import uuid
from datetime import datetime, UTC
from typing import Dict, Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, declarative_base, relationship

# 创建基类
Base = declarative_base()

class RefreshToken(Base):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_value = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)
    client_id = Column(String(100), nullable=True)  # 用于记录客户端设备
    client_info = Column(JSONB, nullable=True)  # 客户端信息（如设备类型、IP等）
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    
    # 关系
    # user = relationship("User", back_populates="refresh_tokens")  # 关联到user模型