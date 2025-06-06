"""
sqlite_user_repository - 索克生活项目模块
"""

from datetime import datetime, timezone
from internal.model.user import (User, UserHealthSummary, DeviceInfo, UserStatus,
from internal.repository.exceptions import (UserNotFoundError, UserAlreadyExistsError, 
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import json
import logging
import os
import sqlite3
import uuid

"""
SQLite用户仓库实现模块

该模块实现了基于SQLite的用户数据存储，作为前端本地存储方案。
"""

                          UserRole, ConstitutionType, HealthMetric)
                                     DeviceNotFoundError, DeviceAlreadyBoundError,
                                     DatabaseError)

class SQLiteUserRepository:
    """SQLite用户仓库实现"""
    
    def __init__(self, db_path: str):
        """
        初始化SQLite仓库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """初始化数据库表结构"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                phone TEXT,
                full_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                roles TEXT,
                preferences TEXT
            )
            ''')
            
            # 创建健康摘要表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_summaries (
                user_id TEXT PRIMARY KEY,
                health_score INTEGER,
                dominant_constitution TEXT,
                constitution_scores TEXT,
                recent_metrics TEXT,
                last_assessment_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
            ''')
            
            # 创建设备表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                binding_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                device_type TEXT NOT NULL,
                device_name TEXT,
                binding_time TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                last_active_time TEXT NOT NULL,
                device_metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                UNIQUE (user_id, device_id)
            )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices (device_id)')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"SQLite数据库初始化成功: {self.db_path}")
        except Exception as e:
            self.logger.error(f"初始化SQLite数据库失败: {e}")
            raise DatabaseError(f"初始化数据库失败: {e}")
    
    async def create_user(self, username: str, email: str, password_hash: str,
                   phone: Optional[str] = None, full_name: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None,
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户名和邮箱是否已存在
            cursor.execute('SELECT username, email FROM users WHERE username = ? OR email = ?', 
                          (username, email))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                if existing[0] == username:
                    raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
                else:
                    raise UserAlreadyExistsError(f"邮箱 '{email}' 已存在")
            
            # 准备用户数据
            user_id = user_id or uuid.uuid4()
            now = datetime.now(timezone.utc).isoformat()
            metadata = metadata or {}
            roles = [UserRole.USER.value]
            preferences = {}
            
            # 插入用户记录
            cursor.execute('''
            INSERT INTO users 
            (user_id, username, email, password_hash, phone, full_name, 
             created_at, updated_at, status, metadata, roles, preferences)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(user_id),
                username,
                email,
                password_hash,
                phone,
                full_name,
                now,
                now,
                UserStatus.ACTIVE.value,
                json.dumps(metadata),
                json.dumps(roles),
                json.dumps(preferences)
            ))
            
            conn.commit()
            conn.close()
            
            # 返回用户对象
            return User(
                user_id=user_id,
                username=username,
                email=email,
                phone=phone,
                full_name=full_name,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
                status=UserStatus.ACTIVE,
                metadata=metadata,
                roles=[UserRole.USER],
                preferences=preferences
            )
            
        except (UserAlreadyExistsError, DatabaseError):
            raise
        except Exception as e:
            self.logger.error(f"创建用户失败: {e}")
            raise DatabaseError(f"创建用户失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使用字典形式返回结果
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM users WHERE user_id = ?
            ''', (str(user_id),))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            # 转换回User对象
            return User(
                user_id=UUID(row['user_id']),
                username=row['username'],
                email=row['email'],
                phone=row['phone'],
                full_name=row['full_name'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                status=UserStatus(row['status']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                roles=[UserRole(role) for role in json.loads(row['roles'])],
                preferences=json.loads(row['preferences']) if row['preferences'] else {}
            )
            
        except Exception as e:
            self.logger.error(f"获取用户失败: {e}")
            raise DatabaseError(f"获取用户失败: {e}")
    
    async def update_user(self, user_id: UUID, username: Optional[str] = None,
                   email: Optional[str] = None, phone: Optional[str] = None,
                   full_name: Optional[str] = None, status: Optional[UserStatus] = None,
                   metadata: Optional[Dict[str, str]] = None) -> User:
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 如果更新用户名，检查是否与其他用户冲突
            if username:
                cursor.execute('SELECT COUNT(*) FROM users WHERE username = ? AND user_id != ?', 
                               (username, str(user_id)))
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
            
            # 如果更新邮箱，检查是否与其他用户冲突
            if email:
                cursor.execute('SELECT COUNT(*) FROM users WHERE email = ? AND user_id != ?', 
                               (email, str(user_id)))
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    raise UserAlreadyExistsError(f"邮箱 '{email}' 已存在")
            
            # 获取当前用户数据
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(user_id),))
            current_user = cursor.fetchone()
            
            # 准备更新数据
            update_fields = []
            params = []
            
            if username:
                update_fields.append('username = ?')
                params.append(username)
            
            if email:
                update_fields.append('email = ?')
                params.append(email)
            
            if phone is not None:  # 允许设置为None
                update_fields.append('phone = ?')
                params.append(phone)
            
            if full_name is not None:  # 允许设置为None
                update_fields.append('full_name = ?')
                params.append(full_name)
            
            if status:
                update_fields.append('status = ?')
                params.append(status.value)
            
            if metadata:
                update_fields.append('metadata = ?')
                params.append(json.dumps(metadata))
            
            # 更新时间戳
            update_fields.append('updated_at = ?')
            now = datetime.now(timezone.utc).isoformat()
            params.append(now)
            
            # 执行更新
            params.append(str(user_id))  # WHERE条件的参数
            
            cursor.execute(f'''
            UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?
            ''', params)
            
            conn.commit()
            conn.close()
            
            # 返回更新后的用户
            return await self.get_user_by_id(user_id)
            
        except (UserNotFoundError, UserAlreadyExistsError, DatabaseError):
            raise
        except Exception as e:
            self.logger.error(f"更新用户失败: {e}")
            raise DatabaseError(f"更新用户失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 删除用户及关联数据（SQLite外键级联删除）
            cursor.execute('DELETE FROM users WHERE user_id = ?', (str(user_id),))
            
            conn.commit()
            conn.close()
            
            return True
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"删除用户失败: {e}")
            raise DatabaseError(f"删除用户失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            
            if status:
                where_clause = "WHERE status = ?"
                params.append(status.value)
            
            # 查询总数
            count_query = f"SELECT COUNT(*) FROM users {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # 查询分页数据
            query = f"SELECT * FROM users {where_clause} LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            users_list = []
            for row in rows:
                user = User(
                    user_id=UUID(row['user_id']),
                    username=row['username'],
                    email=row['email'],
                    phone=row['phone'],
                    full_name=row['full_name'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    status=UserStatus(row['status']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    roles=[UserRole(role) for role in json.loads(row['roles'])],
                    preferences=json.loads(row['preferences']) if row['preferences'] else {}
                )
                users_list.append(user)
            
            conn.close()
            return users_list, total
            
        except Exception as e:
            self.logger.error(f"获取用户列表失败: {e}")
            raise DatabaseError(f"获取用户列表失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询健康摘要
            cursor.execute('''
            SELECT * FROM health_summaries WHERE user_id = ?
            ''', (str(user_id),))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                # 如果不存在，返回默认健康摘要
                return UserHealthSummary(
                    user_id=user_id,
                    health_score=60,
                    dominant_constitution=None,
                    constitution_scores={},
                    recent_metrics=[],
                    last_assessment_date=None
                )
            
            # 构建健康指标列表
            recent_metrics = []
            metrics_data = json.loads(row['recent_metrics']) if row['recent_metrics'] else []
            
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
            if row['dominant_constitution']:
                try:
                    dominant_constitution = ConstitutionType(row['dominant_constitution'])
                except ValueError:
                    pass
            
            # 获取上次评估时间
            last_assessment_date = None
            if row['last_assessment_date']:
                last_assessment_date = datetime.fromisoformat(row['last_assessment_date'])
            
            # 构建并返回健康摘要
            return UserHealthSummary(
                user_id=user_id,
                health_score=row['health_score'],
                dominant_constitution=dominant_constitution,
                constitution_scores=json.loads(row['constitution_scores']) if row['constitution_scores'] else {},
                recent_metrics=recent_metrics,
                last_assessment_date=last_assessment_date
            )
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"获取用户健康摘要失败: {e}")
            raise DatabaseError(f"获取用户健康摘要失败: {e}")
    
    async def update_user_preferences(self, user_id: UUID, 
                              preferences: Dict[str, str]) -> User:
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 更新偏好设置
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute('''
            UPDATE users SET preferences = ?, updated_at = ? WHERE user_id = ?
            ''', (json.dumps(preferences), now, str(user_id)))
            
            conn.commit()
            conn.close()
            
            # 返回更新后的用户
            return await self.get_user_by_id(user_id)
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"更新用户偏好设置失败: {e}")
            raise DatabaseError(f"更新用户偏好设置失败: {e}")
    
    async def bind_device(self, user_id: UUID, device_id: str, device_type: str,
                   device_name: Optional[str] = None,
                   device_metadata: Optional[Dict[str, str]] = None) -> str:
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 检查设备是否已绑定
            cursor.execute('SELECT COUNT(*) FROM devices WHERE device_id = ?', (device_id,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise DeviceAlreadyBoundError(f"设备ID '{device_id}' 已绑定")
            
            # 生成绑定ID
            binding_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            
            # 插入设备记录
            cursor.execute('''
            INSERT INTO devices 
            (binding_id, user_id, device_id, device_type, device_name, 
             binding_time, is_active, last_active_time, device_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                binding_id,
                str(user_id),
                device_id,
                device_type,
                device_name,
                now,
                1,  # is_active
                now,
                json.dumps(device_metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            return binding_id
            
        except (UserNotFoundError, DeviceAlreadyBoundError):
            raise
        except Exception as e:
            self.logger.error(f"绑定设备失败: {e}")
            raise DatabaseError(f"绑定设备失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 检查设备是否绑定到该用户
            cursor.execute('''
            SELECT COUNT(*) FROM devices 
            WHERE user_id = ? AND device_id = ?
            ''', (str(user_id), device_id))
            
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise DeviceNotFoundError(f"设备ID '{device_id}' 未绑定到用户ID '{user_id}'")
            
            # 删除设备记录
            cursor.execute('''
            DELETE FROM devices 
            WHERE user_id = ? AND device_id = ?
            ''', (str(user_id), device_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except (UserNotFoundError, DeviceNotFoundError):
            raise
        except Exception as e:
            self.logger.error(f"解绑设备失败: {e}")
            raise DatabaseError(f"解绑设备失败: {e}")
    
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
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (str(user_id),))
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            # 查询设备列表
            cursor.execute('''
            SELECT * FROM devices WHERE user_id = ?
            ''', (str(user_id),))
            
            rows = cursor.fetchall()
            conn.close()
            
            devices_list = []
            for row in rows:
                device = DeviceInfo(
                    binding_id=row['binding_id'],
                    device_id=row['device_id'],
                    device_type=row['device_type'],
                    device_name=row['device_name'],
                    binding_time=datetime.fromisoformat(row['binding_time']),
                    is_active=bool(row['is_active']),
                    last_active_time=datetime.fromisoformat(row['last_active_time']),
                    device_metadata=json.loads(row['device_metadata']) if row['device_metadata'] else {}
                )
                devices_list.append(device)
            
            return devices_list
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"获取用户设备列表失败: {e}")
            raise DatabaseError(f"获取用户设备列表失败: {e}")
    
    async def count_active_users(self) -> int:
        """
        统计活跃用户数
        
        Returns:
            int: 活跃用户数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE status = ?",
                (UserStatus.ACTIVE.value,)
            )
            row = cursor.fetchone()
            conn.close()
            
            return row[0] if row else 0
        except Exception as e:
            self.logger.error(f"统计活跃用户数失败: {e}")
            raise DatabaseError(f"统计活跃用户数失败: {e}")
    
    async def count_device_bindings(self) -> int:
        """
        统计设备绑定总数
        
        Returns:
            int: 设备绑定总数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM devices WHERE is_active = 1"
            )
            row = cursor.fetchone()
            conn.close()
            
            return row[0] if row else 0
        except Exception as e:
            self.logger.error(f"统计设备绑定总数失败: {e}")
            raise DatabaseError(f"统计设备绑定总数失败: {e}")
    
    async def count_health_summaries(self) -> int:
        """
        统计健康摘要总数
        
        Returns:
            int: 健康摘要总数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM health_summaries"
            )
            row = cursor.fetchone()
            conn.close()
            
            return row[0] if row else 0
        except Exception as e:
            self.logger.error(f"统计健康摘要总数失败: {e}")
            raise DatabaseError(f"统计健康摘要总数失败: {e}")
    
    async def check_connection(self) -> bool:
        """
        检查数据库连接状态
        
        Returns:
            bool: 连接是否正常
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            return result is not None and result[0] == 1
        except Exception as e:
            self.logger.error(f"数据库连接检查失败: {e}")
            return False