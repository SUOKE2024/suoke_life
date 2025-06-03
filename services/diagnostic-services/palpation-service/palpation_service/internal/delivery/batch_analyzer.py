#!/usr/bin/env python

"""
切诊服务 - 批量分析模块
实现批量脉诊分析和比较功能
"""

import logging
import time
from datetime import datetime, timedelta

import grpc

# 导入生成的gRPC代码

logger = logging.getLogger(__name__)

class BatchAnalysisHandler:
    """批量分析处理器"""

    def __init__(self, session_repository, user_repository, pulse_processor, metrics):
        """
        初始化批量分析处理器

        Args:
            session_repository: 会话存储库
            user_repository: 用户存储库
            pulse_processor: 脉搏处理器
            metrics: 指标收集器
        """
        self.session_repository = session_repository
        self.user_repository = user_repository
        self.pulse_processor = pulse_processor
        self.metrics = metrics

    def handle_batch_analysis(
        self, request: pb2.BatchAnalysisRequest, context: grpc.ServicerContext
    ) -> pb2.BatchAnalysisResponse:
        """
        处理批量分析请求

        Args:
            request: 批量分析请求
            context: gRPC上下文

        Returns:
            批量分析响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id
            session_ids = list(request.session_ids)
            timeframe = request.timeframe

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return pb2.BatchAnalysisResponse(
                    success=False, error_message=f"User not found: {user_id}"
                )

            # 如果没有提供会话ID，则根据时间范围获取
            if not session_ids:
                session_ids = self._get_sessions_by_timeframe(user_id, timeframe)

                if not session_ids:
                    logger.warning(f"在指定时间范围内未找到会话: {user_id}")
                    return pb2.BatchAnalysisResponse(
                        success=False, error_message="No sessions found in the specified timeframe"
                    )

            # 获取各个会话的分析结果
            analysis_summaries = []

            for session_id in session_ids:
                session = self.session_repository.get_session(session_id)
                if not session:
                    logger.warning(f"会话不存在: {session_id}")
                    continue

                # 提取分析结果
                analysis_results = session.get("analysis_results", {})
                if not analysis_results:
                    logger.warning(f"会话没有分析结果: {session_id}")
                    continue

                # 创建分析摘要
                timestamp = session.get("start_time", 0)
                dominant_types = analysis_results.get("pulse_types", [])
                if isinstance(dominant_types, dict):
                    dominant_types = [k for k, v in dominant_types.items() if v > 0.5]

                main_patterns = []
                for pattern in analysis_results.get("tcm_patterns", []):
                    if isinstance(pattern, dict) and pattern.get("confidence", 0) > 0.6:
                        main_patterns.append(pattern.get("name", ""))

                summary = analysis_results.get("summary", "未提供分析摘要")

                analysis_summary = pb2.PulseAnalysisSummary(
                    session_id=session_id,
                    timestamp=int(timestamp),
                    dominant_pulse_types=dominant_types,
                    main_patterns=main_patterns,
                    summary=summary,
                )

                analysis_summaries.append(analysis_summary)

            # 如果没有有效的分析结果
            if not analysis_summaries:
                logger.warning(f"未找到有效的分析结果: {user_id}")
                return pb2.BatchAnalysisResponse(
                    success=False, error_message="No valid analysis results found"
                )

            # 按时间排序
            analysis_summaries.sort(key=lambda x: x.timestamp)

            # 生成趋势分析
            trend_analysis = self._generate_trend_analysis(analysis_summaries)

            # 记录指标
            self.metrics.record_counter(
                "batch_analyses", 1, {"user_id": user_id, "session_count": len(analysis_summaries)}
            )

            return pb2.BatchAnalysisResponse(
                analysis_summaries=analysis_summaries,
                trend_analysis=trend_analysis,
                success=True,
                error_message="",
            )

        except Exception as e:
            logger.exception(f"批量分析失败: {e!s}")
            self.metrics.record_counter("analysis_errors", 1, {"error_type": "batch_analysis"})

            return pb2.BatchAnalysisResponse(
                success=False, error_message=f"Failed to perform batch analysis: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("batch_analysis_latency", end_time - start_time)

    def handle_compare_pulse_sessions(
        self, request: pb2.ComparePulseSessionsRequest, context: grpc.ServicerContext
    ) -> pb2.ComparePulseSessionsResponse:
        """
        处理脉诊会话比较请求

        Args:
            request: 会话比较请求
            context: gRPC上下文

        Returns:
            会话比较响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id
            baseline_session_id = request.baseline_session_id
            comparison_session_id = request.comparison_session_id

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return pb2.ComparePulseSessionsResponse(
                    success=False, error_message=f"User not found: {user_id}"
                )

            # 获取基准会话
            baseline_session = self.session_repository.get_session(baseline_session_id)
            if not baseline_session:
                logger.error(f"基准会话不存在: {baseline_session_id}")
                return pb2.ComparePulseSessionsResponse(
                    success=False,
                    error_message=f"Baseline session not found: {baseline_session_id}",
                )

            # 获取比较会话
            comparison_session = self.session_repository.get_session(comparison_session_id)
            if not comparison_session:
                logger.error(f"比较会话不存在: {comparison_session_id}")
                return pb2.ComparePulseSessionsResponse(
                    success=False,
                    error_message=f"Comparison session not found: {comparison_session_id}",
                )

            # 提取基准会话特征
            baseline_features = baseline_session.get("features", {}).get("features", [])
            baseline_analysis = baseline_session.get("analysis_results", {})

            # 提取比较会话特征
            comparison_features = comparison_session.get("features", {}).get("features", [])
            comparison_analysis = comparison_session.get("analysis_results", {})

            # 比较特征变化
            changed_features = self._compare_features(baseline_features, comparison_features)

            # 比较证型变化
            baseline_patterns = [
                p.get("name")
                for p in baseline_analysis.get("tcm_patterns", [])
                if isinstance(p, dict) and p.get("confidence", 0) > 0.6
            ]

            comparison_patterns = [
                p.get("name")
                for p in comparison_analysis.get("tcm_patterns", [])
                if isinstance(p, dict) and p.get("confidence", 0) > 0.6
            ]

            # 新出现的证型
            new_patterns = [p for p in comparison_patterns if p not in baseline_patterns]

            # 已解决的证型
            resolved_patterns = [p for p in baseline_patterns if p not in comparison_patterns]

            # 持续存在的证型
            persisting_patterns = [p for p in comparison_patterns if p in baseline_patterns]

            # 生成比较总结
            comparison_summary = self._generate_comparison_summary(
                changed_features,
                new_patterns,
                resolved_patterns,
                persisting_patterns,
                baseline_session,
                comparison_session,
            )

            # 创建比较结果
            comparison_result = pb2.ComparisonResult(
                changed_features=changed_features,
                new_patterns=new_patterns,
                resolved_patterns=resolved_patterns,
                persisting_patterns=persisting_patterns,
                comparison_summary=comparison_summary,
            )

            # 记录指标
            self.metrics.record_counter("session_comparisons", 1, {"user_id": user_id})

            return pb2.ComparePulseSessionsResponse(
                comparison=comparison_result, success=True, error_message=""
            )

        except Exception as e:
            logger.exception(f"比较脉诊会话失败: {e!s}")
            self.metrics.record_counter("analysis_errors", 1, {"error_type": "compare_sessions"})

            return pb2.ComparePulseSessionsResponse(
                success=False, error_message=f"Failed to compare pulse sessions: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("session_comparison_latency", end_time - start_time)

    def handle_generate_report(
        self, request: pb2.GeneratePalpationReportRequest, context: grpc.ServicerContext
    ) -> pb2.GeneratePalpationReportResponse:
        """
        处理生成切诊报告请求

        Args:
            request: 报告生成请求
            context: gRPC上下文

        Returns:
            报告生成响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id
            analysis_id = request.analysis_id
            report_format = request.format
            include_recommendations = request.include_recommendations

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return pb2.GeneratePalpationReportResponse(
                    success=False, error_message=f"User not found: {user_id}"
                )

            # 获取分析结果
            analysis_result = self.session_repository.get_analysis_result(analysis_id)
            if not analysis_result:
                logger.error(f"分析结果不存在: {analysis_id}")
                return pb2.GeneratePalpationReportResponse(
                    success=False, error_message=f"Analysis result not found: {analysis_id}"
                )

            # 生成报告
            report_data, report_url = self._generate_report(
                user, analysis_result, report_format, include_recommendations
            )

            # 记录指标
            self.metrics.record_counter(
                "reports_generated", 1, {"format": pb2.ReportFormat.Name(report_format)}
            )

            return pb2.GeneratePalpationReportResponse(
                report_data=report_data, report_url=report_url, success=True, error_message=""
            )

        except Exception as e:
            logger.exception(f"生成切诊报告失败: {e!s}")
            self.metrics.record_counter("report_errors", 1, {"error_type": "generate_report"})

            return pb2.GeneratePalpationReportResponse(
                success=False, error_message=f"Failed to generate palpation report: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("report_generation_latency", end_time - start_time)

    def _get_sessions_by_timeframe(self, user_id, timeframe):
        """根据时间范围获取会话ID"""
        now = datetime.now()
        start_timestamp = timeframe.start_timestamp
        end_timestamp = timeframe.end_timestamp

        # 如果未指定具体时间范围，使用时间范围类型
        if start_timestamp == 0 or end_timestamp == 0:
            timeframe_type = timeframe.timeframe_type.lower()

            if timeframe_type == "day":
                start_timestamp = int((now - timedelta(days=1)).timestamp())
            elif timeframe_type == "week":
                start_timestamp = int((now - timedelta(weeks=1)).timestamp())
            elif timeframe_type == "month":
                start_timestamp = int((now - timedelta(days=30)).timestamp())
            elif timeframe_type == "year":
                start_timestamp = int((now - timedelta(days=365)).timestamp())
            else:
                # 默认使用一周
                start_timestamp = int((now - timedelta(weeks=1)).timestamp())

            end_timestamp = int(now.timestamp())

        # 查询会话
        return self.session_repository.get_session_ids_by_timeframe(
            user_id, start_timestamp, end_timestamp
        )

    def _compare_features(self, baseline_features, comparison_features):
        """比较两个会话的特征变化"""
        changed_features = []

        # 创建基准特征字典
        baseline_dict = {}
        for feature in baseline_features:
            if isinstance(feature, dict):
                key = f"{feature.get('name')}_{feature.get('position')}"
                baseline_dict[key] = feature.get("value", 0)

        # 比较特征
        for feature in comparison_features:
            if isinstance(feature, dict):
                name = feature.get("name", "")
                position = feature.get("position", "")
                key = f"{name}_{position}"

                if key in baseline_dict:
                    baseline_value = baseline_dict[key]
                    current_value = feature.get("value", 0)

                    # 计算变化百分比
                    if baseline_value != 0:
                        change_percentage = (
                            (current_value - baseline_value) / abs(baseline_value) * 100
                        )
                    else:
                        change_percentage = 0

                    # 确定变化显著性
                    significance = "显著" if abs(change_percentage) > 20 else "轻微"

                    # 只添加有意义的变化
                    if abs(change_percentage) > 5:
                        changed_feature = pb2.ChangedFeature(
                            feature_name=name,
                            baseline_value=baseline_value,
                            current_value=current_value,
                            change_percentage=change_percentage,
                            change_significance=significance,
                        )
                        changed_features.append(changed_feature)

        # 按变化百分比排序
        changed_features.sort(key=lambda x: abs(x.change_percentage), reverse=True)

        # 只返回最显著的变化
        return changed_features[:10] if len(changed_features) > 10 else changed_features

    def _generate_trend_analysis(self, analysis_summaries):
        """生成趋势分析"""
        if len(analysis_summaries) < 2:
            return pb2.TrendAnalysis(
                improving_aspects=[],
                worsening_aspects=[],
                stable_aspects=["数据点不足，无法进行趋势分析"],
                overall_trend="数据不足",
            )

        # 收集第一个和最后一个分析的主要特征
        first_analysis = analysis_summaries[0]
        last_analysis = analysis_summaries[-1]

        # 收集所有出现过的脉象类型和证型
        all_pulse_types = set()
        all_patterns = set()

        for summary in analysis_summaries:
            all_pulse_types.update(summary.dominant_pulse_types)
            all_patterns.update(summary.main_patterns)

        # 分析改善、恶化和稳定的方面
        improving_aspects = []
        worsening_aspects = []
        stable_aspects = []

        # 分析脉象变化
        good_pulse_types = {"MODERATE", "和脉"}  # 正常脉象
        bad_pulse_types = {
            "RAPID",
            "FAINT",
            "INTERMITTENT",
            "SCATTERED",
            "数脉",
            "微脉",
            "代脉",
            "散脉",
        }  # 异常脉象

        first_bad_count = sum(
            1 for t in first_analysis.dominant_pulse_types if t in bad_pulse_types
        )
        last_bad_count = sum(1 for t in last_analysis.dominant_pulse_types if t in bad_pulse_types)

        first_good_count = sum(
            1 for t in first_analysis.dominant_pulse_types if t in good_pulse_types
        )
        last_good_count = sum(
            1 for t in last_analysis.dominant_pulse_types if t in good_pulse_types
        )

        if last_bad_count < first_bad_count or last_good_count > first_good_count:
            improving_aspects.append("脉象趋于平和")
        elif last_bad_count > first_bad_count or last_good_count < first_good_count:
            worsening_aspects.append("脉象趋于异常")
        else:
            stable_aspects.append("脉象基本稳定")

        # 分析证型变化
        first_patterns = set(first_analysis.main_patterns)
        last_patterns = set(last_analysis.main_patterns)

        # 判断是否好转（证型减少或变轻）
        if len(last_patterns) < len(first_patterns):
            improving_aspects.append("证型数量减少")
        elif len(last_patterns) > len(first_patterns):
            worsening_aspects.append("证型数量增加")
        else:
            stable_aspects.append("证型数量稳定")

        # 确定整体趋势
        if len(improving_aspects) > len(worsening_aspects):
            overall_trend = "整体趋势向好"
        elif len(improving_aspects) < len(worsening_aspects):
            overall_trend = "整体趋势变差"
        else:
            overall_trend = "整体趋势稳定"

        return pb2.TrendAnalysis(
            improving_aspects=improving_aspects,
            worsening_aspects=worsening_aspects,
            stable_aspects=stable_aspects,
            overall_trend=overall_trend,
        )

    def _generate_comparison_summary(
        self,
        changed_features,
        new_patterns,
        resolved_patterns,
        persisting_patterns,
        baseline_session,
        comparison_session,
    ):
        """生成比较摘要"""
        summary_parts = []

        # 计算基准和比较会话的时间间隔
        baseline_time = baseline_session.get("start_time", 0)
        comparison_time = comparison_session.get("start_time", 0)

        days_diff = (comparison_time - baseline_time) / (24 * 3600)
        time_desc = f"相隔{int(days_diff)}天" if days_diff >= 1 else "同一天内"

        summary_parts.append(f"本次比较{time_desc}的两次切诊结果")

        # 添加特征变化摘要
        if changed_features:
            significant_changes = [f for f in changed_features if abs(f.change_percentage) > 20]
            if significant_changes:
                change_desc = []
                for feature in significant_changes[:3]:
                    direction = "增加" if feature.change_percentage > 0 else "减少"
                    change_desc.append(
                        f"{feature.feature_name}{direction}{abs(int(feature.change_percentage))}%"
                    )

                summary_parts.append(f"主要变化：{', '.join(change_desc)}")

        # 添加证型变化摘要
        pattern_changes = []

        if new_patterns:
            pattern_changes.append(f"新出现证型：{', '.join(new_patterns)}")

        if resolved_patterns:
            pattern_changes.append(f"已改善证型：{', '.join(resolved_patterns)}")

        if persisting_patterns:
            pattern_changes.append(f"持续存在证型：{', '.join(persisting_patterns)}")

        if pattern_changes:
            summary_parts.append("；".join(pattern_changes))

        # 添加整体评估
        if len(new_patterns) > len(resolved_patterns):
            summary_parts.append("整体评估：状况有所恶化")
        elif len(new_patterns) < len(resolved_patterns):
            summary_parts.append("整体评估：状况有所改善")
        else:
            summary_parts.append("整体评估：状况基本稳定")

        return "；".join(summary_parts) + "。"

    def _generate_report(self, user, analysis_result, report_format, include_recommendations):
        """生成报告数据和URL"""
        # 此处应该实现实际的报告生成逻辑
        # 为简化示例，我们返回一个简单的JSON字符串和空URL

        import json

        report_data = json.dumps(analysis_result, ensure_ascii=False).encode("utf-8")
        report_url = ""

        # TODO: 实现实际的报告生成逻辑，包括PDF、HTML等格式

        return report_data, report_url
