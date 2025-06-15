"""
生物识别仓储
管理生物识别认证凭证
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from internal.db.models import BiometricCredential
from .base import BaseRepository

logger = logging.getLogger(__name__)


class BiometricRepository(BaseRepository[BiometricCredential]):
    """生物识别仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BiometricCredential)
    
    async def create_credential(
        self,
        credential_id: str,
        user_id: str,
        public_key: bytes,
        counter: int,
        device_type: str,
        authenticator_data: bytes,
        attestation_object: bytes
    ) -> BiometricCredential:
        """创建生物识别凭证"""
        credential = BiometricCredential(
            credential_id=credential_id,
            user_id=user_id,
            public_key=public_key,
            counter=counter,
            device_type=device_type,
            authenticator_data=authenticator_data,
            attestation_object=attestation_object
        )
        
        self.session.add(credential)
        await self.session.commit()
        await self.session.refresh(credential)
        
        logger.info(f"创建生物识别凭证: user_id={user_id}, credential_id={credential_id}")
        return credential
    
    async def get_credential(self, credential_id: str) -> Optional[BiometricCredential]:
        """根据凭证ID获取凭证"""
        stmt = select(BiometricCredential).where(
            BiometricCredential.credential_id == credential_id
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_credentials(self, user_id: str) -> List[BiometricCredential]:
        """获取用户的所有生物识别凭证"""
        stmt = select(BiometricCredential).where(
            BiometricCredential.user_id == user_id
        ).order_by(BiometricCredential.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_counter(self, credential_id: str, counter: int) -> bool:
        """更新凭证计数器"""
        stmt = update(BiometricCredential).where(
            BiometricCredential.credential_id == credential_id
        ).values(
            counter=counter,
            last_used=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def delete_credential(
        self,
        credential_id: str,
        user_id: str
    ) -> bool:
        """删除生物识别凭证"""
        stmt = delete(BiometricCredential).where(
            and_(
                BiometricCredential.credential_id == credential_id,
                BiometricCredential.user_id == user_id
            )
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0 