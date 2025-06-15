"""
AI分析任务

处理异步的AI分析工作，包括：
- 文本内容分析
- 图像内容分析
- 风险评估
- 质量评分
"""
import logging
from typing import Any, Dict, List, Optional

from internal.ai.text_analyzer import TextAnalyzer
from internal.tasks.celery_app import celery_app, task_with_retry

logger = logging.getLogger(__name__)

# 全局AI分析器实例
text_analyzer = TextAnalyzer()


@task_with_retry(name='ai_tasks.analyze_text_content')
def analyze_text_content(content: str, content_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    分析文本内容
    
    Args:
        content: 文本内容
        content_type: 内容类型
        context: 上下文信息
        
    Returns:
        分析结果
    """
    try:
        logger.info(f"开始分析文本内容，类型: {content_type}")
        
        # 执行文本分析
        import asyncio
        result = asyncio.run(text_analyzer.analyze_text(content, context))
        
        logger.info(f"文本分析完成，评分: {result.get('overall_score', 0)}")
        
        return {
            'success': True,
            'content_type': content_type,
            'analysis_result': result,
            'processing_time': result.get('metadata', {}).get('processing_time', 0)
        }
        
    except Exception as e:
        logger.error(f"文本分析失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'content_type': content_type
        }


@task_with_retry(name='ai_tasks.analyze_image_content')
def analyze_image_content(image_url: str, content_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    分析图像内容
    
    Args:
        image_url: 图像URL
        content_type: 内容类型
        context: 上下文信息
        
    Returns:
        分析结果
    """
    try:
        logger.info(f"开始分析图像内容: {image_url}")
        
        # 这里应该实现图像分析逻辑
        # 暂时返回模拟结果
        result = {
            'overall_score': 0.8,
            'risk_level': 'low',
            'confidence': 0.9,
            'detected_objects': [],
            'safety_score': 0.95,
            'quality_score': 0.85,
            'metadata': {
                'image_url': image_url,
                'processing_time': 2.5
            }
        }
        
        logger.info(f"图像分析完成，评分: {result.get('overall_score', 0)}")
        
        return {
            'success': True,
            'content_type': content_type,
            'analysis_result': result,
            'processing_time': result.get('metadata', {}).get('processing_time', 0)
        }
        
    except Exception as e:
        logger.error(f"图像分析失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'content_type': content_type
        }


@task_with_retry(name='ai_tasks.batch_analyze_content')
def batch_analyze_content(content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量分析内容
    
    Args:
        content_items: 内容项列表，每项包含content, content_type, context等字段
        
    Returns:
        批量分析结果
    """
    try:
        logger.info(f"开始批量分析 {len(content_items)} 个内容项")
        
        results = []
        for i, item in enumerate(content_items):
            try:
                content = item.get('content', '')
                content_type = item.get('content_type', 'text')
                context = item.get('context', {})
                
                if content_type == 'text':
                    result = analyze_text_content.apply(args=[content, content_type, context])
                    results.append({
                        'index': i,
                        'item_id': item.get('id'),
                        'result': result.get()
                    })
                elif content_type == 'image':
                    image_url = item.get('image_url', '')
                    result = analyze_image_content.apply(args=[image_url, content_type, context])
                    results.append({
                        'index': i,
                        'item_id': item.get('id'),
                        'result': result.get()
                    })
                else:
                    results.append({
                        'index': i,
                        'item_id': item.get('id'),
                        'result': {
                            'success': False,
                            'error': f'不支持的内容类型: {content_type}'
                        }
                    })
                    
            except Exception as e:
                logger.error(f"分析第 {i} 个内容项失败: {e}")
                results.append({
                    'index': i,
                    'item_id': item.get('id'),
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        success_count = sum(1 for r in results if r['result'].get('success', False))
        
        logger.info(f"批量分析完成，成功: {success_count}/{len(content_items)}")
        
        return {
            'success': True,
            'total_items': len(content_items),
            'success_count': success_count,
            'failed_count': len(content_items) - success_count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_items': len(content_items) if content_items else 0
        }


@task_with_retry(name='ai_tasks.calculate_risk_score')
def calculate_risk_score(content: str, content_type: str, additional_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    计算风险评分
    
    Args:
        content: 内容
        content_type: 内容类型
        additional_factors: 额外风险因素
        
    Returns:
        风险评分结果
    """
    try:
        logger.info(f"开始计算风险评分，内容类型: {content_type}")
        
        # 基础风险分析
        if content_type == 'text':
            import asyncio
            analysis_result = asyncio.run(text_analyzer.analyze_text(content))
            base_risk_score = analysis_result.get('risk', {}).get('score', 0.5)
            risk_level = analysis_result.get('risk_level', 'medium')
        else:
            # 其他类型的风险分析
            base_risk_score = 0.5
            risk_level = 'medium'
        
        # 考虑额外风险因素
        additional_risk = 0.0
        risk_factors = []
        
        if additional_factors:
            # 用户历史风险
            if additional_factors.get('user_risk_history', 0) > 0.7:
                additional_risk += 0.2
                risk_factors.append('用户历史风险较高')
            
            # 内容来源风险
            if additional_factors.get('source_risk', 0) > 0.6:
                additional_risk += 0.15
                risk_factors.append('内容来源风险较高')
            
            # 时间敏感性
            if additional_factors.get('time_sensitive', False):
                additional_risk += 0.1
                risk_factors.append('时间敏感内容')
        
        # 计算最终风险评分
        final_risk_score = min(1.0, base_risk_score + additional_risk)
        
        # 重新评估风险等级
        if final_risk_score >= 0.8:
            final_risk_level = 'high'
        elif final_risk_score >= 0.5:
            final_risk_level = 'medium'
        elif final_risk_score >= 0.2:
            final_risk_level = 'low'
        else:
            final_risk_level = 'very_low'
        
        logger.info(f"风险评分计算完成，评分: {final_risk_score}, 等级: {final_risk_level}")
        
        return {
            'success': True,
            'risk_score': final_risk_score,
            'risk_level': final_risk_level,
            'base_risk_score': base_risk_score,
            'additional_risk': additional_risk,
            'risk_factors': risk_factors,
            'confidence': 0.85
        }
        
    except Exception as e:
        logger.error(f"风险评分计算失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'risk_score': 0.5,
            'risk_level': 'medium'
        }


@task_with_retry(name='ai_tasks.generate_review_suggestions')
def generate_review_suggestions(content: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成审核建议
    
    Args:
        content: 原始内容
        analysis_result: AI分析结果
        
    Returns:
        审核建议
    """
    try:
        logger.info("开始生成审核建议")
        
        suggestions = []
        priority = 'medium'
        
        # 基于分析结果生成建议
        overall_score = analysis_result.get('overall_score', 0.5)
        risk_level = analysis_result.get('risk_level', 'medium')
        
        if overall_score < 0.3:
            suggestions.append({
                'type': 'quality',
                'message': '内容质量较低，建议仔细审核',
                'severity': 'high'
            })
            priority = 'high'
        
        if risk_level in ['high', 'very_high']:
            suggestions.append({
                'type': 'risk',
                'message': '检测到高风险内容，需要专业审核',
                'severity': 'high'
            })
            priority = 'high'
        
        # 合规性建议
        compliance_result = analysis_result.get('compliance', {})
        if not compliance_result.get('is_compliant', True):
            violations = compliance_result.get('violations', [])
            for violation in violations:
                suggestions.append({
                    'type': 'compliance',
                    'message': f'合规性问题: {violation.get("type", "未知")}',
                    'severity': violation.get('severity', 'medium')
                })
            if any(v.get('severity') == 'high' for v in violations):
                priority = 'high'
        
        # 医学内容建议
        medical_result = analysis_result.get('medical', {})
        if medical_result.get('is_medical_content', False):
            suggestions.append({
                'type': 'medical',
                'message': '检测到医学相关内容，建议医学专家审核',
                'severity': 'medium'
            })
            if priority == 'low':
                priority = 'medium'
        
        # 如果没有特殊建议，给出通用建议
        if not suggestions:
            if overall_score > 0.8:
                suggestions.append({
                    'type': 'general',
                    'message': '内容质量良好，可快速审核',
                    'severity': 'low'
                })
                priority = 'low'
            else:
                suggestions.append({
                    'type': 'general',
                    'message': '建议进行常规审核',
                    'severity': 'medium'
                })
        
        # 生成审核要点
        review_points = []
        
        # 关键词检查
        keywords_result = analysis_result.get('keywords', {})
        if keywords_result.get('medical_terms'):
            review_points.append('重点关注医学术语的准确性')
        
        # 情感分析
        sentiment_result = analysis_result.get('sentiment', {})
        if sentiment_result.get('sentiment') == 'negative':
            review_points.append('注意负面情感表达的合理性')
        
        logger.info(f"审核建议生成完成，优先级: {priority}, 建议数: {len(suggestions)}")
        
        return {
            'success': True,
            'priority': priority,
            'suggestions': suggestions,
            'review_points': review_points,
            'estimated_time': _estimate_review_time(analysis_result),
            'recommended_reviewer_type': _recommend_reviewer_type(analysis_result)
        }
        
    except Exception as e:
        logger.error(f"生成审核建议失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'priority': 'medium',
            'suggestions': []
        }


def _estimate_review_time(analysis_result: Dict[str, Any]) -> int:
    """估算审核时间（分钟）"""
    base_time = 5  # 基础审核时间
    
    # 根据内容复杂度调整
    overall_score = analysis_result.get('overall_score', 0.5)
    if overall_score < 0.3:
        base_time += 10  # 低质量内容需要更多时间
    
    # 根据风险等级调整
    risk_level = analysis_result.get('risk_level', 'medium')
    if risk_level == 'high':
        base_time += 15
    elif risk_level == 'medium':
        base_time += 5
    
    # 根据医学内容调整
    medical_result = analysis_result.get('medical', {})
    if medical_result.get('is_medical_content', False):
        base_time += 10
    
    return min(60, base_time)  # 最多60分钟


def _recommend_reviewer_type(analysis_result: Dict[str, Any]) -> str:
    """推荐审核员类型"""
    medical_result = analysis_result.get('medical', {})
    if medical_result.get('is_medical_content', False):
        return 'medical_expert'
    
    risk_level = analysis_result.get('risk_level', 'medium')
    if risk_level == 'high':
        return 'senior_reviewer'
    
    overall_score = analysis_result.get('overall_score', 0.5)
    if overall_score > 0.8:
        return 'junior_reviewer'
    
    return 'general_reviewer'


@celery_app.task(name='ai_tasks.health_check')
def ai_health_check() -> Dict[str, Any]:
    """AI模块健康检查"""
    try:
        # 检查文本分析器
        import asyncio
        text_health = asyncio.run(text_analyzer.health_check())
        
        return {
            'status': 'healthy' if text_health.get('status') == 'healthy' else 'unhealthy',
            'text_analyzer': text_health,
            'timestamp': str(logger.handlers[0].formatter.formatTime(logger.makeRecord('', 0, '', 0, '', (), None)))
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        } 