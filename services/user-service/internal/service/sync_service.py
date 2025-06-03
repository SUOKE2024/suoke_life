"""
数据同步服务模块

该模块实现了SQLite(前端)和PostgreSQL(后端)之间的数据同步机制。
"""
import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from uuid import UUID

from internal.model.user import (User, UserHealthSummary, DeviceInfo, UserStatus,
                          UserRole, ConstitutionType, HealthMetric)
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.repository.postgres_user_repository import PostgresUserRepository
                                     DeviceNotFoundError, DeviceAlreadyBoundError)

class SyncDirection(str, Enum):
    """同步方向枚举"""
    LOCAL_TO_REMOTE = "local_to_remote"  # 本地到远程
    REMOTE_TO_LOCAL = "remote_to_local"  # 远程到本地
    BIDIRECTIONAL = "bidirectional"      # 双向同步

class EntityType(str, Enum):
    """实体类型枚举"""
    USER = "user"
    HEALTH_SUMMARY = "health_summary"
    DEVICE = "device"

class ConflictResolutionStrategy(str, Enum):
    """冲突解决策略枚举"""
    LOCAL_WINS = "local_wins"    # 本地数据优先
    REMOTE_WINS = "remote_wins"  # 远程数据优先
    NEWEST_WINS = "newest_wins"  # 最新修改优先
    MANUAL = "manual"            # 手动解决

class SyncConflict:
    """数据同步冲突记录"""
    
    def __init__(self, entity_type: EntityType, entity_id: str, 
                field: str, local_value: Any, remote_value: Any,
                local_updated_at: Optional[datetime] = None,
                remote_updated_at: Optional[datetime] = None):
        """
        初始化同步冲突
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            field: 冲突字段
            local_value: 本地值
            remote_value: 远程值
            local_updated_at: 本地更新时间
            remote_updated_at: 远程更新时间
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.field = field
        self.local_value = local_value
        self.remote_value = remote_value
        self.local_updated_at = local_updated_at
        self.remote_updated_at = remote_updated_at
        self.resolution = None  # 'local', 'remote', 'merged'
        self.merged_value = None

class SyncResult:
    """同步结果"""
    
    def __init__(self, success: bool, entity_type: EntityType, 
                entity_id: str, direction: SyncDirection):
        """
        初始化同步结果
        
        Args:
            success: 是否成功
            entity_type: 实体类型
            entity_id: 实体ID
            direction: 同步方向
        """
        self.success = success
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.direction = direction
        self.conflicts: List[SyncConflict] = []
        self.error_message: Optional[str] = None
        self.timestamp = datetime.utcnow()

class SyncMetadata:
    """同步元数据"""
    
    def __init__(self, entity_type: EntityType, entity_id: str):
        """
        初始化同步元数据
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.last_sync_time = datetime.utcnow()
        self.local_hash: Optional[str] = None
        self.remote_hash: Optional[str] = None
        self.sync_status = "synced"  # synced, pending, conflict

class SyncService:
    """数据同步服务"""
    
    def __init__(self, 
                 local_repository: SQLiteUserRepository,
                 remote_repository: PostgresUserRepository,
                 default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.REMOTE_WINS):
        """
        初始化同步服务
        
        Args:
            local_repository: 本地仓库
            remote_repository: 远程仓库
            default_strategy: 默认冲突解决策略
        """
        self.local_repo = local_repository
        self.remote_repo = remote_repository
        self.default_strategy = default_strategy
        self.logger = logging.getLogger(__name__)
        self.sync_metadata: Dict[str, SyncMetadata] = {}  # 存储同步元数据，key为"entity_type:entity_id"
    
    async def sync_user(self, user_id: UUID, 
                 direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                 strategy: ConflictResolutionStrategy = None) -> SyncResult:
        """
        同步单个用户数据
        
        Args:
            user_id: 用户ID
            direction: 同步方向
            strategy: 冲突解决策略，不提供则使用默认策略
            
        Returns:
            SyncResult: 同步结果
        """
        result = SyncResult(
            success=True, 
            entity_type=EntityType.USER, 
            entity_id=str(user_id),
            direction=direction
        )
        
        strategy = strategy or self.default_strategy
        
        try:
            # 获取本地和远程用户数据
            local_user = await self.local_repo.get_user_by_id(user_id)
            remote_user = await self.remote_repo.get_user_by_id(user_id)
            
            if not local_user and not remote_user:
                result.success = False
                result.error_message = f"用户 {user_id} 在本地和远程均不存在"
                return result
            
            # 单向同步：本地 -> 远程
            if direction == SyncDirection.LOCAL_TO_REMOTE:
                if not local_user:
                    result.success = False
                    result.error_message = f"用户 {user_id} 在本地不存在，无法同步到远程"
                    return result
                
                if not remote_user:
                    # 远程不存在，直接创建
                    await self.remote_repo.create_user(
                        username=local_user.username,
                        email=local_user.email,
                        password_hash="placeholder",  # 真实场景需要安全处理密码
                        phone=local_user.phone,
                        full_name=local_user.full_name,
                        metadata=local_user.metadata,
                        user_id=user_id
                    )
                else:
                    # 远程存在，检查冲突
                    conflicts = self._detect_user_conflicts(local_user, remote_user)
                    if conflicts:
                        result.conflicts = conflicts
                        resolved_conflicts = await self._resolve_conflicts(
                            conflicts, strategy
                        )
                        
                        # 应用解决方案到远程
                        update_data = self._extract_resolved_user_data(
                            resolved_conflicts, 
                            SyncDirection.LOCAL_TO_REMOTE
                        )
                        
                        if update_data:
                            await self.remote_repo.update_user(
                                user_id=user_id,
                                **update_data
                            )
                    else:
                        # 无冲突，直接更新远程
                        await self.remote_repo.update_user(
                            user_id=user_id,
                            username=local_user.username,
                            email=local_user.email,
                            phone=local_user.phone,
                            full_name=local_user.full_name,
                            status=local_user.status,
                            metadata=local_user.metadata
                        )
            
            # 单向同步：远程 -> 本地
            elif direction == SyncDirection.REMOTE_TO_LOCAL:
                if not remote_user:
                    result.success = False
                    result.error_message = f"用户 {user_id} 在远程不存在，无法同步到本地"
                    return result
                
                if not local_user:
                    # 本地不存在，直接创建
                    await self.local_repo.create_user(
                        username=remote_user.username,
                        email=remote_user.email,
                        password_hash="placeholder",  # 真实场景需要安全处理密码
                        phone=remote_user.phone,
                        full_name=remote_user.full_name,
                        metadata=remote_user.metadata,
                        user_id=user_id
                    )
                else:
                    # 本地存在，检查冲突
                    conflicts = self._detect_user_conflicts(local_user, remote_user)
                    if conflicts:
                        result.conflicts = conflicts
                        resolved_conflicts = await self._resolve_conflicts(
                            conflicts, strategy
                        )
                        
                        # 应用解决方案到本地
                        update_data = self._extract_resolved_user_data(
                            resolved_conflicts, 
                            SyncDirection.REMOTE_TO_LOCAL
                        )
                        
                        if update_data:
                            await self.local_repo.update_user(
                                user_id=user_id,
                                **update_data
                            )
                    else:
                        # 无冲突，直接更新本地
                        await self.local_repo.update_user(
                            user_id=user_id,
                            username=remote_user.username,
                            email=remote_user.email,
                            phone=remote_user.phone,
                            full_name=remote_user.full_name,
                            status=remote_user.status,
                            metadata=remote_user.metadata
                        )
            
            # 双向同步
            else:  # SyncDirection.BIDIRECTIONAL
                if local_user and not remote_user:
                    # 本地有，远程没有，向远程推送
                    await self.remote_repo.create_user(
                        username=local_user.username,
                        email=local_user.email,
                        password_hash="placeholder",  # 真实场景需要安全处理密码
                        phone=local_user.phone,
                        full_name=local_user.full_name,
                        metadata=local_user.metadata,
                        user_id=user_id
                    )
                
                elif not local_user and remote_user:
                    # 远程有，本地没有，向本地拉取
                    await self.local_repo.create_user(
                        username=remote_user.username,
                        email=remote_user.email,
                        password_hash="placeholder",  # 真实场景需要安全处理密码
                        phone=remote_user.phone,
                        full_name=remote_user.full_name,
                        metadata=remote_user.metadata,
                        user_id=user_id
                    )
                
                elif local_user and remote_user:
                    # 两边都有，需要处理冲突
                    conflicts = self._detect_user_conflicts(local_user, remote_user)
                    if conflicts:
                        result.conflicts = conflicts
                        
                        # 如果两边都有更新，根据策略解决冲突
                        resolved_conflicts = await self._resolve_conflicts(
                            conflicts, strategy
                        )
                        
                        # 应用解决方案
                        for conflict in resolved_conflicts:
                            if conflict.resolution == "local":
                                # 本地数据优先，更新远程
                                update_data = {conflict.field: conflict.local_value}
                                await self.remote_repo.update_user(
                                    user_id=user_id,
                                    **update_data
                                )
                            elif conflict.resolution == "remote":
                                # 远程数据优先，更新本地
                                update_data = {conflict.field: conflict.remote_value}
                                await self.local_repo.update_user(
                                    user_id=user_id,
                                    **update_data
                                )
                            elif conflict.resolution == "merged":
                                # 合并数据，更新两边
                                update_data = {conflict.field: conflict.merged_value}
                                await self.local_repo.update_user(
                                    user_id=user_id,
                                    **update_data
                                )
                                await self.remote_repo.update_user(
                                    user_id=user_id,
                                    **update_data
                                )
                            
                        # 如果策略是手动解决，无需应用解决方案
                        if strategy == ConflictResolutionStrategy.MANUAL:
                            result.error_message = "存在未解决的冲突，需要手动解决"
                    
                    # 没有冲突或冲突已解决，将最新的更新时间标记到元数据中
                    if not conflicts or strategy != ConflictResolutionStrategy.MANUAL:
                        metadata_key = f"{EntityType.USER.value}:{user_id}"
                        sync_metadata = SyncMetadata(
                            entity_type=EntityType.USER,
                            entity_id=str(user_id)
                        )
                        
                        # 计算数据哈希，用于后续快速比较
                        sync_metadata.local_hash = self._calculate_entity_hash(local_user)
                        sync_metadata.remote_hash = self._calculate_entity_hash(remote_user)
                        
                        self.sync_metadata[metadata_key] = sync_metadata
                
            return result
            
        except Exception as e:
            self.logger.error(f"同步用户失败: {e}")
            result.success = False
            result.error_message = str(e)
            return result
    
    async def sync_health_summary(self, user_id: UUID,
                          direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                          strategy: ConflictResolutionStrategy = None) -> SyncResult:
        """
        同步用户健康摘要
        
        Args:
            user_id: 用户ID
            direction: 同步方向
            strategy: 冲突解决策略，不提供则使用默认策略
            
        Returns:
            SyncResult: 同步结果
        """
        result = SyncResult(
            success=True,
            entity_type=EntityType.HEALTH_SUMMARY,
            entity_id=str(user_id),
            direction=direction
        )
        
        strategy = strategy or self.default_strategy
        
        try:
            # 获取本地和远程健康摘要
            local_summary = await self.local_repo.get_user_health_summary(user_id)
            remote_summary = await self.remote_repo.get_user_health_summary(user_id)
            
            # 基于同步方向和冲突解决策略进行同步
            # 实现类似sync_user的逻辑，但针对健康摘要
            # 这里简化处理，实际应根据具体字段进行冲突检测和解决
            
            # 示例：仅演示双向同步基本逻辑
            if direction == SyncDirection.BIDIRECTIONAL:
                # 计算健康摘要的哈希值，用于快速判断是否有变化
                local_hash = self._calculate_entity_hash(local_summary)
                remote_hash = self._calculate_entity_hash(remote_summary)
                
                if local_hash != remote_hash:
                    # 存在差异，检查具体冲突字段
                    # 这里可以实现针对健康摘要的冲突检测逻辑
                    
                    # 简化处理：根据策略选择一方数据
                    if strategy == ConflictResolutionStrategy.LOCAL_WINS:
                        # 将本地数据同步到远程的逻辑
                        pass
                    elif strategy == ConflictResolutionStrategy.REMOTE_WINS:
                        # 将远程数据同步到本地的逻辑
                        pass
                    elif strategy == ConflictResolutionStrategy.NEWEST_WINS:
                        # 比较最后评估日期，选择最新的数据
                        if local_summary.last_assessment_date and remote_summary.last_assessment_date:
                            if local_summary.last_assessment_date > remote_summary.last_assessment_date:
                                # 本地更新，同步到远程
                                pass
                            else:
                                # 远程更新，同步到本地
                                pass
                    else:  # MANUAL
                        # 记录冲突，等待手动解决
                        pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"同步健康摘要失败: {e}")
            result.success = False
            result.error_message = str(e)
            return result
    
    async def sync_devices(self, user_id: UUID,
                    direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                    strategy: ConflictResolutionStrategy = None) -> SyncResult:
        """
        同步用户设备列表
        
        Args:
            user_id: 用户ID
            direction: 同步方向
            strategy: 冲突解决策略，不提供则使用默认策略
            
        Returns:
            SyncResult: 同步结果
        """
        result = SyncResult(
            success=True,
            entity_type=EntityType.DEVICE,
            entity_id=str(user_id),
            direction=direction
        )
        
        strategy = strategy or self.default_strategy
        
        try:
            # 获取本地和远程设备列表
            local_devices = await self.local_repo.get_user_devices(user_id)
            remote_devices = await self.remote_repo.get_user_devices(user_id)
            
            # 设备同步的核心逻辑
            # 设备同步需要特别处理，因为它是一个集合而非单个实体
            
            # 获取设备ID集合
            local_device_ids = {device.device_id for device in local_devices}
            remote_device_ids = {device.device_id for device in remote_devices}
            
            # 计算差集
            only_in_local = local_device_ids - remote_device_ids
            only_in_remote = remote_device_ids - local_device_ids
            in_both = local_device_ids.intersection(remote_device_ids)
            
            # 根据同步方向处理
            if direction in [SyncDirection.LOCAL_TO_REMOTE, SyncDirection.BIDIRECTIONAL]:
                # 将本地独有的设备同步到远程
                for device_id in only_in_local:
                    local_device = next(d for d in local_devices if d.device_id == device_id)
                    # 绑定设备到远程
                    await self.remote_repo.bind_device(
                        user_id=user_id,
                        device_id=local_device.device_id,
                        device_type=local_device.device_type,
                        device_name=local_device.device_name,
                        device_metadata=local_device.device_metadata
                    )
            
            if direction in [SyncDirection.REMOTE_TO_LOCAL, SyncDirection.BIDIRECTIONAL]:
                # 将远程独有的设备同步到本地
                for device_id in only_in_remote:
                    remote_device = next(d for d in remote_devices if d.device_id == device_id)
                    # 绑定设备到本地
                    await self.local_repo.bind_device(
                        user_id=user_id,
                        device_id=remote_device.device_id,
                        device_type=remote_device.device_type,
                        device_name=remote_device.device_name,
                        device_metadata=remote_device.device_metadata
                    )
            
            # 处理两边都有的设备，检查元数据和状态是否一致
            for device_id in in_both:
                local_device = next(d for d in local_devices if d.device_id == device_id)
                remote_device = next(d for d in remote_devices if d.device_id == device_id)
                
                # 检测设备冲突并解决
                device_conflicts = self._detect_device_conflicts(local_device, remote_device)
                if device_conflicts:
                    result.conflicts.extend(device_conflicts)
                    # 根据策略解决冲突并更新设备元数据
                    # 实际实现需要根据设备元数据的具体字段进行处理
            
            return result
            
        except Exception as e:
            self.logger.error(f"同步设备列表失败: {e}")
            result.success = False
            result.error_message = str(e)
            return result
    
    async def sync_all_user_data(self, user_id: UUID,
                         direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                         strategy: ConflictResolutionStrategy = None) -> Dict[str, SyncResult]:
        """
        同步用户的所有数据（用户信息、健康摘要、设备）
        
        Args:
            user_id: 用户ID
            direction: 同步方向
            strategy: 冲突解决策略，不提供则使用默认策略
            
        Returns:
            Dict[str, SyncResult]: 各实体类型的同步结果
        """
        results = {}
        
        # 同步用户基本信息
        user_result = await self.sync_user(user_id, direction, strategy)
        results[EntityType.USER.value] = user_result
        
        # 如果用户同步成功，继续同步健康摘要和设备
        if user_result.success:
            # 同步健康摘要
            health_result = await self.sync_health_summary(user_id, direction, strategy)
            results[EntityType.HEALTH_SUMMARY.value] = health_result
            
            # 同步设备
            devices_result = await self.sync_devices(user_id, direction, strategy)
            results[EntityType.DEVICE.value] = devices_result
        
        return results
    
    async def sync_all_users(self, 
                     direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
                     strategy: ConflictResolutionStrategy = None) -> Dict[str, Dict[str, SyncResult]]:
        """
        同步所有用户数据
        
        Args:
            direction: 同步方向
            strategy: 冲突解决策略，不提供则使用默认策略
            
        Returns:
            Dict[str, Dict[str, SyncResult]]: 每个用户的同步结果
        """
        all_results = {}
        
        # 获取本地和远程所有用户
        local_users, _ = await self.local_repo.list_users(0, 9999)
        remote_users, _ = await self.remote_repo.list_users(0, 9999)
        
        # 获取所有用户ID集合
        local_user_ids = {str(user.user_id) for user in local_users}
        remote_user_ids = {str(user.user_id) for user in remote_users}
        
        # 所有用户ID的并集
        all_user_ids = local_user_ids.union(remote_user_ids)
        
        # 同步每个用户
        for user_id in all_user_ids:
            user_results = await self.sync_all_user_data(
                UUID(user_id), direction, strategy
            )
            all_results[user_id] = user_results
        
        return all_results
    
    def _detect_user_conflicts(self, local_user: User, remote_user: User) -> List[SyncConflict]:
        """
        检测用户数据冲突
        
        Args:
            local_user: 本地用户
            remote_user: 远程用户
            
        Returns:
            List[SyncConflict]: 冲突列表
        """
        conflicts = []
        
        # 比较用户字段
        for field in ['username', 'email', 'phone', 'full_name', 'status']:
            local_value = getattr(local_user, field)
            remote_value = getattr(remote_user, field)
            
            if local_value != remote_value:
                conflict = SyncConflict(
                    entity_type=EntityType.USER,
                    entity_id=str(local_user.user_id),
                    field=field,
                    local_value=local_value,
                    remote_value=remote_value,
                    local_updated_at=local_user.updated_at,
                    remote_updated_at=remote_user.updated_at
                )
                conflicts.append(conflict)
        
        # 比较元数据（需要特殊处理字典类型）
        if local_user.metadata != remote_user.metadata:
            conflict = SyncConflict(
                entity_type=EntityType.USER,
                entity_id=str(local_user.user_id),
                field='metadata',
                local_value=local_user.metadata,
                remote_value=remote_user.metadata,
                local_updated_at=local_user.updated_at,
                remote_updated_at=remote_user.updated_at
            )
            conflicts.append(conflict)
        
        # 比较角色
        if set(local_user.roles) != set(remote_user.roles):
            conflict = SyncConflict(
                entity_type=EntityType.USER,
                entity_id=str(local_user.user_id),
                field='roles',
                local_value=local_user.roles,
                remote_value=remote_user.roles,
                local_updated_at=local_user.updated_at,
                remote_updated_at=remote_user.updated_at
            )
            conflicts.append(conflict)
        
        # 比较偏好设置
        if local_user.preferences != remote_user.preferences:
            conflict = SyncConflict(
                entity_type=EntityType.USER,
                entity_id=str(local_user.user_id),
                field='preferences',
                local_value=local_user.preferences,
                remote_value=remote_user.preferences,
                local_updated_at=local_user.updated_at,
                remote_updated_at=remote_user.updated_at
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def _detect_device_conflicts(self, local_device: DeviceInfo, remote_device: DeviceInfo) -> List[SyncConflict]:
        """
        检测设备数据冲突
        
        Args:
            local_device: 本地设备
            remote_device: 远程设备
            
        Returns:
            List[SyncConflict]: 冲突列表
        """
        conflicts = []
        
        # 比较设备字段
        for field in ['device_name', 'device_type', 'is_active']:
            local_value = getattr(local_device, field)
            remote_value = getattr(remote_device, field)
            
            if local_value != remote_value:
                conflict = SyncConflict(
                    entity_type=EntityType.DEVICE,
                    entity_id=local_device.device_id,
                    field=field,
                    local_value=local_value,
                    remote_value=remote_value,
                    local_updated_at=local_device.last_active_time,
                    remote_updated_at=remote_device.last_active_time
                )
                conflicts.append(conflict)
        
        # 比较设备元数据
        if local_device.device_metadata != remote_device.device_metadata:
            conflict = SyncConflict(
                entity_type=EntityType.DEVICE,
                entity_id=local_device.device_id,
                field='device_metadata',
                local_value=local_device.device_metadata,
                remote_value=remote_device.device_metadata,
                local_updated_at=local_device.last_active_time,
                remote_updated_at=remote_device.last_active_time
            )
            conflicts.append(conflict)
        
        return conflicts
    
    async def _resolve_conflicts(self, 
                         conflicts: List[SyncConflict],
                         strategy: ConflictResolutionStrategy) -> List[SyncConflict]:
        """
        解决冲突
        
        Args:
            conflicts: 冲突列表
            strategy: 冲突解决策略
            
        Returns:
            List[SyncConflict]: 解决后的冲突列表
        """
        resolved_conflicts = []
        
        for conflict in conflicts:
            if strategy == ConflictResolutionStrategy.LOCAL_WINS:
                conflict.resolution = "local"
                conflict.merged_value = conflict.local_value
            
            elif strategy == ConflictResolutionStrategy.REMOTE_WINS:
                conflict.resolution = "remote"
                conflict.merged_value = conflict.remote_value
            
            elif strategy == ConflictResolutionStrategy.NEWEST_WINS:
                # 根据更新时间判断
                if conflict.local_updated_at and conflict.remote_updated_at:
                    if conflict.local_updated_at > conflict.remote_updated_at:
                        conflict.resolution = "local"
                        conflict.merged_value = conflict.local_value
                    else:
                        conflict.resolution = "remote"
                        conflict.merged_value = conflict.remote_value
                else:
                    # 如果没有时间戳，默认远程优先
                    conflict.resolution = "remote"
                    conflict.merged_value = conflict.remote_value
            
            elif strategy == ConflictResolutionStrategy.MANUAL:
                # 手动解决，不设置resolution和merged_value
                pass
            
            # 特殊字段的合并逻辑
            if strategy != ConflictResolutionStrategy.MANUAL:
                # 合并元数据字典
                if conflict.field == 'metadata' or conflict.field == 'device_metadata':
                    # 对字典类型，如果策略不是手动解决，可以尝试智能合并
                    merged_dict = self._merge_dictionaries(
                        conflict.local_value, 
                        conflict.remote_value,
                        strategy
                    )
                    conflict.merged_value = merged_dict
                    conflict.resolution = "merged"
                
                # 合并角色列表
                elif conflict.field == 'roles':
                    # 对于角色，可以取并集
                    merged_roles = list(set(conflict.local_value).union(set(conflict.remote_value)))
                    conflict.merged_value = merged_roles
                    conflict.resolution = "merged"
            
            resolved_conflicts.append(conflict)
        
        return resolved_conflicts
    
    def _merge_dictionaries(self, 
                     local_dict: Dict, 
                     remote_dict: Dict,
                     strategy: ConflictResolutionStrategy) -> Dict:
        """
        合并两个字典
        
        Args:
            local_dict: 本地字典
            remote_dict: 远程字典
            strategy: 冲突解决策略
            
        Returns:
            Dict: 合并后的字典
        """
        result = {}
        
        # 获取所有键
        all_keys = set(local_dict.keys()).union(set(remote_dict.keys()))
        
        for key in all_keys:
            # 如果键只在一个字典中存在，直接使用该值
            if key not in local_dict:
                result[key] = remote_dict[key]
            elif key not in remote_dict:
                result[key] = local_dict[key]
            # 如果键在两个字典中都存在，但值不同，根据策略解决
            elif local_dict[key] != remote_dict[key]:
                if strategy == ConflictResolutionStrategy.LOCAL_WINS:
                    result[key] = local_dict[key]
                elif strategy == ConflictResolutionStrategy.REMOTE_WINS:
                    result[key] = remote_dict[key]
                else:
                    # 对于NEWEST_WINS策略，由于无法获知字典中每个键的更新时间，
                    # 这里简化处理，使用远程值
                    result[key] = remote_dict[key]
            else:
                # 值相同，使用任一即可
                result[key] = local_dict[key]
        
        return result
    
    def _extract_resolved_user_data(self, 
                            resolved_conflicts: List[SyncConflict],
                            direction: SyncDirection) -> Dict:
        """
        从已解决的冲突中提取用户更新数据
        
        Args:
            resolved_conflicts: 已解决的冲突列表
            direction: 同步方向
            
        Returns:
            Dict: 更新数据
        """
        update_data = {}
        
        for conflict in resolved_conflicts:
            if direction == SyncDirection.LOCAL_TO_REMOTE:
                # 从本地到远程，使用本地值或合并值
                if conflict.resolution == "local" or conflict.resolution == "merged":
                    update_data[conflict.field] = conflict.merged_value if conflict.resolution == "merged" else conflict.local_value
            
            elif direction == SyncDirection.REMOTE_TO_LOCAL:
                # 从远程到本地，使用远程值或合并值
                if conflict.resolution == "remote" or conflict.resolution == "merged":
                    update_data[conflict.field] = conflict.merged_value if conflict.resolution == "merged" else conflict.remote_value
        
        return update_data
    
    def _calculate_entity_hash(self, entity) -> str:
        """
        计算实体的哈希值，用于快速比较是否有变化
        
        Args:
            entity: 实体对象
            
        Returns:
            str: 哈希值
        """
        # 将实体转换为字典，然后转为JSON字符串，最后计算SHA-256哈希
        try:
            entity_dict = entity.dict() if hasattr(entity, 'dict') else vars(entity)
            
            # 移除不影响同步的字段
            if 'updated_at' in entity_dict:
                del entity_dict['updated_at']
            
            # 将字典转为排序后的JSON字符串
            json_str = json.dumps(entity_dict, sort_keys=True)
            
            # 计算SHA-256哈希
            hash_obj = hashlib.sha256(json_str.encode())
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"计算实体哈希失败: {e}")
            # 返回空字符串表示计算失败
            return ""

# 离线操作管理
class OperationType(str, Enum):
    """操作类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class OfflineOperation:
    """离线操作记录"""
    
    def __init__(self, 
                operation_id: str,
                operation_type: OperationType,
                entity_type: EntityType,
                entity_id: str,
                data: Dict[str, Any],
                timestamp: datetime = None):
        """
        初始化离线操作
        
        Args:
            operation_id: 操作ID
            operation_type: 操作类型
            entity_type: 实体类型
            entity_id: 实体ID
            data: 操作数据
            timestamp: 操作时间戳
        """
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.synced = False
        self.sync_timestamp = None

class OfflineOperationManager:
    """离线操作管理器"""
    
    def __init__(self, sync_service: SyncService):
        """
        初始化离线操作管理器
        
        Args:
            sync_service: 同步服务
        """
        self.sync_service = sync_service
        self.operations: List[OfflineOperation] = []
        self.logger = logging.getLogger(__name__)
    
    def add_operation(self, 
                     operation_type: OperationType,
                     entity_type: EntityType,
                     entity_id: str,
                     data: Dict[str, Any]) -> str:
        """
        添加离线操作
        
        Args:
            operation_type: 操作类型
            entity_type: 实体类型
            entity_id: 实体ID
            data: 操作数据
            
        Returns:
            str: 操作ID
        """
        operation_id = str(uuid.uuid4())
        
        operation = OfflineOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data
        )
        
        self.operations.append(operation)
        return operation_id
    
    async def sync_operations(self, 
                       strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.REMOTE_WINS) -> Dict[str, bool]:
        """
        同步离线操作
        
        Args:
            strategy: 冲突解决策略
            
        Returns:
            Dict[str, bool]: 操作ID和同步结果映射
        """
        results = {}
        
        # 按时间戳排序操作
        sorted_operations = sorted(
            [op for op in self.operations if not op.synced],
            key=lambda op: op.timestamp
        )
        
        for operation in sorted_operations:
            sync_success = await self._sync_operation(operation, strategy)
            results[operation.operation_id] = sync_success
            
            if sync_success:
                operation.synced = True
                operation.sync_timestamp = datetime.utcnow()
        
        return results
    
    async def _sync_operation(self, 
                       operation: OfflineOperation,
                       strategy: ConflictResolutionStrategy) -> bool:
        """
        同步单个操作
        
        Args:
            operation: 离线操作
            strategy: 冲突解决策略
            
        Returns:
            bool: 是否同步成功
        """
        try:
            if operation.entity_type == EntityType.USER:
                if operation.operation_type == OperationType.CREATE:
                    # 创建用户的同步逻辑
                    pass
                elif operation.operation_type == OperationType.UPDATE:
                    # 更新用户的同步逻辑
                    result = await self.sync_service.sync_user(
                        UUID(operation.entity_id),
                        SyncDirection.LOCAL_TO_REMOTE,
                        strategy
                    )
                    return result.success
                elif operation.operation_type == OperationType.DELETE:
                    # 删除用户的同步逻辑
                    pass
            
            elif operation.entity_type == EntityType.HEALTH_SUMMARY:
                # 健康摘要的同步逻辑
                result = await self.sync_service.sync_health_summary(
                    UUID(operation.entity_id),
                    SyncDirection.LOCAL_TO_REMOTE,
                    strategy
                )
                return result.success
            
            elif operation.entity_type == EntityType.DEVICE:
                # 设备的同步逻辑
                if operation.operation_type == OperationType.CREATE:
                    # 绑定设备的同步逻辑
                    pass
                elif operation.operation_type == OperationType.DELETE:
                    # 解绑设备的同步逻辑
                    pass
            
            # 默认返回成功
            return True
            
        except Exception as e:
            self.logger.error(f"同步操作失败: {e}")
            return False