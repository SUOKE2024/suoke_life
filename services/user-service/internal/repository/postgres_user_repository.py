"""
PostgreSQL用户仓库实现模块

该模块实现了基于PostgreSQL的用户数据仓库，作为服务端主数据源。
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from uuid import UUID

from sqlalchemy import create_engine, and_, or_, select, update, delete, insert, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from internal.model.user import (User, UserHealthSummary, DeviceInfo, UserStatus,
                          UserRole, ConstitutionType, HealthMetric)
from internal.repository.exceptions import (UserNotFoundError, UserAlreadyExistsError, 
                                     DeviceNotFoundError, DeviceAlreadyBoundError,
                                     DatabaseError)
from internal.repository.models import Base, User as UserModel, HealthSummary as HealthSummaryModel, Device as DeviceModel

class PostgresUserRepository:
    """PostgreSQL用户仓库实现"""
    
    def __init__(self, connection_string: str):
        """
        初始化PostgreSQL仓库
        
        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """初始化数据库连接"""
        try:
            # 创建所有表（如果不存在）
            # 实际应用中应该使用Alembic管理迁移，这里为了简化直接创建
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("PostgreSQL数据库初始化成功")
        except Exception as e:
            self.logger.error(f"初始化PostgreSQL数据库失败: {e}")
            raise DatabaseError(f"初始化数据库失败: {e}")
    
    def _get_db(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def _model_to_domain_user(self, user_model: UserModel) -> User:
        """将数据库模型转换为领域模型"""
        return User(
            user_id=user_model.user_id,
            username=user_model.username,
            email=user_model.email,
            phone=user_model.phone,
            full_name=user_model.full_name,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            status=UserStatus(user_model.status),
            metadata=user_model.metadata if user_model.metadata else {},
            roles=[UserRole(role) for role in user_model.roles] if user_model.roles else [UserRole.USER],
            preferences=user_model.preferences if user_model.preferences else {}
        )
    
    def _model_to_domain_health_summary(self, summary_model: HealthSummaryModel) -> UserHealthSummary:
        """将健康摘要数据库模型转换为领域模型"""
        # 构建健康指标列表
        recent_metrics = []
        metrics_data = summary_model.recent_metrics if summary_model.recent_metrics else []
        
        for metric_data in metrics_data:
            metric = HealthMetric(
                metric_name=metric_data["metric_name"],
                value=metric_data["value"],
                unit=metric_data.get("unit", ""),
                timestamp=datetime.fromisoformat(metric_data["timestamp"])
            )
            recent_metrics.append(metric)
        
        # 获取主导体质类型
        dominant_constitution = None
        if summary_model.dominant_constitution:
            try:
                dominant_constitution = ConstitutionType(summary_model.dominant_constitution)
            except ValueError:
                pass
        
        return UserHealthSummary(
            user_id=summary_model.user_id,
            health_score=summary_model.health_score,
            dominant_constitution=dominant_constitution,
            constitution_scores=summary_model.constitution_scores if summary_model.constitution_scores else {},
            recent_metrics=recent_metrics,
            last_assessment_date=summary_model.last_assessment_date
        )
    
    def _model_to_domain_device(self, device_model: DeviceModel) -> DeviceInfo:
        """将设备数据库模型转换为领域模型"""
        return DeviceInfo(
            binding_id=device_model.binding_id,
            device_id=device_model.device_id,
            device_type=device_model.device_type,
            device_name=device_model.device_name,
            binding_time=device_model.binding_time,
            is_active=device_model.is_active,
            last_active_time=device_model.last_active_time,
            device_metadata=device_model.device_metadata if device_model.device_metadata else {}
        )
    
    async def create_user(self, username: str, email: str, password_hash: str,
                   phone: Optional[str] = None, full_name: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   user_id: Optional[UUID] = None) -> User:
        """
        创建用户
        
        Args:
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            phone: 电话号码
            full_name: 全名
            metadata: 元数据
            user_id: 可选的用户ID，如果不提供则自动生成
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            UserAlreadyExistsError: 当用户名或邮箱已存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户名和邮箱是否已存在
            query = select(UserModel).where(
                or_(
                    UserModel.username == username,
                    UserModel.email == email
                )
            )
            existing_user = db.execute(query).scalar_one_or_none()
            
            if existing_user:
                if existing_user.username == username:
                    raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
                else:
                    raise UserAlreadyExistsError(f"邮箱 '{email}' 已存在")
            
            # 准备用户数据
            new_user = UserModel(
                user_id=user_id,  # 如果为None，PostgreSQL会自动生成
                username=username,
                email=email,
                password_hash=password_hash,
                phone=phone,
                full_name=full_name,
                status=UserStatus.ACTIVE.value,
                metadata=metadata or {},
                roles=[UserRole.USER.value],
                preferences={}
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # 转换为领域模型并返回
            return self._model_to_domain_user(new_user)
            
        except (UserAlreadyExistsError, DatabaseError):
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            self.logger.error(f"创建用户失败，完整性错误: {e}")
            raise UserAlreadyExistsError(f"用户名或邮箱已存在: {e}")
        except Exception as e:
            db.rollback()
            self.logger.error(f"创建用户失败: {e}")
            raise DatabaseError(f"创建用户失败: {e}")
        finally:
            db.close()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        通过ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象，不存在则返回None
            
        Raises:
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_domain_user(user_model)
            
        except Exception as e:
            self.logger.error(f"获取用户失败: {e}")
            raise DatabaseError(f"获取用户失败: {e}")
        finally:
            db.close()
    
    async def update_user(self, user_id: UUID, username: Optional[str] = None,
                   email: Optional[str] = None, phone: Optional[str] = None,
                   full_name: Optional[str] = None, status: Optional[UserStatus] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> User:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱
            phone: 电话号码
            full_name: 全名
            status: 用户状态
            metadata: 元数据
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            UserNotFoundError: 当用户不存在时
            UserAlreadyExistsError: 当新用户名或邮箱已被其他用户使用时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 如果更新用户名，检查是否与其他用户冲突
            if username and username != user_model.username:
                query = select(UserModel).where(
                    and_(
                        UserModel.username == username,
                        UserModel.user_id != user_id
                    )
                )
                if db.execute(query).scalar_one_or_none():
                    raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
            
            # 如果更新邮箱，检查是否与其他用户冲突
            if email and email != user_model.email:
                query = select(UserModel).where(
                    and_(
                        UserModel.email == email,
                        UserModel.user_id != user_id
                    )
                )
                if db.execute(query).scalar_one_or_none():
                    raise UserAlreadyExistsError(f"邮箱 '{email}' 已存在")
            
            # 准备更新数据
            update_data = {}
            
            if username:
                update_data["username"] = username
            
            if email:
                update_data["email"] = email
            
            if phone is not None:  # 允许设置为None
                update_data["phone"] = phone
            
            if full_name is not None:  # 允许设置为None
                update_data["full_name"] = full_name
            
            if status:
                update_data["status"] = status.value
            
            if metadata:
                update_data["metadata"] = metadata
            
            # 更新时间戳
            update_data["updated_at"] = datetime.now(datetime.timezone.utc)
            
            # 执行更新
            if update_data:
                for key, value in update_data.items():
                    setattr(user_model, key, value)
                
                db.commit()
                db.refresh(user_model)
            
            # 返回更新后的用户
            return self._model_to_domain_user(user_model)
            
        except (UserNotFoundError, UserAlreadyExistsError):
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            self.logger.error(f"更新用户失败，完整性错误: {e}")
            raise UserAlreadyExistsError(f"用户名或邮箱已存在: {e}")
        except Exception as e:
            db.rollback()
            self.logger.error(f"更新用户失败: {e}")
            raise DatabaseError(f"更新用户失败: {e}")
        finally:
            db.close()
    
    async def delete_user(self, user_id: UUID) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 删除用户（注意：健康摘要和设备会通过外键约束自动级联删除）
            db.delete(user_model)
            db.commit()
            
            return True
            
        except UserNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"删除用户失败: {e}")
            raise DatabaseError(f"删除用户失败: {e}")
        finally:
            db.close()
    
    async def list_users(self, offset: int = 0, limit: int = 10,
                  status: Optional[UserStatus] = None) -> Tuple[List[User], int]:
        """
        获取用户列表
        
        Args:
            offset: 分页偏移
            limit: 分页限制
            status: 用户状态过滤
            
        Returns:
            Tuple[List[User], int]: 用户列表和总数
            
        Raises:
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 构建查询条件
            query = select(UserModel)
            count_query = select(func.count()).select_from(UserModel)
            
            if status:
                query = query.where(UserModel.status == status.value)
                count_query = count_query.where(UserModel.status == status.value)
            
            # 查询总数
            total = db.execute(count_query).scalar_one()
            
            # 查询分页数据
            query = query.offset(offset).limit(limit)
            result = db.execute(query).scalars().all()
            
            # 转换为领域模型
            users_list = [self._model_to_domain_user(user) for user in result]
            
            return users_list, total
            
        except Exception as e:
            self.logger.error(f"获取用户列表失败: {e}")
            raise DatabaseError(f"获取用户列表失败: {e}")
        finally:
            db.close()
    
    async def get_user_health_summary(self, user_id: UUID) -> UserHealthSummary:
        """
        获取用户健康摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserHealthSummary: 用户健康摘要
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询健康摘要
            query = select(HealthSummaryModel).where(HealthSummaryModel.user_id == user_id)
            summary_model = db.execute(query).scalar_one_or_none()
            
            if not summary_model:
                # 如果不存在，返回默认健康摘要
                return UserHealthSummary(
                    user_id=user_id,
                    health_score=60,
                    dominant_constitution=None,
                    constitution_scores={},
                    recent_metrics=[],
                    last_assessment_date=None
                )
            
            # 转换为领域模型
            return self._model_to_domain_health_summary(summary_model)
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"获取用户健康摘要失败: {e}")
            raise DatabaseError(f"获取用户健康摘要失败: {e}")
        finally:
            db.close()
    
    async def update_health_summary(self, user_id: UUID, health_score: Optional[int] = None,
                             dominant_constitution: Optional[ConstitutionType] = None,
                             constitution_scores: Optional[Dict[str, float]] = None,
                             recent_metrics: Optional[List[HealthMetric]] = None,
                             last_assessment_date: Optional[datetime] = None) -> UserHealthSummary:
        """
        更新用户健康摘要
        
        Args:
            user_id: 用户ID
            health_score: 健康得分
            dominant_constitution: 主导体质
            constitution_scores: 体质评分
            recent_metrics: 最近测量指标
            last_assessment_date: 最后评估日期
            
        Returns:
            UserHealthSummary: 更新后的健康摘要
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询现有健康摘要
            query = select(HealthSummaryModel).where(HealthSummaryModel.user_id == user_id)
            summary_model = db.execute(query).scalar_one_or_none()
            
            # 如果不存在，创建新记录
            if not summary_model:
                # 准备健康指标JSON
                metrics_json = []
                if recent_metrics:
                    for metric in recent_metrics:
                        metric_json = {
                            "metric_name": metric.metric_name,
                            "value": metric.value,
                            "unit": metric.unit,
                            "timestamp": metric.timestamp.isoformat()
                        }
                        metrics_json.append(metric_json)
                
                # 创建新健康摘要
                summary_model = HealthSummaryModel(
                    user_id=user_id,
                    health_score=health_score if health_score is not None else 60,
                    dominant_constitution=dominant_constitution.value if dominant_constitution else None,
                    constitution_scores=constitution_scores or {},
                    recent_metrics=metrics_json,
                    last_assessment_date=last_assessment_date
                )
                
                db.add(summary_model)
            else:
                # 更新现有记录
                if health_score is not None:
                    summary_model.health_score = health_score
                
                if dominant_constitution is not None:
                    summary_model.dominant_constitution = dominant_constitution.value
                
                if constitution_scores is not None:
                    summary_model.constitution_scores = constitution_scores
                
                if recent_metrics is not None:
                    metrics_json = []
                    for metric in recent_metrics:
                        metric_json = {
                            "metric_name": metric.metric_name,
                            "value": metric.value,
                            "unit": metric.unit,
                            "timestamp": metric.timestamp.isoformat()
                        }
                        metrics_json.append(metric_json)
                    
                    summary_model.recent_metrics = metrics_json
                
                if last_assessment_date is not None:
                    summary_model.last_assessment_date = last_assessment_date
            
            db.commit()
            db.refresh(summary_model)
            
            # 转换为领域模型并返回
            return self._model_to_domain_health_summary(summary_model)
            
        except UserNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"更新健康摘要失败: {e}")
            raise DatabaseError(f"更新健康摘要失败: {e}")
        finally:
            db.close()
    
    async def update_user_preferences(self, user_id: UUID, 
                              preferences: Dict[str, Any]) -> User:
        """
        更新用户偏好设置
        
        Args:
            user_id: 用户ID
            preferences: 偏好设置
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 更新偏好设置
            user_model.preferences = preferences
            user_model.updated_at = datetime.now(datetime.timezone.utc)
            
            db.commit()
            db.refresh(user_model)
            
            # 返回更新后的用户
            return self._model_to_domain_user(user_model)
            
        except UserNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"更新用户偏好设置失败: {e}")
            raise DatabaseError(f"更新用户偏好设置失败: {e}")
        finally:
            db.close()
    
    async def bind_device(self, user_id: UUID, device_id: str, device_type: str,
                   device_name: Optional[str] = None,
                   device_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        绑定设备
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            device_type: 设备类型
            device_name: 设备名称
            device_metadata: 设备元数据
            
        Returns:
            str: 绑定ID
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DeviceAlreadyBoundError: 当设备已绑定时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 检查设备是否已绑定
            query = select(DeviceModel).where(DeviceModel.device_id == device_id)
            existing_device = db.execute(query).scalar_one_or_none()
            
            if existing_device:
                raise DeviceAlreadyBoundError(f"设备ID '{device_id}' 已绑定")
            
            # 创建设备记录
            now = datetime.now(datetime.timezone.utc)
            device_model = DeviceModel(
                user_id=user_id,
                device_id=device_id,
                device_type=device_type,
                device_name=device_name,
                binding_time=now,
                is_active=True,
                last_active_time=now,
                device_metadata=device_metadata or {}
            )
            
            db.add(device_model)
            db.commit()
            db.refresh(device_model)
            
            return str(device_model.binding_id)
            
        except (UserNotFoundError, DeviceAlreadyBoundError):
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            self.logger.error(f"绑定设备失败，完整性错误: {e}")
            raise DeviceAlreadyBoundError(f"设备ID '{device_id}' 已绑定: {e}")
        except Exception as e:
            db.rollback()
            self.logger.error(f"绑定设备失败: {e}")
            raise DatabaseError(f"绑定设备失败: {e}")
        finally:
            db.close()
    
    async def unbind_device(self, user_id: UUID, device_id: str) -> bool:
        """
        解绑设备
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            bool: 是否解绑成功
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DeviceNotFoundError: 当设备不存在或未绑定到该用户时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询设备
            query = select(DeviceModel).where(
                and_(
                    DeviceModel.user_id == user_id,
                    DeviceModel.device_id == device_id
                )
            )
            device_model = db.execute(query).scalar_one_or_none()
            
            if not device_model:
                raise DeviceNotFoundError(f"设备ID '{device_id}' 未绑定到用户ID '{user_id}'")
            
            # 删除设备记录
            db.delete(device_model)
            db.commit()
            
            return True
            
        except (UserNotFoundError, DeviceNotFoundError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"解绑设备失败: {e}")
            raise DatabaseError(f"解绑设备失败: {e}")
        finally:
            db.close()
    
    async def get_user_devices(self, user_id: UUID) -> List[DeviceInfo]:
        """
        获取用户设备列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[DeviceInfo]: 设备列表
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 检查用户是否存在
            query = select(UserModel).where(UserModel.user_id == user_id)
            user_model = db.execute(query).scalar_one_or_none()
            
            if not user_model:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询设备列表
            query = select(DeviceModel).where(DeviceModel.user_id == user_id)
            result = db.execute(query).scalars().all()
            
            # 转换为领域模型
            devices_list = [self._model_to_domain_device(device) for device in result]
            
            return devices_list
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"获取用户设备列表失败: {e}")
            raise DatabaseError(f"获取用户设备列表失败: {e}")
        finally:
            db.close()
    
    async def update_device(self, binding_id: str, 
                     device_name: Optional[str] = None,
                     is_active: Optional[bool] = None,
                     device_metadata: Optional[Dict[str, Any]] = None) -> DeviceInfo:
        """
        更新设备信息
        
        Args:
            binding_id: 绑定ID
            device_name: 设备名称
            is_active: 是否活跃
            device_metadata: 设备元数据
            
        Returns:
            DeviceInfo: 更新后的设备信息
            
        Raises:
            DeviceNotFoundError: 当设备不存在时
            DatabaseError: 数据库操作失败时
        """
        db = self._get_db()
        try:
            # 查询设备
            query = select(DeviceModel).where(DeviceModel.binding_id == UUID(binding_id))
            device_model = db.execute(query).scalar_one_or_none()
            
            if not device_model:
                raise DeviceNotFoundError(f"绑定ID '{binding_id}' 不存在")
            
            # 更新设备信息
            if device_name is not None:
                device_model.device_name = device_name
            
            if is_active is not None:
                device_model.is_active = is_active
            
            if device_metadata is not None:
                device_model.device_metadata = device_metadata
            
            # 更新最后活跃时间
            device_model.last_active_time = datetime.now(datetime.timezone.utc)
            
            db.commit()
            db.refresh(device_model)
            
            # 转换为领域模型并返回
            return self._model_to_domain_device(device_model)
            
        except DeviceNotFoundError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"更新设备信息失败: {e}")
            raise DatabaseError(f"更新设备信息失败: {e}")
        finally:
            db.close()