#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能报告生成器
根据用户背景生成个性化健康报告，使用自然语言生成技术
提供可视化图表和趋势分析，支持多语言和多格式输出
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import base64
import io
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """报告类型枚举"""
    BASIC = "basic"           # 基础报告
    DETAILED = "detailed"     # 详细报告
    PROFESSIONAL = "professional"  # 专业报告
    SUMMARY = "summary"       # 摘要报告

class ReportFormat(Enum):
    """报告格式枚举"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"

class Language(Enum):
    """语言枚举"""
    ZH_CN = "zh_cn"  # 简体中文
    ZH_TW = "zh_tw"  # 繁体中文
    EN_US = "en_us"  # 英语
    JA_JP = "ja_jp"  # 日语

@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    charts: List[str] = field(default_factory=list)  # 图表的base64编码
    importance: int = 1  # 重要性等级 1-5
    recommendations: List[str] = field(default_factory=list)

@dataclass
class HealthReport:
    """健康报告"""
    report_id: str
    user_id: str
    session_id: str
    report_type: ReportType
    language: Language
    generated_at: datetime
    sections: List[ReportSection]
    summary: str
    overall_score: float
    risk_level: str
    recommendations: List[str]
    follow_up_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntelligentReportGenerator:
    """智能报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能报告生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 报告配置
        self.default_language = Language(config.get('default_language', 'zh_cn'))
        self.default_format = ReportFormat(config.get('default_format', 'html'))
        self.template_dir = config.get('template_dir', 'templates/reports')
        self.output_dir = config.get('output_dir', 'output/reports')
        
        # 图表配置
        self.chart_config = config.get('chart_config', {})
        self.chart_style = self.chart_config.get('style', 'seaborn-v0_8')
        self.chart_dpi = self.chart_config.get('dpi', 300)
        self.chart_figsize = tuple(self.chart_config.get('figsize', [12, 8]))
        
        # 自然语言生成配置
        self.nlg_config = config.get('nlg_config', {})
        self.use_ai_generation = self.nlg_config.get('use_ai', False)
        self.template_based = self.nlg_config.get('template_based', True)
        
        # 个性化配置
        self.personalization = config.get('personalization', {})
        self.age_groups = self.personalization.get('age_groups', {
            'young': (0, 30),
            'middle': (30, 60),
            'senior': (60, 120)
        })
        
        # 初始化组件
        self.template_env = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.font_paths = {}
        
        # 语言模板
        self.language_templates = {
            Language.ZH_CN: self._load_chinese_templates(),
            Language.EN_US: self._load_english_templates()
        }
        
        # 健康评级标准
        self.health_grades = {
            'excellent': (0.9, 1.0),
            'good': (0.8, 0.9),
            'fair': (0.6, 0.8),
            'poor': (0.4, 0.6),
            'critical': (0.0, 0.4)
        }
        
        self._initialize_components()
        
        logger.info("智能报告生成器初始化完成")
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化模板环境
            if Path(self.template_dir).exists():
                self.template_env = Environment(
                    loader=FileSystemLoader(self.template_dir),
                    autoescape=True
                )
            
            # 创建输出目录
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # 设置matplotlib中文字体
            self._setup_fonts()
            
            # 设置图表样式
            plt.style.use('default')
            sns.set_palette("husl")
            
            logger.info("报告生成器组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    def _setup_fonts(self):
        """设置字体"""
        try:
            # 尝试设置中文字体
            chinese_fonts = [
                'SimHei', 'Microsoft YaHei', 'DejaVu Sans',
                'WenQuanYi Micro Hei', 'Noto Sans CJK SC'
            ]
            
            for font_name in chinese_fonts:
                try:
                    plt.rcParams['font.sans-serif'] = [font_name]
                    plt.rcParams['axes.unicode_minus'] = False
                    # 测试字体
                    fig, ax = plt.subplots(figsize=(1, 1))
                    ax.text(0.5, 0.5, '测试', fontsize=12)
                    plt.close(fig)
                    self.font_paths['chinese'] = font_name
                    logger.info(f"设置中文字体: {font_name}")
                    break
                except Exception:
                    continue
            
        except Exception as e:
            logger.warning(f"字体设置失败: {e}")
    
    def _load_chinese_templates(self) -> Dict[str, str]:
        """加载中文模板"""
        return {
            'summary_excellent': "您的整体健康状况非常优秀，各项指标均在正常范围内。",
            'summary_good': "您的整体健康状况良好，大部分指标正常，建议继续保持。",
            'summary_fair': "您的健康状况一般，部分指标需要关注和改善。",
            'summary_poor': "您的健康状况较差，多项指标异常，建议及时就医。",
            'summary_critical': "您的健康状况堪忧，存在严重风险，请立即就医。",
            
            'pulse_analysis': "脉象分析显示您的{pulse_type}，{pulse_description}。",
            'constitution_analysis': "根据中医体质辨识，您属于{constitution_type}体质。",
            'recommendation_exercise': "建议进行适量的{exercise_type}运动。",
            'recommendation_diet': "饮食方面建议{diet_advice}。",
            'recommendation_lifestyle': "生活方式建议{lifestyle_advice}。",
            
            'risk_low': "风险等级：低风险",
            'risk_medium': "风险等级：中等风险",
            'risk_high': "风险等级：高风险",
            
            'follow_up_1week': "建议1周后复查",
            'follow_up_1month': "建议1个月后复查",
            'follow_up_3months': "建议3个月后复查",
            'follow_up_6months': "建议6个月后复查"
        }
    
    def _load_english_templates(self) -> Dict[str, str]:
        """加载英文模板"""
        return {
            'summary_excellent': "Your overall health condition is excellent with all indicators within normal ranges.",
            'summary_good': "Your overall health condition is good with most indicators normal. Continue maintaining current habits.",
            'summary_fair': "Your health condition is fair with some indicators requiring attention and improvement.",
            'summary_poor': "Your health condition is poor with multiple abnormal indicators. Medical consultation is recommended.",
            'summary_critical': "Your health condition is critical with serious risks. Please seek immediate medical attention.",
            
            'pulse_analysis': "Pulse analysis shows {pulse_type}, {pulse_description}.",
            'constitution_analysis': "According to TCM constitution identification, you have {constitution_type} constitution.",
            'recommendation_exercise': "Recommend moderate {exercise_type} exercise.",
            'recommendation_diet': "Dietary recommendations: {diet_advice}.",
            'recommendation_lifestyle': "Lifestyle recommendations: {lifestyle_advice}.",
            
            'risk_low': "Risk Level: Low Risk",
            'risk_medium': "Risk Level: Medium Risk",
            'risk_high': "Risk Level: High Risk",
            
            'follow_up_1week': "Recommend follow-up in 1 week",
            'follow_up_1month': "Recommend follow-up in 1 month",
            'follow_up_3months': "Recommend follow-up in 3 months",
            'follow_up_6months': "Recommend follow-up in 6 months"
        }
    
    async def generate_comprehensive_report(
        self,
        session_id: str,
        analysis_results: Dict[str, Any],
        user_profile: Dict[str, Any],
        report_type: ReportType = ReportType.DETAILED,
        language: Optional[Language] = None,
        format_type: ReportFormat = ReportFormat.HTML
    ) -> HealthReport:
        """
        生成综合健康报告
        
        Args:
            session_id: 会话ID
            analysis_results: 分析结果
            user_profile: 用户档案
            report_type: 报告类型
            language: 语言
            format_type: 格式类型
            
        Returns:
            健康报告
        """
        try:
            # 设置默认语言
            if language is None:
                language = self.default_language
            
            # 生成报告ID
            report_id = f"report_{session_id}_{int(datetime.now().timestamp())}"
            
            # 分析数据并生成各个章节
            sections = await self._generate_report_sections(
                analysis_results, user_profile, language, report_type
            )
            
            # 生成总体评估
            overall_score, risk_level = await self._calculate_overall_assessment(analysis_results)
            
            # 生成摘要
            summary = await self._generate_summary(
                analysis_results, user_profile, overall_score, language
            )
            
            # 生成建议
            recommendations = await self._generate_recommendations(
                analysis_results, user_profile, language
            )
            
            # 计算随访时间
            follow_up_date = await self._calculate_follow_up_date(overall_score, risk_level)
            
            # 创建报告对象
            report = HealthReport(
                report_id=report_id,
                user_id=user_profile.get('user_id', 'unknown'),
                session_id=session_id,
                report_type=report_type,
                language=language,
                generated_at=datetime.now(),
                sections=sections,
                summary=summary,
                overall_score=overall_score,
                risk_level=risk_level,
                recommendations=recommendations,
                follow_up_date=follow_up_date,
                metadata={
                    'format': format_type.value,
                    'generation_time': datetime.now().isoformat(),
                    'user_age': user_profile.get('age'),
                    'user_gender': user_profile.get('gender')
                }
            )
            
            logger.info(f"综合报告生成完成: {report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            raise
    
    async def _generate_report_sections(
        self,
        analysis_results: Dict[str, Any],
        user_profile: Dict[str, Any],
        language: Language,
        report_type: ReportType
    ) -> List[ReportSection]:
        """生成报告章节"""
        sections = []
        
        # 1. 基本信息章节
        basic_section = await self._generate_basic_info_section(
            user_profile, language
        )
        sections.append(basic_section)
        
        # 2. 脉象分析章节
        if 'comprehensive_features' in analysis_results:
            pulse_section = await self._generate_pulse_analysis_section(
                analysis_results, language
            )
            sections.append(pulse_section)
        
        # 3. 体质分析章节
        if 'constitution_type' in analysis_results:
            constitution_section = await self._generate_constitution_section(
                analysis_results, language
            )
            sections.append(constitution_section)
        
        # 4. 健康评估章节
        if 'health_assessment' in analysis_results:
            health_section = await self._generate_health_assessment_section(
                analysis_results, language
            )
            sections.append(health_section)
        
        # 5. 趋势分析章节（如果有历史数据）
        if report_type in [ReportType.DETAILED, ReportType.PROFESSIONAL]:
            trend_section = await self._generate_trend_analysis_section(
                analysis_results, language
            )
            if trend_section:
                sections.append(trend_section)
        
        # 6. 预测分析章节（专业报告）
        if report_type == ReportType.PROFESSIONAL and 'prediction' in analysis_results:
            prediction_section = await self._generate_prediction_section(
                analysis_results, language
            )
            sections.append(prediction_section)
        
        return sections
    
    async def _generate_basic_info_section(
        self,
        user_profile: Dict[str, Any],
        language: Language
    ) -> ReportSection:
        """生成基本信息章节"""
        templates = self.language_templates[language]
        
        if language == Language.ZH_CN:
            title = "基本信息"
            content = f"""
            姓名：{user_profile.get('name', '未提供')}
            年龄：{user_profile.get('age', '未提供')}岁
            性别：{user_profile.get('gender', '未提供')}
            检测时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}
            """
        else:
            title = "Basic Information"
            content = f"""
            Name: {user_profile.get('name', 'Not provided')}
            Age: {user_profile.get('age', 'Not provided')} years old
            Gender: {user_profile.get('gender', 'Not provided')}
            Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
        
        return ReportSection(
            title=title,
            content=content.strip(),
            importance=1
        )
    
    async def _generate_pulse_analysis_section(
        self,
        analysis_results: Dict[str, Any],
        language: Language
    ) -> ReportSection:
        """生成脉象分析章节"""
        features = analysis_results.get('comprehensive_features', {})
        
        # 生成脉象图表
        charts = []
        pulse_chart = await self._create_pulse_features_chart(features, language)
        if pulse_chart:
            charts.append(pulse_chart)
        
        # 生成文本内容
        if language == Language.ZH_CN:
            title = "脉象分析"
            content = await self._generate_pulse_analysis_text_zh(features)
        else:
            title = "Pulse Analysis"
            content = await self._generate_pulse_analysis_text_en(features)
        
        return ReportSection(
            title=title,
            content=content,
            charts=charts,
            importance=5
        )
    
    async def _generate_pulse_analysis_text_zh(self, features: Dict[str, Any]) -> str:
        """生成中文脉象分析文本"""
        heart_rate = features.get('heart_rate', 70)
        hrv = features.get('heart_rate_variability', 0.5)
        rhythm = features.get('rhythm_regularity', 0.8)
        
        content = f"""
        脉象特征分析：
        
        • 心率：{heart_rate:.0f}次/分钟
        • 心率变异性：{hrv:.2f}
        • 节律规整度：{rhythm:.2f}
        
        """
        
        # 根据数值生成评价
        if 60 <= heart_rate <= 100:
            content += "心率在正常范围内。"
        elif heart_rate < 60:
            content += "心率偏慢，可能提示心动过缓。"
        else:
            content += "心率偏快，可能提示心动过速。"
        
        if hrv > 0.4:
            content += "心率变异性良好，提示自主神经功能正常。"
        else:
            content += "心率变异性偏低，建议关注心血管健康。"
        
        return content
    
    async def _generate_pulse_analysis_text_en(self, features: Dict[str, Any]) -> str:
        """生成英文脉象分析文本"""
        heart_rate = features.get('heart_rate', 70)
        hrv = features.get('heart_rate_variability', 0.5)
        rhythm = features.get('rhythm_regularity', 0.8)
        
        content = f"""
        Pulse Feature Analysis:
        
        • Heart Rate: {heart_rate:.0f} bpm
        • Heart Rate Variability: {hrv:.2f}
        • Rhythm Regularity: {rhythm:.2f}
        
        """
        
        # Generate evaluation based on values
        if 60 <= heart_rate <= 100:
            content += "Heart rate is within normal range. "
        elif heart_rate < 60:
            content += "Heart rate is low, may indicate bradycardia. "
        else:
            content += "Heart rate is high, may indicate tachycardia. "
        
        if hrv > 0.4:
            content += "Heart rate variability is good, indicating normal autonomic function."
        else:
            content += "Heart rate variability is low, recommend attention to cardiovascular health."
        
        return content
    
    async def _generate_constitution_section(
        self,
        analysis_results: Dict[str, Any],
        language: Language
    ) -> ReportSection:
        """生成体质分析章节"""
        constitution_type = analysis_results.get('constitution_type', 'unknown')
        
        # 生成体质图表
        charts = []
        constitution_chart = await self._create_constitution_chart(constitution_type, language)
        if constitution_chart:
            charts.append(constitution_chart)
        
        if language == Language.ZH_CN:
            title = "中医体质分析"
            content = await self._generate_constitution_text_zh(constitution_type)
        else:
            title = "TCM Constitution Analysis"
            content = await self._generate_constitution_text_en(constitution_type)
        
        return ReportSection(
            title=title,
            content=content,
            charts=charts,
            importance=4
        )
    
    async def _generate_constitution_text_zh(self, constitution_type: str) -> str:
        """生成中文体质分析文本"""
        constitution_descriptions = {
            'balanced': "平和体质：体质均衡，身体健康状态良好。",
            'qi_deficiency': "气虚体质：元气不足，容易疲劳，需要补气调理。",
            'yang_deficiency': "阳虚体质：阳气不足，畏寒怕冷，需要温阳补肾。",
            'yin_deficiency': "阴虚体质：阴液不足，容易上火，需要滋阴润燥。",
            'phlegm_dampness': "痰湿体质：痰湿内盛，容易肥胖，需要化痰除湿。",
            'damp_heat': "湿热体质：湿热内蕴，容易长痘，需要清热利湿。",
            'blood_stasis': "血瘀体质：血液运行不畅，需要活血化瘀。",
            'qi_stagnation': "气郁体质：气机不畅，情绪波动大，需要疏肝理气。",
            'special': "特禀体质：先天禀赋不足，容易过敏，需要调补先天。"
        }
        
        description = constitution_descriptions.get(constitution_type, "体质类型未明确。")
        
        content = f"""
        体质类型：{constitution_type}
        
        {description}
        
        调理建议：
        • 根据体质特点调整饮食结构
        • 选择适合的运动方式
        • 保持良好的作息习惯
        • 必要时寻求专业中医指导
        """
        
        return content
    
    async def _generate_constitution_text_en(self, constitution_type: str) -> str:
        """生成英文体质分析文本"""
        constitution_descriptions = {
            'balanced': "Balanced Constitution: Well-balanced constitution with good health status.",
            'qi_deficiency': "Qi Deficiency: Insufficient vital energy, prone to fatigue, needs qi tonification.",
            'yang_deficiency': "Yang Deficiency: Insufficient yang qi, cold intolerance, needs yang warming.",
            'yin_deficiency': "Yin Deficiency: Insufficient yin fluid, prone to heat symptoms, needs yin nourishment.",
            'phlegm_dampness': "Phlegm-Dampness: Excessive phlegm and dampness, prone to obesity, needs dampness elimination.",
            'damp_heat': "Damp-Heat: Internal damp-heat, prone to acne, needs heat clearing and dampness draining.",
            'blood_stasis': "Blood Stasis: Poor blood circulation, needs blood activation and stasis removal.",
            'qi_stagnation': "Qi Stagnation: Poor qi circulation, emotional fluctuations, needs liver qi regulation.",
            'special': "Special Constitution: Congenital deficiency, prone to allergies, needs constitutional strengthening."
        }
        
        description = constitution_descriptions.get(constitution_type, "Constitution type unclear.")
        
        content = f"""
        Constitution Type: {constitution_type}
        
        {description}
        
        Adjustment Recommendations:
        • Adjust diet according to constitution characteristics
        • Choose suitable exercise methods
        • Maintain good sleep habits
        • Seek professional TCM guidance when necessary
        """
        
        return content
    
    async def _generate_health_assessment_section(
        self,
        analysis_results: Dict[str, Any],
        language: Language
    ) -> ReportSection:
        """生成健康评估章节"""
        health_assessment = analysis_results.get('health_assessment', {})
        overall_score = health_assessment.get('overall_score', 0.7)
        
        # 生成健康评估图表
        charts = []
        health_chart = await self._create_health_assessment_chart(health_assessment, language)
        if health_chart:
            charts.append(health_chart)
        
        if language == Language.ZH_CN:
            title = "健康评估"
            content = await self._generate_health_assessment_text_zh(health_assessment)
        else:
            title = "Health Assessment"
            content = await self._generate_health_assessment_text_en(health_assessment)
        
        recommendations = health_assessment.get('recommendations', [])
        
        return ReportSection(
            title=title,
            content=content,
            charts=charts,
            recommendations=recommendations,
            importance=5
        )
    
    async def _generate_health_assessment_text_zh(self, health_assessment: Dict[str, Any]) -> str:
        """生成中文健康评估文本"""
        overall_score = health_assessment.get('overall_score', 0.7)
        risk_factors = health_assessment.get('risk_factors', [])
        
        # 确定健康等级
        grade = self._get_health_grade(overall_score)
        grade_descriptions = {
            'excellent': '优秀',
            'good': '良好',
            'fair': '一般',
            'poor': '较差',
            'critical': '危险'
        }
        
        content = f"""
        整体健康评分：{overall_score:.1f}/1.0
        健康等级：{grade_descriptions.get(grade, '未知')}
        
        """
        
        if risk_factors:
            content += "风险因素：\n"
            for risk in risk_factors:
                content += f"• {risk}\n"
        else:
            content += "未发现明显风险因素。\n"
        
        return content
    
    async def _generate_health_assessment_text_en(self, health_assessment: Dict[str, Any]) -> str:
        """生成英文健康评估文本"""
        overall_score = health_assessment.get('overall_score', 0.7)
        risk_factors = health_assessment.get('risk_factors', [])
        
        # Determine health grade
        grade = self._get_health_grade(overall_score)
        grade_descriptions = {
            'excellent': 'Excellent',
            'good': 'Good',
            'fair': 'Fair',
            'poor': 'Poor',
            'critical': 'Critical'
        }
        
        content = f"""
        Overall Health Score: {overall_score:.1f}/1.0
        Health Grade: {grade_descriptions.get(grade, 'Unknown')}
        
        """
        
        if risk_factors:
            content += "Risk Factors:\n"
            for risk in risk_factors:
                content += f"• {risk}\n"
        else:
            content += "No significant risk factors identified.\n"
        
        return content
    
    async def _generate_trend_analysis_section(
        self,
        analysis_results: Dict[str, Any],
        language: Language
    ) -> Optional[ReportSection]:
        """生成趋势分析章节"""
        # 这里应该从历史数据中分析趋势
        # 目前返回模拟数据
        
        if language == Language.ZH_CN:
            title = "趋势分析"
            content = """
            基于历史数据的趋势分析：
            
            • 心率变化趋势：稳定
            • 体质变化趋势：逐步改善
            • 整体健康趋势：向好发展
            
            建议继续保持当前的健康管理方式。
            """
        else:
            title = "Trend Analysis"
            content = """
            Trend analysis based on historical data:
            
            • Heart rate trend: Stable
            • Constitution trend: Gradually improving
            • Overall health trend: Positive development
            
            Recommend continuing current health management approach.
            """
        
        return ReportSection(
            title=title,
            content=content,
            importance=3
        )
    
    async def _generate_prediction_section(
        self,
        analysis_results: Dict[str, Any],
        language: Language
    ) -> ReportSection:
        """生成预测分析章节"""
        prediction = analysis_results.get('prediction', {})
        
        if language == Language.ZH_CN:
            title = "健康预测"
            content = f"""
            基于当前健康状况的预测分析：
            
            健康趋势：{prediction.get('health_trend', '稳定')}
            
            风险预测：
            • 心血管风险：{prediction.get('risk_prediction', {}).get('cardiovascular_risk', 0.2):.1%}
            • 代谢风险：{prediction.get('risk_prediction', {}).get('metabolic_risk', 0.15):.1%}
            • 免疫风险：{prediction.get('risk_prediction', {}).get('immune_risk', 0.1):.1%}
            
            预测置信度：{prediction.get('confidence', 0.75):.1%}
            """
        else:
            title = "Health Prediction"
            content = f"""
            Predictive analysis based on current health status:
            
            Health Trend: {prediction.get('health_trend', 'stable')}
            
            Risk Prediction:
            • Cardiovascular Risk: {prediction.get('risk_prediction', {}).get('cardiovascular_risk', 0.2):.1%}
            • Metabolic Risk: {prediction.get('risk_prediction', {}).get('metabolic_risk', 0.15):.1%}
            • Immune Risk: {prediction.get('risk_prediction', {}).get('immune_risk', 0.1):.1%}
            
            Prediction Confidence: {prediction.get('confidence', 0.75):.1%}
            """
        
        return ReportSection(
            title=title,
            content=content,
            importance=4
        )
    
    async def _create_pulse_features_chart(
        self,
        features: Dict[str, Any],
        language: Language
    ) -> Optional[str]:
        """创建脉象特征图表"""
        try:
            # 提取关键特征
            feature_names = ['心率', '心率变异性', '节律规整度', '脉搏强度'] if language == Language.ZH_CN else \
                           ['Heart Rate', 'HRV', 'Rhythm', 'Pulse Strength']
            
            feature_values = [
                features.get('heart_rate', 70) / 100,  # 归一化
                features.get('heart_rate_variability', 0.5),
                features.get('rhythm_regularity', 0.8),
                features.get('pulse_strength', 0.6)
            ]
            
            # 创建雷达图
            fig, ax = plt.subplots(figsize=self.chart_figsize, subplot_kw=dict(projection='polar'))
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(feature_names), endpoint=False)
            angles = np.concatenate((angles, [angles[0]]))  # 闭合图形
            
            feature_values = feature_values + [feature_values[0]]  # 闭合数据
            
            # 绘制雷达图
            ax.plot(angles, feature_values, 'o-', linewidth=2, label='当前值' if language == Language.ZH_CN else 'Current')
            ax.fill(angles, feature_values, alpha=0.25)
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(feature_names)
            ax.set_ylim(0, 1)
            
            # 设置标题
            title = '脉象特征分析' if language == Language.ZH_CN else 'Pulse Feature Analysis'
            ax.set_title(title, size=16, fontweight='bold', pad=20)
            
            # 保存为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=self.chart_dpi, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return chart_base64
            
        except Exception as e:
            logger.error(f"脉象特征图表生成失败: {e}")
            return None
    
    async def _create_constitution_chart(
        self,
        constitution_type: str,
        language: Language
    ) -> Optional[str]:
        """创建体质分析图表"""
        try:
            # 体质类型和对应的特征值（模拟数据）
            constitution_features = {
                'balanced': [0.8, 0.8, 0.8, 0.8, 0.8],
                'qi_deficiency': [0.4, 0.6, 0.5, 0.7, 0.6],
                'yang_deficiency': [0.3, 0.5, 0.4, 0.6, 0.5],
                'yin_deficiency': [0.6, 0.4, 0.7, 0.5, 0.6],
                'phlegm_dampness': [0.5, 0.7, 0.3, 0.4, 0.5]
            }
            
            features = constitution_features.get(constitution_type, [0.5, 0.5, 0.5, 0.5, 0.5])
            
            feature_names = ['气血', '阴阳', '脏腑', '经络', '体质'] if language == Language.ZH_CN else \
                           ['Qi-Blood', 'Yin-Yang', 'Organs', 'Meridians', 'Constitution']
            
            # 创建条形图
            fig, ax = plt.subplots(figsize=self.chart_figsize)
            
            bars = ax.bar(feature_names, features, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
            
            # 设置标题和标签
            title = f'{constitution_type}体质特征' if language == Language.ZH_CN else f'{constitution_type} Constitution Features'
            ax.set_title(title, size=16, fontweight='bold')
            ax.set_ylabel('特征值' if language == Language.ZH_CN else 'Feature Value')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for bar, value in zip(bars, features):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.2f}', ha='center', va='bottom')
            
            # 保存为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=self.chart_dpi, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return chart_base64
            
        except Exception as e:
            logger.error(f"体质分析图表生成失败: {e}")
            return None
    
    async def _create_health_assessment_chart(
        self,
        health_assessment: Dict[str, Any],
        language: Language
    ) -> Optional[str]:
        """创建健康评估图表"""
        try:
            overall_score = health_assessment.get('overall_score', 0.7)
            
            # 创建仪表盘样式的图表
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 绘制半圆仪表盘
            theta = np.linspace(0, np.pi, 100)
            
            # 背景半圆
            ax.plot(np.cos(theta), np.sin(theta), 'lightgray', linewidth=20)
            
            # 根据分数确定颜色
            if overall_score >= 0.8:
                color = 'green'
            elif overall_score >= 0.6:
                color = 'orange'
            else:
                color = 'red'
            
            # 分数对应的角度
            score_theta = np.linspace(0, np.pi * overall_score, int(100 * overall_score))
            ax.plot(np.cos(score_theta), np.sin(score_theta), color, linewidth=20)
            
            # 添加指针
            pointer_angle = np.pi * overall_score
            ax.arrow(0, 0, 0.8 * np.cos(pointer_angle), 0.8 * np.sin(pointer_angle),
                    head_width=0.05, head_length=0.05, fc='black', ec='black')
            
            # 添加分数文本
            ax.text(0, -0.3, f'{overall_score:.1f}', ha='center', va='center', 
                   fontsize=24, fontweight='bold')
            
            # 设置标题
            title = '健康评分' if language == Language.ZH_CN else 'Health Score'
            ax.set_title(title, size=16, fontweight='bold', pad=20)
            
            # 设置坐标轴
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.5, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # 保存为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=self.chart_dpi, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return chart_base64
            
        except Exception as e:
            logger.error(f"健康评估图表生成失败: {e}")
            return None
    
    async def _calculate_overall_assessment(
        self,
        analysis_results: Dict[str, Any]
    ) -> Tuple[float, str]:
        """计算整体评估"""
        health_assessment = analysis_results.get('health_assessment', {})
        overall_score = health_assessment.get('overall_score', 0.7)
        
        # 确定风险等级
        if overall_score >= 0.8:
            risk_level = 'low'
        elif overall_score >= 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return overall_score, risk_level
    
    async def _generate_summary(
        self,
        analysis_results: Dict[str, Any],
        user_profile: Dict[str, Any],
        overall_score: float,
        language: Language
    ) -> str:
        """生成报告摘要"""
        templates = self.language_templates[language]
        
        # 根据分数选择摘要模板
        grade = self._get_health_grade(overall_score)
        summary_key = f'summary_{grade}'
        
        base_summary = templates.get(summary_key, "健康状况评估完成。")
        
        # 个性化调整
        age = user_profile.get('age', 30)
        if age < 30:
            age_advice = "年轻人应注重预防保健。" if language == Language.ZH_CN else "Young people should focus on preventive care."
        elif age < 60:
            age_advice = "中年人应定期体检。" if language == Language.ZH_CN else "Middle-aged people should have regular check-ups."
        else:
            age_advice = "老年人应加强健康监测。" if language == Language.ZH_CN else "Elderly people should strengthen health monitoring."
        
        return f"{base_summary} {age_advice}"
    
    async def _generate_recommendations(
        self,
        analysis_results: Dict[str, Any],
        user_profile: Dict[str, Any],
        language: Language
    ) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        templates = self.language_templates[language]
        
        # 基于健康评估的建议
        health_assessment = analysis_results.get('health_assessment', {})
        existing_recommendations = health_assessment.get('recommendations', [])
        recommendations.extend(existing_recommendations)
        
        # 基于体质的建议
        constitution_type = analysis_results.get('constitution_type', '')
        if constitution_type:
            constitution_advice = self._get_constitution_advice(constitution_type, language)
            recommendations.extend(constitution_advice)
        
        # 基于年龄的建议
        age = user_profile.get('age', 30)
        age_advice = self._get_age_specific_advice(age, language)
        recommendations.extend(age_advice)
        
        return recommendations[:10]  # 限制建议数量
    
    def _get_constitution_advice(self, constitution_type: str, language: Language) -> List[str]:
        """获取体质相关建议"""
        if language == Language.ZH_CN:
            advice_map = {
                'qi_deficiency': ['多食用补气食物如山药、红枣', '适量运动，避免过度劳累', '保证充足睡眠'],
                'yang_deficiency': ['多食用温热食物', '避免生冷食物', '适当进行温和运动'],
                'yin_deficiency': ['多食用滋阴食物如银耳、百合', '避免辛辣刺激食物', '保持心情平和'],
                'phlegm_dampness': ['清淡饮食，少食油腻', '适当运动促进代谢', '保持环境干燥'],
                'damp_heat': ['清热利湿饮食', '避免辛辣油腻食物', '适当运动排汗']
            }
        else:
            advice_map = {
                'qi_deficiency': ['Eat qi-tonifying foods like yam and red dates', 'Moderate exercise, avoid overexertion', 'Ensure adequate sleep'],
                'yang_deficiency': ['Eat warm foods', 'Avoid cold foods', 'Engage in gentle exercise'],
                'yin_deficiency': ['Eat yin-nourishing foods like white fungus and lily', 'Avoid spicy foods', 'Maintain emotional balance'],
                'phlegm_dampness': ['Light diet, less greasy food', 'Moderate exercise to promote metabolism', 'Keep environment dry'],
                'damp_heat': ['Heat-clearing and dampness-draining diet', 'Avoid spicy and greasy foods', 'Moderate exercise to sweat']
            }
        
        return advice_map.get(constitution_type, [])
    
    def _get_age_specific_advice(self, age: int, language: Language) -> List[str]:
        """获取年龄相关建议"""
        if language == Language.ZH_CN:
            if age < 30:
                return ['建立良好的生活习惯', '注重营养均衡', '适当运动锻炼']
            elif age < 60:
                return ['定期体检', '注意工作压力管理', '保持适量运动']
            else:
                return ['加强健康监测', '注意慢性病预防', '保持社交活动']
        else:
            if age < 30:
                return ['Establish good lifestyle habits', 'Focus on balanced nutrition', 'Engage in appropriate exercise']
            elif age < 60:
                return ['Regular health check-ups', 'Manage work stress', 'Maintain moderate exercise']
            else:
                return ['Strengthen health monitoring', 'Prevent chronic diseases', 'Maintain social activities']
    
    async def _calculate_follow_up_date(self, overall_score: float, risk_level: str) -> Optional[datetime]:
        """计算随访日期"""
        now = datetime.now()
        
        if risk_level == 'high':
            return now + timedelta(weeks=1)
        elif risk_level == 'medium':
            return now + timedelta(weeks=4)
        else:
            return now + timedelta(weeks=12)
    
    def _get_health_grade(self, score: float) -> str:
        """获取健康等级"""
        for grade, (min_score, max_score) in self.health_grades.items():
            if min_score <= score <= max_score:
                return grade
        return 'unknown'
    
    async def export_report(
        self,
        report: HealthReport,
        format_type: ReportFormat = ReportFormat.HTML
    ) -> str:
        """
        导出报告
        
        Args:
            report: 健康报告
            format_type: 导出格式
            
        Returns:
            导出文件路径
        """
        try:
            if format_type == ReportFormat.HTML:
                return await self._export_html_report(report)
            elif format_type == ReportFormat.JSON:
                return await self._export_json_report(report)
            elif format_type == ReportFormat.MARKDOWN:
                return await self._export_markdown_report(report)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
                
        except Exception as e:
            logger.error(f"报告导出失败: {e}")
            raise
    
    async def _export_html_report(self, report: HealthReport) -> str:
        """导出HTML格式报告"""
        # 生成HTML内容
        html_content = await self._generate_html_content(report)
        
        # 保存文件
        filename = f"{report.report_id}.html"
        filepath = Path(self.output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    async def _generate_html_content(self, report: HealthReport) -> str:
        """生成HTML内容"""
        # 简单的HTML模板
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>健康报告 - {{ report.report_id }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .chart { text-align: center; margin: 20px 0; }
                .recommendations { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }
                .score { font-size: 24px; font-weight: bold; color: #2c3e50; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>健康报告</h1>
                <p>报告ID: {{ report.report_id }}</p>
                <p>生成时间: {{ report.generated_at.strftime('%Y年%m月%d日 %H:%M') }}</p>
            </div>
            
            <div class="section">
                <h2>总体评估</h2>
                <p class="score">健康评分: {{ "%.1f"|format(report.overall_score) }}/1.0</p>
                <p>风险等级: {{ report.risk_level }}</p>
                <p>{{ report.summary }}</p>
            </div>
            
            {% for section in report.sections %}
            <div class="section">
                <h2>{{ section.title }}</h2>
                <div>{{ section.content|replace('\n', '<br>')|safe }}</div>
                
                {% for chart in section.charts %}
                <div class="chart">
                    <img src="data:image/png;base64,{{ chart }}" alt="图表" style="max-width: 100%; height: auto;">
                </div>
                {% endfor %}
                
                {% if section.recommendations %}
                <div class="recommendations">
                    <h3>建议</h3>
                    <ul>
                    {% for rec in section.recommendations %}
                        <li>{{ rec }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            {% if report.recommendations %}
            <div class="section recommendations">
                <h2>综合建议</h2>
                <ul>
                {% for rec in report.recommendations %}
                    <li>{{ rec }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if report.follow_up_date %}
            <div class="section">
                <h2>随访建议</h2>
                <p>建议随访时间: {{ report.follow_up_date.strftime('%Y年%m月%d日') }}</p>
            </div>
            {% endif %}
        </body>
        </html>
        """
        
        # 使用Jinja2渲染模板
        from jinja2 import Template
        template = Template(html_template)
        return template.render(report=report)
    
    async def _export_json_report(self, report: HealthReport) -> str:
        """导出JSON格式报告"""
        # 转换为字典
        report_dict = {
            'report_id': report.report_id,
            'user_id': report.user_id,
            'session_id': report.session_id,
            'report_type': report.report_type.value,
            'language': report.language.value,
            'generated_at': report.generated_at.isoformat(),
            'summary': report.summary,
            'overall_score': report.overall_score,
            'risk_level': report.risk_level,
            'recommendations': report.recommendations,
            'follow_up_date': report.follow_up_date.isoformat() if report.follow_up_date else None,
            'sections': [
                {
                    'title': section.title,
                    'content': section.content,
                    'charts': section.charts,
                    'importance': section.importance,
                    'recommendations': section.recommendations
                }
                for section in report.sections
            ],
            'metadata': report.metadata
        }
        
        # 保存文件
        filename = f"{report.report_id}.json"
        filepath = Path(self.output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    async def _export_markdown_report(self, report: HealthReport) -> str:
        """导出Markdown格式报告"""
        md_content = f"""# 健康报告

**报告ID:** {report.report_id}  
**生成时间:** {report.generated_at.strftime('%Y年%m月%d日 %H:%M')}  

## 总体评估

**健康评分:** {report.overall_score:.1f}/1.0  
**风险等级:** {report.risk_level}  

{report.summary}

"""
        
        # 添加各个章节
        for section in report.sections:
            md_content += f"## {section.title}\n\n"
            md_content += f"{section.content}\n\n"
            
            if section.recommendations:
                md_content += "### 建议\n\n"
                for rec in section.recommendations:
                    md_content += f"- {rec}\n"
                md_content += "\n"
        
        # 添加综合建议
        if report.recommendations:
            md_content += "## 综合建议\n\n"
            for rec in report.recommendations:
                md_content += f"- {rec}\n"
            md_content += "\n"
        
        # 添加随访建议
        if report.follow_up_date:
            md_content += f"## 随访建议\n\n建议随访时间: {report.follow_up_date.strftime('%Y年%m月%d日')}\n"
        
        # 保存文件
        filename = f"{report.report_id}.md"
        filepath = Path(self.output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(filepath)
    
    def cleanup(self):
        """清理资源"""
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        logger.info("智能报告生成器资源清理完成") 