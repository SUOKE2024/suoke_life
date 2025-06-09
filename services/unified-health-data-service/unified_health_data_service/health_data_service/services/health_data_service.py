"""
健康数据服务核心实现
提供健康数据的收集、处理、存储和查询功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict, Union
from .base import BaseService
from ..core.database import DatabaseService
from ..models.health_data import HealthData, VitalSigns, DiagnosticData
from ..utils.validators import HealthDataValidator
from ..utils.processors import HealthDataProcessor

logger = logging.getLogger(__name__)

class HealthDataService(BaseService):
    """
    健康数据服务
    负责健康数据的全生命周期管理
    """
    
    def __init__(self, database_service: Optional[DatabaseService] = None):
        """初始化健康数据服务"""
        super().__init__()
        self.database_service = database_service or DatabaseService()
        self.validator = HealthDataValidator()
        self.processor = HealthDataProcessor()
        self.running = False
        
    async def start(self) -> None:
        """启动健康数据服务"""
        try:
            # 初始化数据库连接
            if not self.database_service.connected:
                await self.database_service.initialize()
            
            self.running = True
            logger.info("健康数据服务启动成功")
            
        except Exception as e:
            logger.error(f"健康数据服务启动失败: {e}")
            raise
    
    async def stop(self) -> None:
        """停止健康数据服务"""
        self.running = False
        logger.info("健康数据服务已停止")
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康数据"""
        try:
            # 验证数据
            validated_data = await self.validator.validate(data)
            
            # 处理数据
            processed_data = await self.processor.process(validated_data)
            
            # 存储数据
            data_id = await self.store_health_data(processed_data)
            
            return {
                "status": "success",
                "data_id": data_id,
                "processed_data": processed_data
            }
            
        except Exception as e:
            logger.error(f"健康数据处理失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def store_health_data(self, data: Dict[str, Any]) -> str:
        """存储健康数据"""
        try:
            # 根据数据类型选择存储策略
            data_type = data.get('data_type', 'general')
            
            if data_type == 'vital_signs':
                return await self._store_vital_signs(data)
            elif data_type == 'diagnostic':
                return await self._store_diagnostic_data(data)
            elif data_type == 'tcm':
                return await self._store_tcm_data(data)
            else:
                return await self._store_general_health_data(data)
                
        except Exception as e:
            logger.error(f"健康数据存储失败: {e}")
            raise
    
    async def _store_vital_signs(self, data: Dict[str, Any]) -> str:
        """存储生命体征数据"""
        # 存储到PostgreSQL
        pg_id = await self.database_service.store_data('vital_signs', {
            'user_id': data['user_id'],
            'heart_rate': data.get('heart_rate'),
            'blood_pressure_systolic': data.get('blood_pressure_systolic'),
            'blood_pressure_diastolic': data.get('blood_pressure_diastolic'),
            'temperature': data.get('temperature'),
            'oxygen_saturation': data.get('oxygen_saturation'),
            'recorded_at': data.get('recorded_at', datetime.utcnow()),
            'created_at': datetime.utcnow()
        })
        
        # 缓存最新数据
        cache_key = f"vital_signs:latest:{data['user_id']}"
        await self.database_service.cache_set(cache_key, data, expire=3600)
        
        return pg_id
    
    async def _store_diagnostic_data(self, data: Dict[str, Any]) -> str:
        """存储诊断数据"""
        # 存储到PostgreSQL
        pg_id = await self.database_service.store_data('diagnostic_data', {
            'user_id': data['user_id'],
            'diagnosis_type': data['diagnosis_type'],
            'diagnosis_result': data['diagnosis_result'],
            'confidence_score': data.get('confidence_score'),
            'raw_data': data.get('raw_data'),
            'processed_data': data.get('processed_data'),
            'created_at': datetime.utcnow()
        })
        
        # 存储到MongoDB（用于复杂查询）
        mongo_id = await self.database_service.mongo_insert('diagnostic_data', {
            'pg_id': pg_id,
            'user_id': data['user_id'],
            'diagnosis_type': data['diagnosis_type'],
            'full_data': data,
            'created_at': datetime.utcnow()
        })
        
        return pg_id
    
    async def _store_tcm_data(self, data: Dict[str, Any]) -> str:
        """存储中医数据"""
        # 存储到MongoDB（适合中医复杂数据结构）
        mongo_id = await self.database_service.mongo_insert('tcm_data', {
            'user_id': data['user_id'],
            'diagnosis_method': data['diagnosis_method'],  # 望、闻、问、切
            'symptoms': data.get('symptoms', []),
            'constitution': data.get('constitution'),
            'syndrome_differentiation': data.get('syndrome_differentiation'),
            'treatment_plan': data.get('treatment_plan'),
            'created_at': datetime.utcnow()
        })
        
        # 同时存储摘要到PostgreSQL
        pg_id = await self.database_service.store_data('tcm_summary', {
            'user_id': data['user_id'],
            'mongo_id': mongo_id,
            'diagnosis_method': data['diagnosis_method'],
            'main_syndrome': data.get('syndrome_differentiation', {}).get('main_syndrome'),
            'created_at': datetime.utcnow()
        })
        
        return pg_id
    
    async def _store_general_health_data(self, data: Dict[str, Any]) -> str:
        """存储一般健康数据"""
        return await self.database_service.store_data('health_data', {
            'user_id': data['user_id'],
            'data_type': data['data_type'],
            'data_value': data['data_value'],
            'unit': data.get('unit'),
            'source': data.get('source'),
            'metadata': data.get('metadata'),
            'created_at': datetime.utcnow()
        })
    
    async def query_health_data(self, user_id: str, data_type: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """查询健康数据"""
        try:
            conditions = {'user_id': user_id}
            
            if data_type:
                conditions['data_type'] = data_type
            
            # 构建时间范围查询
            if start_date or end_date:
                # 这里需要更复杂的SQL查询，暂时简化
                pass
            
            # 查询数据
            results = await self.database_service.query_data(
                'health_data', 
                conditions=conditions, 
                limit=limit
            )
            
            return results
            
        except Exception as e:
            logger.error(f"健康数据查询失败: {e}")
            raise
    
    async def get_latest_vital_signs(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取最新生命体征"""
        try:
            # 先尝试从缓存获取
            cache_key = f"vital_signs:latest:{user_id}"
            cached_data = await self.database_service.cache_get(cache_key)
            
            if cached_data:
                return cached_data
            
            # 从数据库查询
            results = await self.database_service.query_data(
                'vital_signs',
                conditions={'user_id': user_id},
                limit=1
            )
            
            if results:
                latest_data = results[0]
                # 更新缓存
                await self.database_service.cache_set(cache_key, latest_data, expire=3600)
                return latest_data
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新生命体征失败: {e}")
            return None
    
    async def get_health_trends(self, user_id: str, data_type: str, 
                               days: int = 30) -> Dict[str, Any]:
        """获取健康趋势分析"""
        try:
            # 计算时间范围
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 查询历史数据
            results = await self.query_health_data(
                user_id=user_id,
                data_type=data_type,
                start_date=start_date,
                end_date=end_date
            )
            
            # 分析趋势
            trend_analysis = await self.processor.analyze_trends(results)
            
            return {
                "user_id": user_id,
                "data_type": data_type,
                "period_days": days,
                "data_points": len(results),
                "trend_analysis": trend_analysis
            }
            
        except Exception as e:
            logger.error(f"健康趋势分析失败: {e}")
            raise
    
    async def generate_health_report(self, user_id: str) -> Dict[str, Any]:
        """生成健康报告"""
        try:
            # 获取各类健康数据
            vital_signs = await self.get_latest_vital_signs(user_id)
            
            # 获取最近的诊断数据
            diagnostic_data = await self.database_service.mongo_find(
                'diagnostic_data',
                filter_dict={'user_id': user_id},
                limit=5
            )
            
            # 获取中医数据
            tcm_data = await self.database_service.mongo_find(
                'tcm_data',
                filter_dict={'user_id': user_id},
                limit=3
            )
            
            # 生成综合报告
            report = {
                "user_id": user_id,
                "generated_at": datetime.utcnow(),
                "vital_signs": vital_signs,
                "recent_diagnostics": diagnostic_data,
                "tcm_analysis": tcm_data,
                "health_score": await self._calculate_health_score(user_id),
                "recommendations": await self._generate_recommendations(user_id)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"健康报告生成失败: {e}")
            raise
    
    async def _calculate_health_score(self, user_id: str) -> float:
        """计算健康评分"""
        # 这里实现健康评分算法
        # 暂时返回模拟值
        return 85.5
    
    async def _generate_recommendations(self, user_id: str) -> List[str]:
        """生成健康建议"""
        # 这里实现健康建议生成算法
        # 暂时返回模拟建议
        return [
            "建议保持规律作息",
            "适量运动，每周至少3次",
            "注意饮食均衡，多吃蔬菜水果"
        ]
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "health_data_service",
            "running": self.running,
            "database_connected": self.database_service.connected if self.database_service else False
        }