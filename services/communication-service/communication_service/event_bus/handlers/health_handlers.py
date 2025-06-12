"""
健康数据事件处理器
处理健康数据的收集、验证、存储和同步
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

import structlog

from ..core.event_bus import Event, SuokeEventBus
from ..core.event_store import EventStore
from ..core.event_types import HealthDataEvents

logger = structlog.get_logger(__name__)


class HealthEventHandlers:
    """健康数据事件处理器"""
    
    def __init__(self, event_bus: SuokeEventBus, event_store: EventStore):
        """初始化健康数据事件处理器"""
        self.event_bus = event_bus
        self.event_store = event_store
        
        # 数据质量阈值
        self.quality_thresholds = {
            'heart_rate': {'min': 40, 'max': 200},
            'blood_pressure_systolic': {'min': 70, 'max': 250},
            'blood_pressure_diastolic': {'min': 40, 'max': 150},
            'temperature': {'min': 35.0, 'max': 42.0},
            'oxygen_saturation': {'min': 70, 'max': 100}
        }
        
        # 异常检测规则
        self.anomaly_rules = {
            'heart_rate_high': 100,
            'heart_rate_low': 60,
            'blood_pressure_high': {'systolic': 140, 'diastolic': 90},
            'blood_pressure_low': {'systolic': 90, 'diastolic': 60},
            'fever_threshold': 37.5,
            'oxygen_low': 95
        }
    
    async def register_handlers(self) -> None:
        """注册所有事件处理器"""
        # 数据接收事件
        await self.event_bus.subscribe(
            HealthDataEvents.HEALTH_DATA_RECEIVED,
            self.handle_health_data_received
        )
        
        # 生命体征更新事件
        await self.event_bus.subscribe(
            HealthDataEvents.VITAL_SIGNS_UPDATED,
            self.handle_vital_signs_updated
        )
        
        # 诊断数据接收事件
        await self.event_bus.subscribe(
            HealthDataEvents.DIAGNOSTIC_DATA_RECEIVED,
            self.handle_diagnostic_data_received
        )
        
        # 中医数据接收事件
        await self.event_bus.subscribe(
            HealthDataEvents.TCM_DATA_RECEIVED,
            self.handle_tcm_data_received
        )
        
        # 数据同步事件
        await self.event_bus.subscribe(
            HealthDataEvents.DATA_SYNC_STARTED,
            self.handle_data_sync_started
        )
        
        logger.info("健康数据事件处理器注册完成")
    
    async def handle_health_data_received(self, event: Event) -> None:
        """处理健康数据接收事件"""
        try:
            user_id = event.data.get('user_id')
            data_type = event.data.get('data_type')
            data_value = event.data.get('data_value')
            
            if not all([user_id, data_type, data_value]):
                logger.error("健康数据缺少必要字段", event_id=event.id)
                return
            
            # 数据质量检查
            quality_result = await self._check_data_quality(data_type, data_value)
            
            if quality_result['valid']:
                # 发布数据验证成功事件
                await self.event_bus.publish(
                    HealthDataEvents.HEALTH_DATA_VALIDATED,
                    {
                        'user_id': user_id,
                        'data_type': data_type,
                        'data_value': data_value,
                        'quality_score': quality_result['score'],
                        'original_event_id': event.id
                    },
                    correlation_id=event.correlation_id
                )
                
                # 根据数据类型分发到具体处理器
                if data_type in ['heart_rate', 'blood_pressure', 'temperature', 'oxygen_saturation']:
                    await self.event_bus.publish(
                        HealthDataEvents.VITAL_SIGNS_UPDATED,
                        event.data,
                        correlation_id=event.correlation_id
                    )
                elif data_type.startswith('diagnostic_'):
                    await self.event_bus.publish(
                        HealthDataEvents.DIAGNOSTIC_DATA_RECEIVED,
                        event.data,
                        correlation_id=event.correlation_id
                    )
                elif data_type.startswith('tcm_'):
                    await self.event_bus.publish(
                        HealthDataEvents.TCM_DATA_RECEIVED,
                        event.data,
                        correlation_id=event.correlation_id
                    )
            else:
                # 发布数据验证失败事件
                await self.event_bus.publish(
                    HealthDataEvents.DATA_VALIDATION_FAILED,
                    {
                        'user_id': user_id,
                        'data_type': data_type,
                        'data_value': data_value,
                        'validation_errors': quality_result['errors'],
                        'original_event_id': event.id
                    },
                    correlation_id=event.correlation_id
                )
            
            logger.info("健康数据处理完成", 
                       user_id=user_id,
                       data_type=data_type,
                       valid=quality_result['valid'])
            
        except Exception as e:
            logger.error("处理健康数据接收事件失败", 
                        event_id=event.id,
                        error=str(e))
    
    async def handle_vital_signs_updated(self, event: Event) -> None:
        """处理生命体征更新事件"""
        try:
            user_id = event.data.get('user_id')
            data_type = event.data.get('data_type')
            data_value = event.data.get('data_value')
            
            # 异常检测
            anomaly_result = await self._detect_vital_signs_anomaly(data_type, data_value)
            
            if anomaly_result['is_anomaly']:
                severity = anomaly_result['severity']
                
                if severity=='critical':
                    # 发布危急值事件
                    await self.event_bus.publish(
                        HealthDataEvents.VITAL_SIGNS_CRITICAL,
                        {
                            'user_id': user_id,
                            'data_type': data_type,
                            'data_value': data_value,
                            'anomaly_type': anomaly_result['type'],
                            'severity': severity,
                            'alert_level': 'immediate',
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        correlation_id=event.correlation_id
                    )
                elif severity=='abnormal':
                    # 发布异常值事件
                    await self.event_bus.publish(
                        HealthDataEvents.VITAL_SIGNS_ABNORMAL,
                        {
                            'user_id': user_id,
                            'data_type': data_type,
                            'data_value': data_value,
                            'anomaly_type': anomaly_result['type'],
                            'severity': severity,
                            'alert_level': 'warning',
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        correlation_id=event.correlation_id
                    )
            
            # 存储数据
            await self._store_vital_signs_data(user_id, data_type, data_value, event.correlation_id)
            
            # 发布数据存储完成事件
            await self.event_bus.publish(
                HealthDataEvents.HEALTH_DATA_STORED,
                {
                    'user_id': user_id,
                    'data_type': data_type,
                    'storage_type': 'vital_signs',
                    'timestamp': datetime.utcnow().isoformat()
                },
                correlation_id=event.correlation_id
            )
            
            logger.info("生命体征数据处理完成", 
                       user_id=user_id,
                       data_type=data_type,
                       anomaly=anomaly_result['is_anomaly'])
            
        except Exception as e:
            logger.error("处理生命体征更新事件失败", 
                        event_id=event.id,
                        error=str(e))
    
    async def handle_diagnostic_data_received(self, event: Event) -> None:
        """处理诊断数据接收事件"""
        try:
            user_id = event.data.get('user_id')
            diagnosis_type = event.data.get('diagnosis_type')
            diagnosis_result = event.data.get('diagnosis_result')
            confidence_score = event.data.get('confidence_score', 0.0)
            
            # 检查诊断置信度
            if confidence_score < 0.7:
                await self.event_bus.publish(
                    HealthDataEvents.DIAGNOSTIC_CONFIDENCE_LOW,
                    {
                        'user_id': user_id,
                        'diagnosis_type': diagnosis_type,
                        'confidence_score': confidence_score,
                        'requires_review': True,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    correlation_id=event.correlation_id
                )
            
            # 存储诊断数据
            await self._store_diagnostic_data(
                user_id, diagnosis_type, diagnosis_result, 
                confidence_score, event.correlation_id
            )
            
            # 发布诊断结果生成事件
            await self.event_bus.publish(
                HealthDataEvents.DIAGNOSTIC_RESULT_GENERATED,
                {
                    'user_id': user_id,
                    'diagnosis_type': diagnosis_type,
                    'diagnosis_result': diagnosis_result,
                    'confidence_score': confidence_score,
                    'timestamp': datetime.utcnow().isoformat()
                },
                correlation_id=event.correlation_id
            )
            
            logger.info("诊断数据处理完成", 
                       user_id=user_id,
                       diagnosis_type=diagnosis_type,
                       confidence=confidence_score)
            
        except Exception as e:
            logger.error("处理诊断数据接收事件失败", 
                        event_id=event.id,
                        error=str(e))
    
    async def handle_tcm_data_received(self, event: Event) -> None:
        """处理中医数据接收事件"""
        try:
            user_id = event.data.get('user_id')
            tcm_type = event.data.get('tcm_type')  # 望、闻、问、切
            tcm_data = event.data.get('tcm_data')
            
            # 中医数据特殊处理
            if tcm_type=='constitution':
                # 体质分析完成
                await self.event_bus.publish(
                    HealthDataEvents.TCM_CONSTITUTION_ANALYZED,
                    {
                        'user_id': user_id,
                        'constitution_type': tcm_data.get('constitution_type'),
                        'constitution_score': tcm_data.get('score'),
                        'characteristics': tcm_data.get('characteristics', []),
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    correlation_id=event.correlation_id
                )
            elif tcm_type=='syndrome':
                # 证候识别完成
                await self.event_bus.publish(
                    HealthDataEvents.TCM_SYNDROME_IDENTIFIED,
                    {
                        'user_id': user_id,
                        'syndrome_name': tcm_data.get('syndrome_name'),
                        'syndrome_category': tcm_data.get('category'),
                        'confidence_score': tcm_data.get('confidence', 0.0),
                        'symptoms': tcm_data.get('symptoms', []),
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    correlation_id=event.correlation_id
                )
            
            # 存储中医数据
            await self._store_tcm_data(user_id, tcm_type, tcm_data, event.correlation_id)
            
            logger.info("中医数据处理完成", 
                       user_id=user_id,
                       tcm_type=tcm_type)
            
        except Exception as e:
            logger.error("处理中医数据接收事件失败", 
                        event_id=event.id,
                        error=str(e))
    
    async def handle_data_sync_started(self, event: Event) -> None:
        """处理数据同步开始事件"""
        try:
            user_id = event.data.get('user_id')
            sync_type = event.data.get('sync_type')
            target_systems = event.data.get('target_systems', [])
            
            # 执行数据同步
            sync_results = []
            for system in target_systems:
                try:
                    result = await self._sync_to_system(user_id, sync_type, system)
                    sync_results.append({
                        'system': system,
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    sync_results.append({
                        'system': system,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            # 发布同步完成事件
            await self.event_bus.publish(
                HealthDataEvents.DATA_SYNC_COMPLETED,
                {
                    'user_id': user_id,
                    'sync_type': sync_type,
                    'sync_results': sync_results,
                    'timestamp': datetime.utcnow().isoformat()
                },
                correlation_id=event.correlation_id
            )
            
            logger.info("数据同步完成", 
                       user_id=user_id,
                       sync_type=sync_type,
                       success_count=len([r for r in sync_results if r['status']=='success']))
            
        except Exception as e:
            logger.error("处理数据同步事件失败", 
                        event_id=event.id,
                        error=str(e))
            
            # 发布同步失败事件
            await self.event_bus.publish(
                HealthDataEvents.DATA_SYNC_FAILED,
                {
                    'user_id': event.data.get('user_id'),
                    'sync_type': event.data.get('sync_type'),
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                },
                correlation_id=event.correlation_id
            )
    
    async def _check_data_quality(self, data_type: str, data_value: Any) -> Dict[str, Any]:
        """检查数据质量"""
        errors = []
        score = 1.0
        
        if data_type in self.quality_thresholds:
            thresholds = self.quality_thresholds[data_type]
            
            if isinstance(data_value, (int, float)):
                if data_value < thresholds['min']:
                    errors.append(f"值 {data_value} 低于最小阈值 {thresholds['min']}")
                    score-=0.5
                elif data_value > thresholds['max']:
                    errors.append(f"值 {data_value} 超过最大阈值 {thresholds['max']}")
                    score-=0.5
            else:
                errors.append(f"数据类型错误，期望数值类型，得到 {type(data_value)}")
                score = 0.0
        
        return {
            'valid': len(errors)==0,
            'score': max(0.0, score),
            'errors': errors
        }
    
    async def _detect_vital_signs_anomaly(self, data_type: str, data_value: Any) -> Dict[str, Any]:
        """检测生命体征异常"""
        is_anomaly = False
        anomaly_type = None
        severity = 'normal'
        
        if data_type=='heart_rate':
            if data_value > self.anomaly_rules['heart_rate_high']:
                is_anomaly = True
                anomaly_type = 'tachycardia'
                severity = 'critical' if data_value > 150 else 'abnormal'
            elif data_value < self.anomaly_rules['heart_rate_low']:
                is_anomaly = True
                anomaly_type = 'bradycardia'
                severity = 'critical' if data_value < 40 else 'abnormal'
        
        elif data_type=='blood_pressure':
            systolic = data_value.get('systolic', 0) if isinstance(data_value, dict) else 0
            diastolic = data_value.get('diastolic', 0) if isinstance(data_value, dict) else 0
            
            high_bp = self.anomaly_rules['blood_pressure_high']
            low_bp = self.anomaly_rules['blood_pressure_low']
            
            if systolic>=high_bp['systolic'] or diastolic>=high_bp['diastolic']:
                is_anomaly = True
                anomaly_type = 'hypertension'
                severity = 'critical' if systolic > 180 or diastolic > 110 else 'abnormal'
            elif systolic<=low_bp['systolic'] or diastolic<=low_bp['diastolic']:
                is_anomaly = True
                anomaly_type = 'hypotension'
                severity = 'critical' if systolic < 80 or diastolic < 50 else 'abnormal'
        
        elif data_type=='temperature':
            if data_value>=self.anomaly_rules['fever_threshold']:
                is_anomaly = True
                anomaly_type = 'fever'
                severity = 'critical' if data_value > 39.0 else 'abnormal'
        
        elif data_type=='oxygen_saturation':
            if data_value < self.anomaly_rules['oxygen_low']:
                is_anomaly = True
                anomaly_type = 'hypoxemia'
                severity = 'critical' if data_value < 90 else 'abnormal'
        
        return {
            'is_anomaly': is_anomaly,
            'type': anomaly_type,
            'severity': severity
        }
    
    async def _store_vital_signs_data(self, user_id: str, data_type: str, 
                                     data_value: Any, correlation_id: str) -> None:
        """存储生命体征数据"""
        # 这里应该调用实际的数据存储服务
        # 暂时用日志记录
        logger.info("存储生命体征数据", 
                   user_id=user_id,
                   data_type=data_type,
                   correlation_id=correlation_id)
    
    async def _store_diagnostic_data(self, user_id: str, diagnosis_type: str,
                                   diagnosis_result: Any, confidence_score: float,
                                   correlation_id: str) -> None:
        """存储诊断数据"""
        logger.info("存储诊断数据", 
                   user_id=user_id,
                   diagnosis_type=diagnosis_type,
                   confidence=confidence_score,
                   correlation_id=correlation_id)
    
    async def _store_tcm_data(self, user_id: str, tcm_type: str,
                             tcm_data: Dict[str, Any], correlation_id: str) -> None:
        """存储中医数据"""
        logger.info("存储中医数据", 
                   user_id=user_id,
                   tcm_type=tcm_type,
                   correlation_id=correlation_id)
    
    async def _sync_to_system(self, user_id: str, sync_type: str, target_system: str) -> Dict[str, Any]:
        """同步数据到目标系统"""
        # 模拟同步操作
        await asyncio.sleep(0.1)
        return {
            'synced_records': 1,
            'sync_time': datetime.utcnow().isoformat()
        } 