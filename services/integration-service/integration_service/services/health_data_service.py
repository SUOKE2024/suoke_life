"""
health_data_service - 索克生活项目模块
"""

from ..models.health_data import HealthData, HealthDataType
from ..models.platform import Platform
from .base_service import BaseService
from datetime import datetime, date, timedelta
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

"""
健康数据服务模块
"""




logger = logging.getLogger(__name__)


class HealthDataService(BaseService[HealthData]):
    """健康数据服务类"""
    
    def __init__(self, db: Session):
        super().__init__(HealthData, db)
    
    def get_health_data_by_id(self, data_id: int) -> Optional[HealthData]:
        """根据ID获取健康数据"""
        try:
            return self.db.query(HealthData).filter(HealthData.id == data_id).first()
        except Exception as e:
            logger.error(f"获取健康数据失败: {e}")
            return None
    
    def get_user_health_data(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        platform_id: Optional[str] = None,
        data_type: Optional[HealthDataType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[HealthData]:
        """获取用户健康数据列表"""
        try:
            query = self.db.query(HealthData).filter(HealthData.user_id == user_id)
            
            # 平台筛选
            if platform_id:
                query = query.filter(HealthData.platform_id == platform_id)
            
            # 数据类型筛选
            if data_type:
                query = query.filter(HealthData.data_type == data_type)
            
            # 日期范围筛选
            if start_date:
                query = query.filter(HealthData.created_at >= start_date)
            if end_date:
                query = query.filter(HealthData.created_at <= end_date)
            
            # 排序和分页
            query = query.order_by(HealthData.created_at.desc())
            query = query.offset(skip).limit(limit)
            
            return query.all()[:1000]  # 限制查询结果数量
            
        except Exception as e:
            logger.error(f"获取用户健康数据失败: {e}")
            return []
    
    def create_health_data(
        self,
        user_id: str,
        platform_id: str,
        data_type: HealthDataType,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None
    ) -> Optional[HealthData]:
        """创建健康数据记录"""
        try:
            health_data = HealthData(
                user_id=user_id,
                platform_id=platform_id,
                data_type=data_type,
                value=value,
                unit=unit,
                extra_data=extra_data or {},
                source_id=source_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(health_data)
            self.db.commit()
            self.db.refresh(health_data)
            
            logger.info(f"创建健康数据记录成功: {health_data.id}")
            return health_data
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建健康数据失败: {e}")
            return None
    
    def create_health_data_batch(
        self,
        user_id: str,
        platform_id: str,
        data_list: List[Dict[str, Any]]
    ) -> int:
        """批量创建健康数据记录"""
        try:
            created_count = 0
            
            for data_item in data_list:
                try:
                    # 验证必需字段
                    if 'data_type' not in data_item:
                        continue
                    
                    data_type = HealthDataType(data_item['data_type'])
                    
                    health_data = HealthData(
                        user_id=user_id,
                        platform_id=platform_id,
                        data_type=data_type,
                        value=data_item.get('value'),
                        unit=data_item.get('unit'),
                        extra_data=data_item.get('extra_data', {}),
                        source_id=data_item.get('source_id'),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    self.db.add(health_data)
                    created_count += 1
                    
                except Exception as item_error:
                    logger.warning(f"跳过无效数据项: {item_error}")
                    continue
            
            self.db.commit()
            logger.info(f"批量创建健康数据成功，共创建 {created_count} 条记录")
            return created_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量创建健康数据失败: {e}")
            return 0
    
    def update_health_data(
        self,
        data_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[HealthData]:
        """更新健康数据记录"""
        try:
            health_data = self.get_health_data_by_id(data_id)
            if not health_data:
                return None
            
            # 更新字段
            for field, value in update_data.items():
                if hasattr(health_data, field):
                    setattr(health_data, field, value)
            
            # 更新时间戳
            health_data.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(health_data)
            
            logger.info(f"健康数据 {data_id} 更新成功")
            return health_data
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新健康数据失败: {e}")
            return None
    
    def delete_health_data(self, data_id: int) -> bool:
        """删除健康数据记录"""
        try:
            health_data = self.get_health_data_by_id(data_id)
            if not health_data:
                return False
            
            self.db.delete(health_data)
            self.db.commit()
            
            logger.info(f"健康数据 {data_id} 删除成功")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除健康数据失败: {e}")
            return False
    
    def get_user_health_data_stats(
        self,
        user_id: str,
        platform_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """获取用户健康数据统计"""
        try:
            query = self.db.query(HealthData).filter(HealthData.user_id == user_id)
            
            # 应用筛选条件
            if platform_id:
                query = query.filter(HealthData.platform_id == platform_id)
            if start_date:
                query = query.filter(HealthData.created_at >= start_date)
            if end_date:
                query = query.filter(HealthData.created_at <= end_date)
            
            # 总数统计
            total_count = query.count()
            
            # 按数据类型统计
            data_type_stats = self.db.query(
                HealthData.data_type,
                func.count(HealthData.id).label('count')
            ).filter(HealthData.user_id == user_id)
            
            if platform_id:
                data_type_stats = data_type_stats.filter(HealthData.platform_id == platform_id)
            if start_date:
                data_type_stats = data_type_stats.filter(HealthData.created_at >= start_date)
            if end_date:
                data_type_stats = data_type_stats.filter(HealthData.created_at <= end_date)
            
            data_type_counts = {
                item.data_type.value: item.count 
                for item in data_type_stats.group_by(HealthData.data_type).all()[:1000]  # 限制查询结果数量
            }
            
            # 按平台统计
            platform_stats = self.db.query(
                HealthData.platform_id,
                func.count(HealthData.id).label('count')
            ).filter(HealthData.user_id == user_id)
            
            if platform_id:
                platform_stats = platform_stats.filter(HealthData.platform_id == platform_id)
            if start_date:
                platform_stats = platform_stats.filter(HealthData.created_at >= start_date)
            if end_date:
                platform_stats = platform_stats.filter(HealthData.created_at <= end_date)
            
            platform_counts = {
                item.platform_id: item.count 
                for item in platform_stats.group_by(HealthData.platform_id).all()[:1000]  # 限制查询结果数量
            }
            
            # 日期范围
            date_range_query = self.db.query(
                func.min(HealthData.created_at).label('min_date'),
                func.max(HealthData.created_at).label('max_date')
            ).filter(HealthData.user_id == user_id)
            
            if platform_id:
                date_range_query = date_range_query.filter(HealthData.platform_id == platform_id)
            
            date_range_result = date_range_query.first()
            date_range = {}
            if date_range_result.min_date:
                date_range['start_date'] = date_range_result.min_date.isoformat()
            if date_range_result.max_date:
                date_range['end_date'] = date_range_result.max_date.isoformat()
            
            return {
                "total_count": total_count,
                "data_type_counts": data_type_counts,
                "platform_counts": platform_counts,
                "date_range": date_range
            }
            
        except Exception as e:
            logger.error(f"获取健康数据统计失败: {e}")
            return {
                "total_count": 0,
                "data_type_counts": {},
                "platform_counts": {},
                "date_range": {}
            }
    
    def sync_health_data_from_platform(
        self,
        user_id: str,
        platform_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        data_types: Optional[List[HealthDataType]] = None
    ) -> Dict[str, Any]:
        """从平台同步健康数据"""
        try:
            # 这里应该调用具体平台的API来获取数据
            # 为了演示，这里返回模拟结果
            
            logger.info(f"开始从平台 {platform_id} 同步用户 {user_id} 的健康数据")
            
            # 模拟同步过程
            sync_result = {
                "status": "success",
                "message": "数据同步成功",
                "synced_count": 0,
                "failed_count": 0,
                "platform_id": platform_id,
                "sync_time": datetime.utcnow().isoformat()
            }
            
            # 实际实现中，这里应该：
            # 1. 根据平台类型调用相应的API客户端
            # 2. 获取指定日期范围和数据类型的数据
            # 3. 将数据转换为标准格式
            # 4. 批量插入数据库
            # 5. 处理重复数据和错误
            
            logger.info(f"平台 {platform_id} 数据同步完成")
            return sync_result
            
        except Exception as e:
            logger.error(f"同步健康数据失败: {e}")
            return {
                "status": "error",
                "message": f"同步失败: {str(e)}",
                "synced_count": 0,
                "failed_count": 0,
                "platform_id": platform_id,
                "sync_time": datetime.utcnow().isoformat()
            }
    
    def get_latest_data_by_type(
        self,
        user_id: str,
        data_type: HealthDataType,
        platform_id: Optional[str] = None
    ) -> Optional[HealthData]:
        """获取指定类型的最新健康数据"""
        try:
            query = self.db.query(HealthData).filter(
                and_(
                    HealthData.user_id == user_id,
                    HealthData.data_type == data_type
                )
            )
            
            if platform_id:
                query = query.filter(HealthData.platform_id == platform_id)
            
            return query.order_by(HealthData.created_at.desc()).first()
            
        except Exception as e:
            logger.error(f"获取最新健康数据失败: {e}")
            return None
    
    def get_data_trend(
        self,
        user_id: str,
        data_type: HealthDataType,
        days: int = 30,
        platform_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取健康数据趋势"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(HealthData).filter(
                and_(
                    HealthData.user_id == user_id,
                    HealthData.data_type == data_type,
                    HealthData.created_at >= start_date,
                    HealthData.created_at <= end_date
                )
            )
            
            if platform_id:
                query = query.filter(HealthData.platform_id == platform_id)
            
            data_list = query.order_by(HealthData.created_at.asc()).all()[:1000]  # 限制查询结果数量
            
            return [
                {
                    "date": data.created_at.date().isoformat(),
                    "value": data.value,
                    "unit": data.unit,
                    "platform_id": data.platform_id
                }
                for data in data_list
            ]
            
        except Exception as e:
            logger.error(f"获取健康数据趋势失败: {e}")
            return []
