#!/usr/bin/env python

"""
切诊服务 - 综合分析模块
实现综合切诊分析功能
"""

import logging
import time
import uuid

import grpc

# 导入生成的gRPC代码

logger = logging.getLogger(__name__)

class ComprehensiveAnalysisHandler:
    """综合分析处理器"""

    def __init__(
        self,
        session_repository,
        user_repository,
        pulse_processor,
        abdominal_analyzer,
        skin_analyzer,
        metrics,
    ):
        """
        初始化综合分析处理器

        Args:
            session_repository: 会话存储库
            user_repository: 用户存储库
            pulse_processor: 脉搏处理器
            abdominal_analyzer: 腹诊分析器
            skin_analyzer: 皮肤分析器
            metrics: 指标收集器
        """
        self.session_repository = session_repository
        self.user_repository = user_repository
        self.pulse_processor = pulse_processor
        self.abdominal_analyzer = abdominal_analyzer
        self.skin_analyzer = skin_analyzer
        self.metrics = metrics

    def handle_comprehensive_analysis(
        self, request: pb2.ComprehensiveAnalysisRequest, context: grpc.ServicerContext
    ) -> pb2.ComprehensiveAnalysisResponse:
        """
        处理综合切诊分析请求

        Args:
            request: 综合分析请求
            context: gRPC上下文

        Returns:
            综合分析结果响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id
            pulse_session_id = request.pulse_session_id
            include_abdominal = request.include_abdominal
            include_skin = request.include_skin

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return pb2.ComprehensiveAnalysisResponse(
                    analysis_id="", success=False, error_message=f"User not found: {user_id}"
                )

            # 获取脉诊会话数据
            pulse_session = self.session_repository.get_session(pulse_session_id)
            if not pulse_session:
                logger.error(f"脉诊会话不存在: {pulse_session_id}")
                return pb2.ComprehensiveAnalysisResponse(
                    analysis_id="",
                    success=False,
                    error_message=f"Pulse session not found: {pulse_session_id}",
                )

            # 获取最新的腹诊和皮肤触诊数据
            abdominal_data = None
            skin_data = None

            if include_abdominal:
                abdominal_data = self.user_repository.get_latest_abdominal_data(user_id)

            if include_skin:
                skin_data = self.user_repository.get_latest_skin_data(user_id)

            # 创建分析ID
            analysis_id = str(uuid.uuid4())

            # 处理脉诊分析
            pulse_analysis = pulse_session.get("analysis_results", {})
            pulse_features = pulse_session.get("features", {})

            pulse_overview = pb2.PulseOverview(
                dominant_pulse_type=pulse_analysis.get("dominant_type", "未知"),
                pulse_quality=pulse_analysis.get("quality", "未知"),
                rhythm_description=pulse_analysis.get("rhythm", "未知"),
                notable_features=pulse_analysis.get("notable_features", []),
            )

            # 处理腹诊分析
            abdominal_overview = pb2.AbdominalOverview(notable_regions=[], overall_condition="未知")

            if include_abdominal and abdominal_data:
                abdominal_findings = abdominal_data.get("findings", [])
                notable_regions = []
                for finding in abdominal_findings:
                    if finding.get("severity", 0) > 0.6:
                        region_name = finding.get("region_name", "")
                        if region_name and region_name not in notable_regions:
                            notable_regions.append(region_name)

                abdominal_overview = pb2.AbdominalOverview(
                    notable_regions=notable_regions,
                    overall_condition=abdominal_data.get("overall_condition", "未知"),
                )

            # 处理皮肤触诊分析
            skin_overview = pb2.SkinOverview(
                overall_moisture="未知",
                overall_elasticity="未知",
                overall_temperature="未知",
                notable_regions=[],
            )

            if include_skin and skin_data:
                skin_findings = skin_data.get("findings", [])
                notable_regions = []
                for finding in skin_findings:
                    if finding.get("severity", 0) > 0.6:
                        region_name = finding.get("region_name", "")
                        if region_name and region_name not in notable_regions:
                            notable_regions.append(region_name)

                skin_condition = skin_data.get("overall_condition", {})
                skin_overview = pb2.SkinOverview(
                    overall_moisture=skin_condition.get("moisture", "未知"),
                    overall_elasticity=skin_condition.get("elasticity", "未知"),
                    overall_temperature=skin_condition.get("temperature", "未知"),
                    notable_regions=notable_regions,
                )

            # 生成综合概览
            overview = pb2.PalpationOverview(
                pulse=pulse_overview,
                abdominal=abdominal_overview,
                skin=skin_overview,
                general_condition=self._generate_general_condition(
                    pulse_analysis, abdominal_data, skin_data
                ),
            )

            # 映射到中医证型
            tcm_patterns = self._map_to_tcm_patterns(pulse_analysis, abdominal_data, skin_data)

            # 生成健康警报
            health_alerts = self._generate_health_alerts(pulse_analysis, abdominal_data, skin_data)

            # 生成综合摘要
            summary = self._generate_comprehensive_summary(overview, tcm_patterns, health_alerts)

            # 记录分析结果
            analysis_result = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "timestamp": time.time(),
                "pulse_session_id": pulse_session_id,
                "included_abdominal": include_abdominal,
                "included_skin": include_skin,
                "overview": {
                    "pulse": {
                        "dominant_type": pulse_overview.dominant_pulse_type,
                        "quality": pulse_overview.pulse_quality,
                        "rhythm": pulse_overview.rhythm_description,
                        "notable_features": list(pulse_overview.notable_features),
                    },
                    "abdominal": {
                        "notable_regions": list(abdominal_overview.notable_regions),
                        "overall_condition": abdominal_overview.overall_condition,
                    },
                    "skin": {
                        "overall_moisture": skin_overview.overall_moisture,
                        "overall_elasticity": skin_overview.overall_elasticity,
                        "overall_temperature": skin_overview.overall_temperature,
                        "notable_regions": list(skin_overview.notable_regions),
                    },
                    "general_condition": overview.general_condition,
                },
                "tcm_patterns": [
                    {
                        "name": pattern.pattern_name,
                        "element": pattern.element,
                        "nature": pattern.nature,
                        "confidence": pattern.confidence,
                        "description": pattern.description,
                        "supporting_findings": list(pattern.supporting_findings),
                    }
                    for pattern in tcm_patterns
                ],
                "health_alerts": [
                    {
                        "type": alert.alert_type,
                        "description": alert.description,
                        "severity": alert.severity,
                        "recommendation": alert.recommendation,
                        "requires_immediate_attention": alert.requires_immediate_attention,
                    }
                    for alert in health_alerts
                ],
                "summary": summary,
            }

            # 保存分析结果
            self.session_repository.save_analysis_result(analysis_id, analysis_result)

            # 记录指标
            self.metrics.record_counter(
                "comprehensive_analyses",
                1,
                {"included_abdominal": str(include_abdominal), "included_skin": str(include_skin)},
            )

            return pb2.ComprehensiveAnalysisResponse(
                analysis_id=analysis_id,
                overview=overview,
                tcm_patterns=tcm_patterns,
                health_alerts=health_alerts,
                summary=summary,
                success=True,
                error_message="",
            )

        except Exception as e:
            logger.exception(f"生成综合切诊分析失败: {e!s}")
            self.metrics.record_counter(
                "analysis_errors", 1, {"error_type": "comprehensive_analysis"}
            )

            return pb2.ComprehensiveAnalysisResponse(
                analysis_id="",
                success=False,
                error_message=f"Failed to generate comprehensive palpation analysis: {e!s}",
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("comprehensive_analysis_latency", end_time - start_time)

    def _generate_general_condition(self, pulse_analysis, abdominal_data, skin_data):
        """生成总体状况描述"""
        conditions = []

        # 脉诊状况
        if pulse_analysis:
            if "dominant_type" in pulse_analysis and pulse_analysis["dominant_type"] != "未知":
                conditions.append(f"脉象主要表现为{pulse_analysis['dominant_type']}")

        # 腹诊状况
        if abdominal_data and "analysis_summary" in abdominal_data:
            conditions.append(abdominal_data["analysis_summary"])

        # 皮肤状况
        if skin_data and "analysis_summary" in skin_data:
            conditions.append(skin_data["analysis_summary"])

        if not conditions:
            return "整体状况良好，未见明显异常"

        return "；".join(conditions) + "。"

    def _map_to_tcm_patterns(self, pulse_analysis, abdominal_data, skin_data):
        """映射到中医证型"""
        # 收集所有证型
        all_patterns = []

        # 脉诊证型
        if pulse_analysis and "tcm_patterns" in pulse_analysis:
            for pattern in pulse_analysis["tcm_patterns"]:
                all_patterns.append(
                    pb2.TCMPattern(
                        pattern_name=pattern.get("name", ""),
                        element=pattern.get("element", ""),
                        nature=pattern.get("nature", ""),
                        confidence=pattern.get("confidence", 0.0),
                        description=pattern.get("description", ""),
                        supporting_findings=pattern.get("supporting_findings", []),
                    )
                )

        # 腹诊证型
        if abdominal_data and "tcm_patterns" in abdominal_data:
            for pattern in abdominal_data["tcm_patterns"]:
                # 检查是否已存在相同证型
                exists = False
                for existing in all_patterns:
                    if existing.pattern_name == pattern.get("name", ""):
                        # 更新置信度和支持发现
                        new_confidence = (existing.confidence + pattern.get("confidence", 0.0)) / 2
                        existing.confidence = new_confidence
                        existing.supporting_findings.extend(pattern.get("supporting_findings", []))
                        exists = True
                        break

                if not exists:
                    all_patterns.append(
                        pb2.TCMPattern(
                            pattern_name=pattern.get("name", ""),
                            element=pattern.get("element", ""),
                            nature=pattern.get("nature", ""),
                            confidence=pattern.get("confidence", 0.0),
                            description=pattern.get("description", ""),
                            supporting_findings=pattern.get("supporting_findings", []),
                        )
                    )

        # 皮肤触诊证型
        if skin_data and "tcm_patterns" in skin_data:
            for pattern in skin_data["tcm_patterns"]:
                # 检查是否已存在相同证型
                exists = False
                for existing in all_patterns:
                    if existing.pattern_name == pattern.get("name", ""):
                        # 更新置信度和支持发现
                        new_confidence = (existing.confidence + pattern.get("confidence", 0.0)) / 2
                        existing.confidence = new_confidence
                        existing.supporting_findings.extend(pattern.get("supporting_findings", []))
                        exists = True
                        break

                if not exists:
                    all_patterns.append(
                        pb2.TCMPattern(
                            pattern_name=pattern.get("name", ""),
                            element=pattern.get("element", ""),
                            nature=pattern.get("nature", ""),
                            confidence=pattern.get("confidence", 0.0),
                            description=pattern.get("description", ""),
                            supporting_findings=pattern.get("supporting_findings", []),
                        )
                    )

        # 按置信度排序
        return sorted(all_patterns, key=lambda x: x.confidence, reverse=True)

    def _generate_health_alerts(self, pulse_analysis, abdominal_data, skin_data):
        """生成健康警报"""
        alerts = []

        # 脉诊警报
        if pulse_analysis and "health_alerts" in pulse_analysis:
            for alert in pulse_analysis["health_alerts"]:
                alerts.append(
                    pb2.HealthAlert(
                        alert_type=alert.get("type", ""),
                        description=alert.get("description", ""),
                        severity=alert.get("severity", 0.0),
                        recommendation=alert.get("recommendation", ""),
                        requires_immediate_attention=alert.get(
                            "requires_immediate_attention", False
                        ),
                    )
                )

        # 腹诊警报
        if abdominal_data and "health_alerts" in abdominal_data:
            for alert in abdominal_data["health_alerts"]:
                alerts.append(
                    pb2.HealthAlert(
                        alert_type=alert.get("type", ""),
                        description=alert.get("description", ""),
                        severity=alert.get("severity", 0.0),
                        recommendation=alert.get("recommendation", ""),
                        requires_immediate_attention=alert.get(
                            "requires_immediate_attention", False
                        ),
                    )
                )

        # 皮肤触诊警报
        if skin_data and "health_alerts" in skin_data:
            for alert in skin_data["health_alerts"]:
                alerts.append(
                    pb2.HealthAlert(
                        alert_type=alert.get("type", ""),
                        description=alert.get("description", ""),
                        severity=alert.get("severity", 0.0),
                        recommendation=alert.get("recommendation", ""),
                        requires_immediate_attention=alert.get(
                            "requires_immediate_attention", False
                        ),
                    )
                )

        # 按严重性排序
        return sorted(alerts, key=lambda x: x.severity, reverse=True)

    def _generate_comprehensive_summary(self, overview, tcm_patterns, health_alerts):
        """生成综合摘要"""
        summary_parts = []

        # 添加总体状况
        if overview.general_condition:
            summary_parts.append(overview.general_condition)

        # 添加主要证型
        if tcm_patterns:
            top_patterns = tcm_patterns[:3] if len(tcm_patterns) > 3 else tcm_patterns
            pattern_names = [p.pattern_name for p in top_patterns if p.confidence > 0.6]
            if pattern_names:
                summary_parts.append(f"主要证型为{'、'.join(pattern_names)}")

        # 添加健康警报
        if health_alerts:
            urgent_alerts = [a for a in health_alerts if a.requires_immediate_attention]
            if urgent_alerts:
                alert_descs = [a.description for a in urgent_alerts]
                summary_parts.append(f"需要注意的健康问题：{'、'.join(alert_descs)}")

        # 添加建议
        recommendations = []

        for alert in health_alerts:
            if alert.recommendation and alert.recommendation not in recommendations:
                recommendations.append(alert.recommendation)

        if recommendations:
            summary_parts.append(f"建议：{'；'.join(recommendations[:3])}")

        if not summary_parts:
            return "综合切诊分析未发现明显异常，建议保持现有生活习惯。"

        return "；".join(summary_parts) + "。"
