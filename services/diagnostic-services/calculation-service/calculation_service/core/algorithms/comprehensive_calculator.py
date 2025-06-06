"""
comprehensive_calculator - 索克生活项目模块
"""

        import hashlib
from .bagua.calculator import BaguaCalculator
from .constitution.calculator import ConstitutionCalculator
from .wuyun_liuqi.calculator import WuyunLiuqiCalculator
from .ziwu_liuzhu.calculator import ZiwuLiuzhuCalculator
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
import numpy as np

"""
综合算诊计算器

整合多种算诊方法，提供综合分析和精确计算
"""



logger = logging.getLogger(__name__)

@dataclass
class AlgorithmWeight:
    """算法权重配置"""
    ziwu_weight: float = 0.25
    constitution_weight: float = 0.30
    bagua_weight: float = 0.20
    wuyun_liuqi_weight: float = 0.25
    
    def normalize(self):
        """权重归一化"""
        total = self.ziwu_weight + self.constitution_weight + self.bagua_weight + self.wuyun_liuqi_weight
        if total != 1.0:
            self.ziwu_weight /= total
            self.constitution_weight /= total
            self.bagua_weight /= total
            self.wuyun_liuqi_weight /= total

@dataclass
class ConfidenceMetrics:
    """置信度指标"""
    overall_confidence: float
    algorithm_confidences: Dict[str, float]
    data_quality_score: float
    historical_accuracy: float
    consistency_score: float

class HistoricalDataValidator:
    """历史数据验证器"""
    
    def __init__(self):
        self.validation_cache = {}
        self.accuracy_records = {}
    
    async def validate_prediction_accuracy(self, birth_info: Dict[str, Any], 
                                         prediction: Dict[str, Any]) -> float:
        """验证预测准确性"""
        try:
            # 基于历史数据验证预测准确性
            birth_key = self._generate_birth_key(birth_info)
            
            if birth_key in self.accuracy_records:
                historical_accuracy = self.accuracy_records[birth_key]
                return min(historical_accuracy * 1.1, 0.95)  # 最高95%准确率
            
            # 基于统计模型估算准确性
            base_accuracy = 0.75
            
            # 根据数据完整性调整
            data_completeness = self._calculate_data_completeness(birth_info)
            accuracy_adjustment = (data_completeness - 0.5) * 0.2
            
            estimated_accuracy = base_accuracy + accuracy_adjustment
            return max(0.6, min(estimated_accuracy, 0.9))
            
        except Exception as e:
            logger.error(f"历史数据验证失败: {e}")
            return 0.7  # 默认准确率
    
    def _generate_birth_key(self, birth_info: Dict[str, Any]) -> str:
        """生成出生信息键值"""
        return f"{birth_info.get('year', 0)}_{birth_info.get('month', 0)}_{birth_info.get('day', 0)}_{birth_info.get('hour', 0)}"
    
    def _calculate_data_completeness(self, birth_info: Dict[str, Any]) -> float:
        """计算数据完整性"""
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        present_fields = sum(1 for field in required_fields if birth_info.get(field))
        return present_fields / len(required_fields)

class AdvancedPerformanceOptimizer:
    """高级性能优化器"""
    
    def __init__(self):
        self.calculation_cache = {}
        self.optimization_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_calculation_time': 0.0
        }
    
    async def optimize_calculation(self, calculation_func, *args, **kwargs):
        """优化计算性能"""
        cache_key = self._generate_cache_key(calculation_func.__name__, args, kwargs)
        
        # 检查缓存
        if cache_key in self.calculation_cache:
            self.optimization_stats['cache_hits'] += 1
            return self.calculation_cache[cache_key]
        
        # 执行计算
        start_time = datetime.now()
        result = await calculation_func(*args, **kwargs)
        calculation_time = (datetime.now() - start_time).total_seconds()
        
        # 更新统计
        self.optimization_stats['cache_misses'] += 1
        self._update_avg_calculation_time(calculation_time)
        
        # 缓存结果
        self.calculation_cache[cache_key] = result
        
        return result
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_avg_calculation_time(self, new_time: float):
        """更新平均计算时间"""
        total_calculations = self.optimization_stats['cache_hits'] + self.optimization_stats['cache_misses']
        if total_calculations == 1:
            self.optimization_stats['avg_calculation_time'] = new_time
        else:
            current_avg = self.optimization_stats['avg_calculation_time']
            self.optimization_stats['avg_calculation_time'] = (current_avg * (total_calculations - 1) + new_time) / total_calculations

class ComprehensiveCalculator:
    """综合算诊计算器 - 增强版"""
    
    def __init__(self):
        # 初始化各个计算器
        self.ziwu_calc = ZiwuLiuzhuCalculator()
        self.constitution_calc = ConstitutionCalculator()
        self.bagua_calc = BaguaCalculator()
        self.wuyun_liuqi_calc = WuyunLiuqiCalculator()
        
        # 初始化增强组件
        self.algorithm_weights = AlgorithmWeight()
        self.historical_validator = HistoricalDataValidator()
        self.performance_optimizer = AdvancedPerformanceOptimizer()
        
        # 算法精度配置
        self.precision_config = {
            'decimal_places': 4,
            'confidence_threshold': 0.7,
            'consistency_threshold': 0.8
        }
        
        logger.info("综合算诊计算器初始化完成 - 增强版")
    
    async def comprehensive_analysis(self, birth_info: Dict[str, Any], 
                                   analysis_date: datetime = None,
                                   include_ziwu: bool = True,
                                   include_constitution: bool = True,
                                   include_bagua: bool = True,
                                   include_wuyun_liuqi: bool = True,
                                   precision_mode: str = "high") -> Dict[str, Any]:
        """
        综合算诊分析 - 增强版
        
        Args:
            birth_info: 出生信息
            analysis_date: 分析日期
            include_*: 是否包含各种分析
            precision_mode: 精度模式 (high/medium/fast)
        """
        try:
            logger.info(f"开始综合算诊分析 - 精度模式: {precision_mode}")
            
            if analysis_date is None:
                analysis_date = datetime.now()
            
            # 数据验证和预处理
            validated_birth_info = await self._validate_and_enhance_birth_info(birth_info)
            
            # 并行执行各种分析
            analysis_tasks = []
            
            if include_ziwu:
                task = self.performance_optimizer.optimize_calculation(
                    self._analyze_ziwu_liuzhu, validated_birth_info, analysis_date
                )
                analysis_tasks.append(('ziwu', task))
            
            if include_constitution:
                task = self.performance_optimizer.optimize_calculation(
                    self._analyze_constitution, validated_birth_info
                )
                analysis_tasks.append(('constitution', task))
            
            if include_bagua:
                task = self.performance_optimizer.optimize_calculation(
                    self._analyze_bagua, validated_birth_info
                )
                analysis_tasks.append(('bagua', task))
            
            if include_wuyun_liuqi:
                task = self.performance_optimizer.optimize_calculation(
                    self._analyze_wuyun_liuqi, validated_birth_info, analysis_date
                )
                analysis_tasks.append(('wuyun_liuqi', task))
            
            # 等待所有分析完成
            analysis_results = {}
            for name, task in analysis_tasks:
                try:
                    result = await task
                    analysis_results[name] = result
                except Exception as e:
                    logger.error(f"{name}分析失败: {e}")
                    analysis_results[name] = {"error": str(e), "confidence": 0.0}
            
            # 计算综合结果
            comprehensive_result = await self._calculate_comprehensive_result(
                analysis_results, validated_birth_info, precision_mode
            )
            
            # 历史数据验证
            historical_accuracy = await self.historical_validator.validate_prediction_accuracy(
                validated_birth_info, comprehensive_result
            )
            
            # 构建最终结果
            final_result = {
                "analysis_metadata": {
                    "analysis_date": analysis_date.isoformat(),
                    "precision_mode": precision_mode,
                    "included_analyses": [name for name, _ in analysis_tasks],
                    "calculation_time": self.performance_optimizer.optimization_stats['avg_calculation_time'],
                    "cache_hit_rate": self._calculate_cache_hit_rate()
                },
                "birth_info": validated_birth_info,
                "individual_analyses": analysis_results,
                "comprehensive_analysis": comprehensive_result,
                "confidence_metrics": await self._calculate_confidence_metrics(
                    analysis_results, comprehensive_result, historical_accuracy
                ),
                "recommendations": await self._generate_enhanced_recommendations(
                    comprehensive_result, analysis_results
                ),
                "performance_stats": self.performance_optimizer.optimization_stats
            }
            
            logger.info(f"综合算诊分析完成，总体置信度: {final_result['confidence_metrics'].overall_confidence:.4f}")
            return final_result
            
        except Exception as e:
            logger.error(f"综合算诊分析失败: {e}")
            raise
    
    async def _validate_and_enhance_birth_info(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证和增强出生信息"""
        enhanced_info = birth_info.copy()
        
        # 数据完整性检查
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        for field in required_fields:
            if field not in enhanced_info or enhanced_info[field] is None:
                logger.warning(f"缺少必要字段: {field}")
                enhanced_info[field] = self._get_default_value(field)
        
        # 数据范围验证
        enhanced_info['year'] = max(1900, min(enhanced_info['year'], 2100))
        enhanced_info['month'] = max(1, min(enhanced_info['month'], 12))
        enhanced_info['day'] = max(1, min(enhanced_info['day'], 31))
        enhanced_info['hour'] = max(0, min(enhanced_info['hour'], 23))
        
        # 添加计算辅助信息
        enhanced_info['birth_datetime'] = datetime(
            enhanced_info['year'], enhanced_info['month'], 
            enhanced_info['day'], enhanced_info['hour']
        )
        enhanced_info['data_quality_score'] = self._calculate_data_quality(enhanced_info)
        
        return enhanced_info
    
    def _get_default_value(self, field: str) -> Any:
        """获取字段默认值"""
        defaults = {
            'year': 1990,
            'month': 1,
            'day': 1,
            'hour': 12,
            'gender': '未知'
        }
        return defaults.get(field)
    
    def _calculate_data_quality(self, birth_info: Dict[str, Any]) -> float:
        """计算数据质量分数"""
        quality_score = 1.0
        
        # 检查数据完整性
        if birth_info.get('gender') == '未知':
            quality_score -= 0.1
        
        # 检查时间精度
        if birth_info.get('hour') == 12:  # 可能是默认值
            quality_score -= 0.05
        
        # 检查年份合理性
        current_year = datetime.now().year
        birth_year = birth_info.get('year', current_year)
        if birth_year < 1920 or birth_year > current_year:
            quality_score -= 0.1
        
        return max(0.5, quality_score)  # 最低0.5分
    
    async def _analyze_ziwu_liuzhu(self, birth_info: Dict[str, Any], 
                                 analysis_date: datetime) -> Dict[str, Any]:
        """子午流注分析"""
        try:
            result = self.ziwu_calc.analyze_current_time(analysis_date)
            result['confidence'] = 0.9  # 子午流注算法相对稳定
            return result
        except Exception as e:
            logger.error(f"子午流注分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_constitution(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """体质分析"""
        try:
            result = self.constitution_calc.analyze_constitution(birth_info)
            # 根据数据质量调整置信度
            base_confidence = 0.85
            quality_adjustment = (birth_info.get('data_quality_score', 0.8) - 0.5) * 0.2
            result['confidence'] = min(0.95, base_confidence + quality_adjustment)
            return result
        except Exception as e:
            logger.error(f"体质分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_bagua(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """八卦分析"""
        try:
            result = self.bagua_calc.analyze_personal_bagua(birth_info)
            result['confidence'] = 0.8  # 八卦分析置信度
            return result
        except Exception as e:
            logger.error(f"八卦分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_wuyun_liuqi(self, birth_info: Dict[str, Any], 
                                 analysis_date: datetime) -> Dict[str, Any]:
        """五运六气分析"""
        try:
            result = self.wuyun_liuqi_calc.get_yearly_prediction(analysis_date.year)
            result['confidence'] = 0.88  # 五运六气分析置信度
            return result
        except Exception as e:
            logger.error(f"五运六气分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _calculate_comprehensive_result(self, analysis_results: Dict[str, Any],
                                            birth_info: Dict[str, Any],
                                            precision_mode: str) -> Dict[str, Any]:
        """计算综合结果"""
        try:
            # 动态调整权重
            weights = await self._calculate_dynamic_weights(analysis_results, precision_mode)
            
            # 提取各分析的关键信息
            health_indicators = []
            constitution_types = []
            recommendations = []
            risk_factors = []
            
            for analysis_name, result in analysis_results.items():
                if 'error' in result:
                    continue
                
                # 提取健康指标
                if 'health_status' in result:
                    health_indicators.append({
                        'source': analysis_name,
                        'status': result['health_status'],
                        'confidence': result.get('confidence', 0.7),
                        'weight': weights.get(analysis_name, 0.25)
                    })
                
                # 提取体质类型
                if 'constitution_type' in result:
                    constitution_types.append({
                        'source': analysis_name,
                        'type': result['constitution_type'],
                        'confidence': result.get('confidence', 0.7),
                        'weight': weights.get(analysis_name, 0.25)
                    })
                
                # 提取建议
                if 'recommendations' in result:
                    recommendations.extend(result['recommendations'])
                
                # 提取风险因素
                if 'risk_factors' in result:
                    risk_factors.extend(result['risk_factors'])
            
            # 计算综合健康状态
            overall_health_status = self._calculate_weighted_health_status(health_indicators)
            
            # 计算主要体质类型
            primary_constitution = self._calculate_primary_constitution(constitution_types)
            
            # 生成综合建议
            comprehensive_recommendations = self._merge_recommendations(recommendations)
            
            # 计算综合风险评估
            risk_assessment = self._calculate_comprehensive_risk(risk_factors, weights)
            
            return {
                "overall_health_status": overall_health_status,
                "primary_constitution": primary_constitution,
                "constitution_distribution": self._calculate_constitution_distribution(constitution_types),
                "health_score": self._calculate_health_score(health_indicators, risk_factors),
                "risk_assessment": risk_assessment,
                "comprehensive_recommendations": comprehensive_recommendations,
                "analysis_weights": weights,
                "precision_metrics": {
                    "calculation_precision": self.precision_config['decimal_places'],
                    "confidence_threshold": self.precision_config['confidence_threshold'],
                    "data_quality": birth_info.get('data_quality_score', 0.8)
                }
            }
            
        except Exception as e:
            logger.error(f"综合结果计算失败: {e}")
            raise
    
    async def _calculate_dynamic_weights(self, analysis_results: Dict[str, Any],
                                       precision_mode: str) -> Dict[str, float]:
        """动态计算权重"""
        base_weights = {
            'ziwu': self.algorithm_weights.ziwu_weight,
            'constitution': self.algorithm_weights.constitution_weight,
            'bagua': self.algorithm_weights.bagua_weight,
            'wuyun_liuqi': self.algorithm_weights.wuyun_liuqi_weight
        }
        
        # 根据各分析的置信度调整权重
        adjusted_weights = {}
        total_confidence = 0
        
        for name, result in analysis_results.items():
            if 'error' not in result:
                confidence = result.get('confidence', 0.7)
                adjusted_weight = base_weights.get(name, 0.25) * confidence
                adjusted_weights[name] = adjusted_weight
                total_confidence += adjusted_weight
        
        # 归一化权重
        if total_confidence > 0:
            for name in adjusted_weights:
                adjusted_weights[name] /= total_confidence
        
        return adjusted_weights
    
    def _calculate_weighted_health_status(self, health_indicators: List[Dict]) -> Dict[str, Any]:
        """计算加权健康状态"""
        if not health_indicators:
            return {"status": "未知", "confidence": 0.0}
        
        # 健康状态映射
        status_scores = {
            "优秀": 1.0, "良好": 0.8, "一般": 0.6, 
            "需要关注": 0.4, "较差": 0.2, "未知": 0.0
        }
        
        weighted_score = 0
        total_weight = 0
        
        for indicator in health_indicators:
            score = status_scores.get(indicator['status'], 0.5)
            weight = indicator['weight'] * indicator['confidence']
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return {"status": "未知", "confidence": 0.0}
        
        final_score = weighted_score / total_weight
        
        # 将分数转换回状态
        if final_score >= 0.9:
            status = "优秀"
        elif final_score >= 0.7:
            status = "良好"
        elif final_score >= 0.5:
            status = "一般"
        elif final_score >= 0.3:
            status = "需要关注"
        else:
            status = "较差"
        
        return {
            "status": status,
            "score": round(final_score, self.precision_config['decimal_places']),
            "confidence": min(total_weight, 0.95)
        }
    
    def _calculate_primary_constitution(self, constitution_types: List[Dict]) -> Dict[str, Any]:
        """计算主要体质类型"""
        if not constitution_types:
            return {"type": "未知", "confidence": 0.0}
        
        # 统计各体质类型的加权得分
        type_scores = {}
        
        for const in constitution_types:
            const_type = const['type']
            weight = const['weight'] * const['confidence']
            
            if const_type in type_scores:
                type_scores[const_type] += weight
            else:
                type_scores[const_type] = weight
        
        # 找出得分最高的体质类型
        primary_type = max(type_scores.items(), key=lambda x: x[1])
        
        return {
            "type": primary_type[0],
            "confidence": round(primary_type[1], self.precision_config['decimal_places']),
            "distribution": type_scores
        }
    
    def _calculate_constitution_distribution(self, constitution_types: List[Dict]) -> Dict[str, float]:
        """计算体质分布"""
        if not constitution_types:
            return {}
        
        type_weights = {}
        total_weight = 0
        
        for const in constitution_types:
            const_type = const['type']
            weight = const['weight'] * const['confidence']
            
            if const_type in type_weights:
                type_weights[const_type] += weight
            else:
                type_weights[const_type] = weight
            
            total_weight += weight
        
        # 归一化为百分比
        if total_weight > 0:
            for const_type in type_weights:
                type_weights[const_type] = round(
                    (type_weights[const_type] / total_weight) * 100,
                    2
                )
        
        return type_weights
    
    def _calculate_health_score(self, health_indicators: List[Dict], 
                              risk_factors: List[str]) -> Dict[str, Any]:
        """计算健康评分"""
        base_score = 80  # 基础分数
        
        # 根据健康指标调整
        if health_indicators:
            avg_confidence = sum(h['confidence'] for h in health_indicators) / len(health_indicators)
            health_adjustment = (avg_confidence - 0.5) * 20
            base_score += health_adjustment
        
        # 根据风险因素扣分
        risk_penalty = min(len(risk_factors) * 5, 30)  # 每个风险因素扣5分，最多扣30分
        base_score -= risk_penalty
        
        # 确保分数在合理范围内
        final_score = max(0, min(base_score, 100))
        
        # 评级
        if final_score >= 90:
            grade = "A+"
        elif final_score >= 80:
            grade = "A"
        elif final_score >= 70:
            grade = "B"
        elif final_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "score": round(final_score, 1),
            "grade": grade,
            "risk_factors_count": len(risk_factors),
            "health_indicators_count": len(health_indicators)
        }
    
    def _calculate_comprehensive_risk(self, risk_factors: List[str], 
                                    weights: Dict[str, float]) -> Dict[str, Any]:
        """计算综合风险评估"""
        if not risk_factors:
            return {
                "level": "低风险",
                "factors": [],
                "recommendations": ["继续保持良好的生活习惯"]
            }
        
        # 风险因素分类和权重
        risk_categories = {
            "心血管": ["高血压", "心律不齐", "胸闷", "心悸"],
            "消化系统": ["胃痛", "消化不良", "腹胀", "便秘"],
            "呼吸系统": ["咳嗽", "气短", "胸闷", "哮喘"],
            "内分泌": ["疲劳", "失眠", "情绪波动", "代谢异常"],
            "免疫系统": ["易感冒", "过敏", "炎症", "免疫力低下"]
        }
        
        category_risks = {}
        for category, factors in risk_categories.items():
            category_risk = sum(1 for factor in risk_factors if any(f in factor for f in factors))
            if category_risk > 0:
                category_risks[category] = category_risk
        
        # 计算总体风险等级
        total_risk_score = len(risk_factors)
        if total_risk_score == 0:
            risk_level = "低风险"
        elif total_risk_score <= 2:
            risk_level = "中低风险"
        elif total_risk_score <= 4:
            risk_level = "中等风险"
        elif total_risk_score <= 6:
            risk_level = "中高风险"
        else:
            risk_level = "高风险"
        
        return {
            "level": risk_level,
            "score": total_risk_score,
            "factors": risk_factors,
            "category_distribution": category_risks,
            "recommendations": self._generate_risk_recommendations(risk_level, category_risks)
        }
    
    def _generate_risk_recommendations(self, risk_level: str, 
                                     category_risks: Dict[str, int]) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        # 基于风险等级的通用建议
        if risk_level == "高风险":
            recommendations.append("建议尽快咨询专业医生进行详细检查")
            recommendations.append("密切关注身体变化，定期监测相关指标")
        elif risk_level in ["中高风险", "中等风险"]:
            recommendations.append("建议定期体检，关注相关健康指标")
            recommendations.append("调整生活方式，加强预防措施")
        
        # 基于风险类别的具体建议
        for category, count in category_risks.items():
            if category == "心血管" and count > 0:
                recommendations.append("注意心血管健康，控制血压和血脂")
            elif category == "消化系统" and count > 0:
                recommendations.append("调整饮食结构，规律作息，保护消化系统")
            elif category == "呼吸系统" and count > 0:
                recommendations.append("注意呼吸道保护，避免污染环境")
            elif category == "内分泌" and count > 0:
                recommendations.append("调节内分泌，保持情绪稳定，充足睡眠")
            elif category == "免疫系统" and count > 0:
                recommendations.append("增强免疫力，适度运动，均衡营养")
        
        return recommendations
    
    def _merge_recommendations(self, recommendations: List[str]) -> List[str]:
        """合并和去重建议"""
        # 去重并保持顺序
        unique_recommendations = []
        seen = set()
        
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        # 按重要性排序（简单的关键词匹配）
        priority_keywords = ["紧急", "立即", "尽快", "重要", "关键"]
        
            @cache(timeout=300)  # 5分钟缓存
def get_priority(rec):
            for i, keyword in enumerate(priority_keywords):
                if keyword in rec:
                    return i
            return len(priority_keywords)
        
        unique_recommendations.sort(key=get_priority)
        
        return unique_recommendations[:10]  # 最多返回10条建议
    
    async def _calculate_confidence_metrics(self, analysis_results: Dict[str, Any],
                                          comprehensive_result: Dict[str, Any],
                                          historical_accuracy: float) -> ConfidenceMetrics:
        """计算置信度指标"""
        # 各算法置信度
        algorithm_confidences = {}
        total_confidence = 0
        valid_count = 0
        
        for name, result in analysis_results.items():
            if 'error' not in result:
                confidence = result.get('confidence', 0.7)
                algorithm_confidences[name] = confidence
                total_confidence += confidence
                valid_count += 1
        
        # 总体置信度
        if valid_count > 0:
            overall_confidence = total_confidence / valid_count
        else:
            overall_confidence = 0.0
        
        # 数据质量分数
        data_quality_score = comprehensive_result.get('precision_metrics', {}).get('data_quality', 0.8)
        
        # 一致性分数（基于各算法结果的一致性）
        consistency_score = self._calculate_consistency_score(analysis_results)
        
        # 综合调整置信度
        final_confidence = (
            overall_confidence * 0.4 +
            historical_accuracy * 0.3 +
            data_quality_score * 0.2 +
            consistency_score * 0.1
        )
        
        return ConfidenceMetrics(
            overall_confidence=round(final_confidence, self.precision_config['decimal_places']),
            algorithm_confidences=algorithm_confidences,
            data_quality_score=round(data_quality_score, self.precision_config['decimal_places']),
            historical_accuracy=round(historical_accuracy, self.precision_config['decimal_places']),
            consistency_score=round(consistency_score, self.precision_config['decimal_places'])
        )
    
    def _calculate_consistency_score(self, analysis_results: Dict[str, Any]) -> float:
        """计算一致性分数"""
        # 提取各分析的健康状态评估
        health_statuses = []
        for result in analysis_results.values():
            if 'error' not in result and 'health_status' in result:
                health_statuses.append(result['health_status'])
        
        if len(health_statuses) < 2:
            return 0.8  # 默认一致性
        
        # 计算状态一致性
        status_counts = {}
        for status in health_statuses:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 最常见状态的比例
        max_count = max(status_counts.values())
        consistency = max_count / len(health_statuses)
        
        return consistency
    
    async def _generate_enhanced_recommendations(self, comprehensive_result: Dict[str, Any],
                                               analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强建议"""
        recommendations = {
            "immediate_actions": [],
            "lifestyle_adjustments": [],
            "dietary_suggestions": [],
            "exercise_recommendations": [],
            "monitoring_advice": [],
            "follow_up_schedule": {}
        }
        
        # 基于健康状态生成建议
        health_status = comprehensive_result.get('overall_health_status', {})
        if health_status.get('status') == '较差':
            recommendations["immediate_actions"].append("建议尽快咨询专业医生")
            recommendations["monitoring_advice"].append("每日监测相关健康指标")
        
        # 基于体质类型生成建议
        constitution = comprehensive_result.get('primary_constitution', {})
        const_type = constitution.get('type', '')
        
        if '阳虚' in const_type:
            recommendations["lifestyle_adjustments"].append("注意保暖，避免寒凉")
            recommendations["dietary_suggestions"].append("多食温热性食物")
            recommendations["exercise_recommendations"].append("适度有氧运动，避免过度出汗")
        elif '阴虚' in const_type:
            recommendations["lifestyle_adjustments"].append("避免熬夜，保证充足睡眠")
            recommendations["dietary_suggestions"].append("多食滋阴润燥食物")
            recommendations["exercise_recommendations"].append("选择柔和的运动方式")
        
        # 基于风险评估生成建议
        risk_assessment = comprehensive_result.get('risk_assessment', {})
        risk_level = risk_assessment.get('level', '低风险')
        
        if risk_level in ['高风险', '中高风险']:
            recommendations["follow_up_schedule"]["next_assessment"] = "1个月内"
            recommendations["monitoring_advice"].append("密切关注身体变化")
        elif risk_level == '中等风险':
            recommendations["follow_up_schedule"]["next_assessment"] = "3个月内"
        else:
            recommendations["follow_up_schedule"]["next_assessment"] = "6个月内"
        
        # 基于子午流注生成时间建议
        if 'ziwu' in analysis_results and 'error' not in analysis_results['ziwu']:
            ziwu_result = analysis_results['ziwu']
            if 'best_treatment_time' in ziwu_result:
                recommendations["monitoring_advice"].append(
                    f"最佳调理时间: {ziwu_result['best_treatment_time']}"
                )
        
        return recommendations
    
    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        stats = self.performance_optimizer.optimization_stats
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests == 0:
            return 0.0
        return round(stats['cache_hits'] / total_requests, 4)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "optimization_stats": self.performance_optimizer.optimization_stats,
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "cache_size": len(self.performance_optimizer.calculation_cache),
            "algorithm_weights": {
                "ziwu": self.algorithm_weights.ziwu_weight,
                "constitution": self.algorithm_weights.constitution_weight,
                "bagua": self.algorithm_weights.bagua_weight,
                "wuyun_liuqi": self.algorithm_weights.wuyun_liuqi_weight
            },
            "precision_config": self.precision_config
        }
    
    async def clear_cache(self):
        """清理缓存"""
        self.performance_optimizer.calculation_cache.clear()
        self.historical_validator.validation_cache.clear()
        logger.info("算诊计算器缓存已清理")
    
    def _generate_health_advice(self, ziwu_result: Dict, constitution_result: Dict, 
                               bagua_result: Dict, wuyun_result: Dict) -> Dict[str, List[str]]:
        """
        生成健康建议（兼容测试）
        
        Args:
            ziwu_result: 子午流注分析结果
            constitution_result: 体质分析结果
            bagua_result: 八卦分析结果
            wuyun_result: 五运六气分析结果
            
        Returns:
            分类的健康建议
        """
        advice = {
            "饮食调养": [],
            "起居调养": [],
            "情志调养": [],
            "运动调养": []
        }
        
        # 基于子午流注的建议
        if "最佳治疗时间" in ziwu_result:
            best_times = ziwu_result["最佳治疗时间"]
            advice["起居调养"].append(f"最佳调理时间：{', '.join(best_times)}")
            advice["起居调养"].append("按照经络时间表安排作息")
        
        # 基于体质的建议
        if "体质类型" in constitution_result:
            constitution_type = constitution_result["体质类型"]
            if constitution_type == "平和质":
                advice["饮食调养"].extend(["饮食均衡", "五谷杂粮为主"])
                advice["运动调养"].append("适度运动，如太极、散步")
            elif "阳虚" in constitution_type:
                advice["饮食调养"].extend(["温热食物", "避免生冷"])
                advice["运动调养"].append("温和运动，避免大汗")
            elif "阴虚" in constitution_type:
                advice["饮食调养"].extend(["滋阴润燥", "多食甘凉食物"])
                advice["情志调养"].append("保持心情平静")
        
        # 基于八卦的建议
        if "本命卦" in bagua_result:
            benming_gua = bagua_result["本命卦"]
            if "乾" in benming_gua:
                advice["情志调养"].append("培养领导力，保持积极心态")
                advice["运动调养"].append("适合力量型运动")
            elif "坤" in benming_gua:
                advice["情志调养"].append("保持包容心态，稳重行事")
                advice["饮食调养"].append("注重脾胃调养")
        
        # 基于五运六气的建议
        if "总体特点" in wuyun_result:
            wuyun_feature = wuyun_result["总体特点"]
            if "木运" in wuyun_feature:
                advice["饮食调养"].append("疏肝理气，少食酸味")
                advice["情志调养"].append("保持心情舒畅，避免郁怒")
            elif "火运" in wuyun_feature:
                advice["饮食调养"].append("清热降火，多食苦味")
                advice["起居调养"].append("避免过度劳累")
            elif "土运" in wuyun_feature:
                advice["饮食调养"].append("健脾益胃，甘味适中")
                advice["运动调养"].append("适度运动，增强脾胃功能")
        
        # 去重并限制数量
        for category in advice:
            advice[category] = list(set(advice[category]))[:5]  # 每类最多5条建议
        
        return advice
    
    async def assess_health_risks(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        健康风险评估（兼容测试）
        
        Args:
            analysis_result: 综合分析结果
            
        Returns:
            健康风险评估结果
        """
        try:
            # 从分析结果中提取风险因素
            risk_factors = []
            
            # 从体质分析中提取风险
            if "体质分析" in analysis_result:
                constitution_analysis = analysis_result["体质分析"]
                if "易患疾病" in constitution_analysis:
                    risk_factors.extend(constitution_analysis["易患疾病"])
            
            # 从八卦分析中提取风险
            if "八卦分析" in analysis_result:
                bagua_analysis = analysis_result["八卦分析"]
                if "健康分析" in bagua_analysis:
                    health_analysis = bagua_analysis["健康分析"]
                    if "易患疾病" in health_analysis:
                        risk_factors.extend(health_analysis["易患疾病"])
            
            # 评估风险等级
            risk_level = "低"
            if len(risk_factors) > 5:
                risk_level = "高"
            elif len(risk_factors) > 2:
                risk_level = "中"
            
            # 生成预防建议
            prevention_advice = [
                "保持规律作息，早睡早起",
                "适当运动，增强体质",
                "饮食均衡，避免偏食",
                "定期体检，及时发现问题"
            ]
            
            if risk_factors:
                prevention_advice.append("针对易患疾病进行重点预防")
            
            return {
                "风险等级": risk_level,
                "主要风险": risk_factors[:5],  # 最多显示5个主要风险
                "预防建议": prevention_advice
            }
            
        except Exception as e:
            logger.error(f"健康风险评估失败: {e}")
            return {
                "风险等级": "未知",
                "主要风险": [],
                "预防建议": ["请咨询专业医师进行详细评估"]
            }
