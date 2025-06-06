"""
evaluation_framework - 索克生活项目模块
"""

from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_score, recall_score, f1_score, ndcg_score
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional, Any, Tuple, Set
import asyncio
import json
import statistics

"""
高级评估框架

全面评估RAG系统的检索质量、生成质量、用户体验和系统性能
"""



class EvaluationMetric(Enum):
    """评估指标"""
    # 检索质量
    RETRIEVAL_PRECISION = "retrieval_precision"
    RETRIEVAL_RECALL = "retrieval_recall"
    RETRIEVAL_F1 = "retrieval_f1"
    RETRIEVAL_NDCG = "retrieval_ndcg"
    RETRIEVAL_MRR = "retrieval_mrr"  # Mean Reciprocal Rank
    
    # 生成质量
    GENERATION_RELEVANCE = "generation_relevance"
    GENERATION_ACCURACY = "generation_accuracy"
    GENERATION_COMPLETENESS = "generation_completeness"
    GENERATION_COHERENCE = "generation_coherence"
    GENERATION_SAFETY = "generation_safety"
    
    # 用户体验
    USER_SATISFACTION = "user_satisfaction"
    RESPONSE_TIME = "response_time"
    ENGAGEMENT_RATE = "engagement_rate"
    TASK_SUCCESS_RATE = "task_success_rate"
    
    # 系统性能
    THROUGHPUT = "throughput"
    LATENCY_P95 = "latency_p95"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"

class EvaluationLevel(Enum):
    """评估级别"""
    COMPONENT = "component"  # 组件级别
    SYSTEM = "system"       # 系统级别
    USER = "user"          # 用户级别
    BUSINESS = "business"   # 业务级别

class EvaluationMethod(Enum):
    """评估方法"""
    AUTOMATIC = "automatic"      # 自动评估
    HUMAN = "human"             # 人工评估
    HYBRID = "hybrid"           # 混合评估
    SIMULATION = "simulation"    # 仿真评估

@dataclass
class EvaluationCase:
    """评估用例"""
    id: str
    query: str
    expected_documents: List[str]  # 期望检索到的文档
    expected_response: str         # 期望的回答
    ground_truth: Dict[str, Any]   # 标准答案
    user_context: Dict[str, Any]   # 用户上下文
    evaluation_criteria: List[str] # 评估标准
    created_at: datetime

@dataclass
class EvaluationResult:
    """评估结果"""
    id: str
    case_id: str
    metric: EvaluationMetric
    score: float
    details: Dict[str, Any]
    method: EvaluationMethod
    evaluator: str
    timestamp: datetime

@dataclass
class SystemEvaluation:
    """系统评估"""
    id: str
    evaluation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    test_cases: List[str]
    results: Dict[EvaluationMetric, float]
    summary: Dict[str, Any]
    status: str

class EvaluationFramework:
    """高级评估框架"""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        evaluation_cases_db: Optional[Dict[str, EvaluationCase]] = None
    ):
        self.redis = redis_client
        self.evaluation_cases = evaluation_cases_db or {}
        
        # 评估结果存储
        self.evaluation_results: Dict[str, List[EvaluationResult]] = defaultdict(list)
        self.system_evaluations: Dict[str, SystemEvaluation] = {}
        
        # 评估器
        self.evaluators = {
            "retrieval": RetrievalEvaluator(),
            "generation": GenerationEvaluator(),
            "user_experience": UserExperienceEvaluator(),
            "system_performance": SystemPerformanceEvaluator()
        }
        
        # 基准数据
        self.benchmarks: Dict[str, Dict[EvaluationMetric, float]] = {}
        
        logger.info("评估框架初始化完成")
    
    async def create_evaluation_case(
        self,
        query: str,
        expected_documents: List[str],
        expected_response: str,
        ground_truth: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        evaluation_criteria: Optional[List[str]] = None
    ) -> str:
        """创建评估用例"""
        try:
            case_id = f"case_{datetime.now().timestamp()}"
            
            case = EvaluationCase(
                id=case_id,
                query=query,
                expected_documents=expected_documents,
                expected_response=expected_response,
                ground_truth=ground_truth,
                user_context=user_context or {},
                evaluation_criteria=evaluation_criteria or [],
                created_at=datetime.now()
            )
            
            self.evaluation_cases[case_id] = case
            
            # 存储到Redis
            await self._store_evaluation_case(case)
            
            logger.info(f"创建评估用例: {case_id}")
            return case_id
            
        except Exception as e:
            logger.error(f"创建评估用例失败: {e}")
            raise
    
    async def run_single_evaluation(
        self,
        case_id: str,
        rag_system: Any,  # RAG系统实例
        metrics: Optional[List[EvaluationMetric]] = None
    ) -> Dict[EvaluationMetric, EvaluationResult]:
        """运行单个评估用例"""
        try:
            case = self.evaluation_cases.get(case_id)
            if not case:
                raise ValueError(f"评估用例不存在: {case_id}")
            
            # 默认评估所有指标
            if metrics is None:
                metrics = list(EvaluationMetric)
            
            results = {}
            
            # 执行RAG查询
            rag_response = await self._execute_rag_query(rag_system, case)
            
            # 评估各项指标
            for metric in metrics:
                result = await self._evaluate_metric(case, rag_response, metric)
                if result:
                    results[metric] = result
                    self.evaluation_results[case_id].append(result)
            
            logger.info(f"完成单个评估: {case_id}, 指标数: {len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"运行单个评估失败: {e}")
            return {}
    
    async def run_batch_evaluation(
        self,
        case_ids: List[str],
        rag_system: Any,
        evaluation_name: str,
        metrics: Optional[List[EvaluationMetric]] = None
    ) -> str:
        """运行批量评估"""
        try:
            eval_id = f"eval_{datetime.now().timestamp()}"
            
            # 创建系统评估记录
            system_eval = SystemEvaluation(
                id=eval_id,
                evaluation_name=evaluation_name,
                start_time=datetime.now(),
                end_time=None,
                test_cases=case_ids,
                results={},
                summary={},
                status="running"
            )
            self.system_evaluations[eval_id] = system_eval
            
            # 运行所有测试用例
            all_results = {}
            for case_id in case_ids:
                case_results = await self.run_single_evaluation(case_id, rag_system, metrics)
                all_results[case_id] = case_results
            
            # 聚合结果
            aggregated_results = await self._aggregate_results(all_results, metrics or list(EvaluationMetric))
            
            # 更新系统评估
            system_eval.end_time = datetime.now()
            system_eval.results = aggregated_results
            system_eval.summary = await self._generate_evaluation_summary(all_results)
            system_eval.status = "completed"
            
            # 存储结果
            await self._store_system_evaluation(system_eval)
            
            logger.info(f"完成批量评估: {eval_id}, 用例数: {len(case_ids)}")
            return eval_id
            
        except Exception as e:
            logger.error(f"运行批量评估失败: {e}")
            return ""
    
    async def run_continuous_evaluation(
        self,
        rag_system: Any,
        duration_hours: int = 24,
        sample_rate: float = 0.1
    ) -> str:
        """运行持续评估"""
        try:
            eval_id = f"continuous_{datetime.now().timestamp()}"
            
            # 创建持续评估任务
            system_eval = SystemEvaluation(
                id=eval_id,
                evaluation_name="持续评估",
                start_time=datetime.now(),
                end_time=None,
                test_cases=[],
                results={},
                summary={},
                status="running"
            )
            self.system_evaluations[eval_id] = system_eval
            
            # 启动后台评估任务
            asyncio.create_task(
                self._continuous_evaluation_task(eval_id, rag_system, duration_hours, sample_rate)
            )
            
            logger.info(f"启动持续评估: {eval_id}")
            return eval_id
            
        except Exception as e:
            logger.error(f"启动持续评估失败: {e}")
            return ""
    
    async def get_evaluation_report(
        self,
        eval_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """获取评估报告"""
        try:
            system_eval = self.system_evaluations.get(eval_id)
            if not system_eval:
                return {}
            
            report = {
                "evaluation_id": eval_id,
                "evaluation_name": system_eval.evaluation_name,
                "start_time": system_eval.start_time.isoformat(),
                "end_time": system_eval.end_time.isoformat() if system_eval.end_time else None,
                "status": system_eval.status,
                "test_cases_count": len(system_eval.test_cases),
                "overall_scores": {
                    metric.value: score for metric, score in system_eval.results.items()
                },
                "summary": system_eval.summary
            }
            
            if include_details:
                # 添加详细结果
                detailed_results = {}
                for case_id in system_eval.test_cases:
                    case_results = self.evaluation_results.get(case_id, [])
                    detailed_results[case_id] = [
                        {
                            "metric": result.metric.value,
                            "score": result.score,
                            "details": result.details,
                            "method": result.method.value,
                            "timestamp": result.timestamp.isoformat()
                        }
                        for result in case_results
                    ]
                report["detailed_results"] = detailed_results
            
            return report
            
        except Exception as e:
            logger.error(f"获取评估报告失败: {e}")
            return {}
    
    async def compare_evaluations(
        self,
        eval_ids: List[str]
    ) -> Dict[str, Any]:
        """比较多个评估结果"""
        try:
            comparison = {
                "evaluations": [],
                "metric_comparison": {},
                "improvement_analysis": {},
                "recommendations": []
            }
            
            # 收集评估数据
            eval_data = []
            for eval_id in eval_ids:
                system_eval = self.system_evaluations.get(eval_id)
                if system_eval:
                    eval_data.append({
                        "id": eval_id,
                        "name": system_eval.evaluation_name,
                        "timestamp": system_eval.start_time,
                        "results": system_eval.results
                    })
            
            # 按时间排序
            eval_data.sort(key=lambda x: x["timestamp"])
            comparison["evaluations"] = eval_data
            
            # 指标比较
            for metric in EvaluationMetric:
                metric_scores = []
                for eval_info in eval_data:
                    if metric in eval_info["results"]:
                        metric_scores.append(eval_info["results"][metric])
                
                if metric_scores:
                    comparison["metric_comparison"][metric.value] = {
                        "scores": metric_scores,
                        "trend": "improving" if len(metric_scores) > 1 and metric_scores[-1] > metric_scores[0] else "declining",
                        "best_score": max(metric_scores),
                        "worst_score": min(metric_scores),
                        "average": statistics.mean(metric_scores),
                        "std_dev": statistics.stdev(metric_scores) if len(metric_scores) > 1 else 0
                    }
            
            # 改进分析
            if len(eval_data) > 1:
                latest = eval_data[-1]["results"]
                previous = eval_data[-2]["results"]
                
                for metric in EvaluationMetric:
                    if metric in latest and metric in previous:
                        improvement = latest[metric] - previous[metric]
                        comparison["improvement_analysis"][metric.value] = {
                            "change": improvement,
                            "percentage_change": (improvement / previous[metric]) * 100 if previous[metric] != 0 else 0,
                            "status": "improved" if improvement > 0 else "declined" if improvement < 0 else "stable"
                        }
            
            # 生成建议
            comparison["recommendations"] = await self._generate_improvement_recommendations(comparison)
            
            return comparison
            
        except Exception as e:
            logger.error(f"比较评估结果失败: {e}")
            return {}
    
    async def set_benchmark(
        self,
        benchmark_name: str,
        benchmark_scores: Dict[EvaluationMetric, float]
    ) -> bool:
        """设置基准分数"""
        try:
            self.benchmarks[benchmark_name] = benchmark_scores
            
            # 存储到Redis
            await self.redis.setex(
                f"benchmark:{benchmark_name}",
                86400 * 30,  # 保存30天
                json.dumps({
                    metric.value: score for metric, score in benchmark_scores.items()
                })
            )
            
            logger.info(f"设置基准: {benchmark_name}")
            return True
            
        except Exception as e:
            logger.error(f"设置基准失败: {e}")
            return False
    
    async def get_benchmark_comparison(
        self,
        eval_id: str,
        benchmark_name: str
    ) -> Dict[str, Any]:
        """与基准进行比较"""
        try:
            system_eval = self.system_evaluations.get(eval_id)
            benchmark = self.benchmarks.get(benchmark_name)
            
            if not system_eval or not benchmark:
                return {}
            
            comparison = {
                "evaluation_id": eval_id,
                "benchmark_name": benchmark_name,
                "metric_comparisons": {},
                "overall_performance": "unknown"
            }
            
            better_count = 0
            total_count = 0
            
            for metric, benchmark_score in benchmark.items():
                if metric in system_eval.results:
                    eval_score = system_eval.results[metric]
                    difference = eval_score - benchmark_score
                    
                    comparison["metric_comparisons"][metric.value] = {
                        "evaluation_score": eval_score,
                        "benchmark_score": benchmark_score,
                        "difference": difference,
                        "percentage_difference": (difference / benchmark_score) * 100 if benchmark_score != 0 else 0,
                        "status": "better" if difference > 0 else "worse" if difference < 0 else "equal"
                    }
                    
                    if difference > 0:
                        better_count += 1
                    total_count += 1
            
            # 整体性能评估
            if total_count > 0:
                if better_count / total_count >= 0.7:
                    comparison["overall_performance"] = "excellent"
                elif better_count / total_count >= 0.5:
                    comparison["overall_performance"] = "good"
                elif better_count / total_count >= 0.3:
                    comparison["overall_performance"] = "fair"
                else:
                    comparison["overall_performance"] = "poor"
            
            return comparison
            
        except Exception as e:
            logger.error(f"基准比较失败: {e}")
            return {}
    
    async def _execute_rag_query(
        self,
        rag_system: Any,
        case: EvaluationCase
    ) -> Dict[str, Any]:
        """执行RAG查询"""
        try:
            # 这里需要根据实际的RAG系统接口进行调用
            # 假设RAG系统有一个query方法
            start_time = datetime.now()
            
            # 模拟RAG系统调用
            response = await rag_system.query(
                query=case.query,
                user_context=case.user_context
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "query": case.query,
                "response": response.get("answer", ""),
                "retrieved_documents": response.get("documents", []),
                "retrieval_scores": response.get("scores", []),
                "response_time": response_time,
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"执行RAG查询失败: {e}")
            return {}
    
    async def _evaluate_metric(
        self,
        case: EvaluationCase,
        rag_response: Dict[str, Any],
        metric: EvaluationMetric
    ) -> Optional[EvaluationResult]:
        """评估单个指标"""
        try:
            result_id = f"result_{datetime.now().timestamp()}"
            
            # 根据指标类型选择评估器
            if metric.value.startswith("retrieval_"):
                evaluator = self.evaluators["retrieval"]
            elif metric.value.startswith("generation_"):
                evaluator = self.evaluators["generation"]
            elif metric.value in ["user_satisfaction", "response_time", "engagement_rate", "task_success_rate"]:
                evaluator = self.evaluators["user_experience"]
            else:
                evaluator = self.evaluators["system_performance"]
            
            # 执行评估
            score, details = await evaluator.evaluate(metric, case, rag_response)
            
            return EvaluationResult(
                id=result_id,
                case_id=case.id,
                metric=metric,
                score=score,
                details=details,
                method=EvaluationMethod.AUTOMATIC,
                evaluator=evaluator.__class__.__name__,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"评估指标失败 {metric.value}: {e}")
            return None
    
    async def _aggregate_results(
        self,
        all_results: Dict[str, Dict[EvaluationMetric, EvaluationResult]],
        metrics: List[EvaluationMetric]
    ) -> Dict[EvaluationMetric, float]:
        """聚合评估结果"""
        try:
            aggregated = {}
            
            for metric in metrics:
                scores = []
                for case_results in all_results.values():
                    if metric in case_results:
                        scores.append(case_results[metric].score)
                
                if scores:
                    aggregated[metric] = statistics.mean(scores)
            
            return aggregated
            
        except Exception as e:
            logger.error(f"聚合结果失败: {e}")
            return {}
    
    async def _generate_evaluation_summary(
        self,
        all_results: Dict[str, Dict[EvaluationMetric, EvaluationResult]]
    ) -> Dict[str, Any]:
        """生成评估摘要"""
        try:
            summary = {
                "total_cases": len(all_results),
                "successful_cases": 0,
                "failed_cases": 0,
                "metric_statistics": {},
                "performance_insights": []
            }
            
            # 统计成功和失败的用例
            for case_results in all_results.values():
                if case_results:
                    summary["successful_cases"] += 1
                else:
                    summary["failed_cases"] += 1
            
            # 计算指标统计
            metric_scores = defaultdict(list)
            for case_results in all_results.values():
                for metric, result in case_results.items():
                    metric_scores[metric].append(result.score)
            
            for metric, scores in metric_scores.items():
                if scores:
                    summary["metric_statistics"][metric.value] = {
                        "mean": statistics.mean(scores),
                        "median": statistics.median(scores),
                        "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                        "min": min(scores),
                        "max": max(scores),
                        "count": len(scores)
                    }
            
            # 生成性能洞察
            summary["performance_insights"] = await self._generate_performance_insights(metric_scores)
            
            return summary
            
        except Exception as e:
            logger.error(f"生成评估摘要失败: {e}")
            return {}
    
    async def _generate_performance_insights(
        self,
        metric_scores: Dict[EvaluationMetric, List[float]]
    ) -> List[str]:
        """生成性能洞察"""
        try:
            insights = []
            
            for metric, scores in metric_scores.items():
                if not scores:
                    continue
                
                mean_score = statistics.mean(scores)
                
                if mean_score >= 0.8:
                    insights.append(f"{metric.value}表现优秀，平均分数{mean_score:.3f}")
                elif mean_score >= 0.6:
                    insights.append(f"{metric.value}表现良好，平均分数{mean_score:.3f}")
                elif mean_score >= 0.4:
                    insights.append(f"{metric.value}表现一般，平均分数{mean_score:.3f}，需要改进")
                else:
                    insights.append(f"{metric.value}表现较差，平均分数{mean_score:.3f}，急需优化")
                
                # 检查分数分布
                if len(scores) > 1:
                    std_dev = statistics.stdev(scores)
                    if std_dev > 0.2:
                        insights.append(f"{metric.value}分数波动较大，标准差{std_dev:.3f}，需要提高稳定性")
            
            return insights
            
        except Exception as e:
            logger.error(f"生成性能洞察失败: {e}")
            return []
    
    async def _generate_improvement_recommendations(
        self,
        comparison: Dict[str, Any]
    ) -> List[str]:
        """生成改进建议"""
        try:
            recommendations = []
            
            # 分析改进情况
            improvement_analysis = comparison.get("improvement_analysis", {})
            
            declining_metrics = []
            stable_metrics = []
            
            for metric, analysis in improvement_analysis.items():
                if analysis["status"] == "declined":
                    declining_metrics.append(metric)
                elif analysis["status"] == "stable":
                    stable_metrics.append(metric)
            
            # 针对下降的指标给出建议
            if declining_metrics:
                recommendations.append(f"以下指标出现下降，需要重点关注：{', '.join(declining_metrics)}")
                
                if "retrieval_precision" in declining_metrics:
                    recommendations.append("检索精度下降，建议优化检索算法或更新知识库")
                
                if "generation_relevance" in declining_metrics:
                    recommendations.append("生成相关性下降，建议调整生成模型参数或提示词")
                
                if "response_time" in declining_metrics:
                    recommendations.append("响应时间增加，建议优化系统性能或增加缓存")
            
            # 针对稳定的指标给出建议
            if stable_metrics:
                recommendations.append(f"以下指标保持稳定，可考虑进一步优化：{', '.join(stable_metrics)}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成改进建议失败: {e}")
            return []
    
    async def _continuous_evaluation_task(
        self,
        eval_id: str,
        rag_system: Any,
        duration_hours: int,
        sample_rate: float
    ):
        """持续评估任务"""
        try:
            end_time = datetime.now() + timedelta(hours=duration_hours)
            
            while datetime.now() < end_time:
                # 随机选择评估用例
                if self.evaluation_cases and np.random.random() < sample_rate:
                    case_id = np.random.choice(list(self.evaluation_cases.keys()))
                    await self.run_single_evaluation(case_id, rag_system)
                
                # 等待一段时间
                await asyncio.sleep(60)  # 每分钟检查一次
            
            # 更新评估状态
            system_eval = self.system_evaluations[eval_id]
            system_eval.end_time = datetime.now()
            system_eval.status = "completed"
            
            logger.info(f"持续评估完成: {eval_id}")
            
        except Exception as e:
            logger.error(f"持续评估任务失败: {e}")
    
    async def _store_evaluation_case(self, case: EvaluationCase):
        """存储评估用例"""
        try:
            case_data = asdict(case)
            case_data["created_at"] = case.created_at.isoformat()
            
            await self.redis.setex(
                f"eval_case:{case.id}",
                86400 * 30,  # 保存30天
                json.dumps(case_data)
            )
            
        except Exception as e:
            logger.error(f"存储评估用例失败: {e}")
    
    async def _store_system_evaluation(self, system_eval: SystemEvaluation):
        """存储系统评估"""
        try:
            eval_data = asdict(system_eval)
            eval_data["start_time"] = system_eval.start_time.isoformat()
            if system_eval.end_time:
                eval_data["end_time"] = system_eval.end_time.isoformat()
            
            # 转换枚举类型
            eval_data["results"] = {
                metric.value: score for metric, score in system_eval.results.items()
            }
            
            await self.redis.setex(
                f"system_eval:{system_eval.id}",
                86400 * 30,  # 保存30天
                json.dumps(eval_data)
            )
            
        except Exception as e:
            logger.error(f"存储系统评估失败: {e}")

class RetrievalEvaluator:
    """检索评估器"""
    
    async def evaluate(
        self,
        metric: EvaluationMetric,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估检索指标"""
        try:
            retrieved_docs = rag_response.get("retrieved_documents", [])
            expected_docs = case.expected_documents
            
            if metric == EvaluationMetric.RETRIEVAL_PRECISION:
                return await self._calculate_precision(retrieved_docs, expected_docs)
            
            elif metric == EvaluationMetric.RETRIEVAL_RECALL:
                return await self._calculate_recall(retrieved_docs, expected_docs)
            
            elif metric == EvaluationMetric.RETRIEVAL_F1:
                return await self._calculate_f1(retrieved_docs, expected_docs)
            
            elif metric == EvaluationMetric.RETRIEVAL_NDCG:
                return await self._calculate_ndcg(retrieved_docs, expected_docs, rag_response.get("retrieval_scores", []))
            
            elif metric == EvaluationMetric.RETRIEVAL_MRR:
                return await self._calculate_mrr(retrieved_docs, expected_docs)
            
            return 0.0, {}
            
        except Exception as e:
            logger.error(f"检索评估失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_precision(
        self,
        retrieved_docs: List[str],
        expected_docs: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算精确率"""
        if not retrieved_docs:
            return 0.0, {"retrieved_count": 0, "relevant_count": 0}
        
        relevant_count = len(set(retrieved_docs) & set(expected_docs))
        precision = relevant_count / len(retrieved_docs)
        
        return precision, {
            "retrieved_count": len(retrieved_docs),
            "relevant_count": relevant_count,
            "precision": precision
        }
    
    async def _calculate_recall(
        self,
        retrieved_docs: List[str],
        expected_docs: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算召回率"""
        if not expected_docs:
            return 1.0, {"expected_count": 0, "found_count": 0}
        
        found_count = len(set(retrieved_docs) & set(expected_docs))
        recall = found_count / len(expected_docs)
        
        return recall, {
            "expected_count": len(expected_docs),
            "found_count": found_count,
            "recall": recall
        }
    
    async def _calculate_f1(
        self,
        retrieved_docs: List[str],
        expected_docs: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算F1分数"""
        precision, precision_details = await self._calculate_precision(retrieved_docs, expected_docs)
        recall, recall_details = await self._calculate_recall(retrieved_docs, expected_docs)
        
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        return f1, {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "precision_details": precision_details,
            "recall_details": recall_details
        }
    
    async def _calculate_ndcg(
        self,
        retrieved_docs: List[str],
        expected_docs: List[str],
        scores: List[float]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算NDCG"""
        if not retrieved_docs or not expected_docs:
            return 0.0, {"ndcg": 0.0}
        
        # 创建相关性标签
        relevance_labels = []
        for doc in retrieved_docs:
            if doc in expected_docs:
                relevance_labels.append(1)
            else:
                relevance_labels.append(0)
        
        # 如果没有分数，使用位置倒数作为分数
        if not scores:
            scores = [1.0 / (i + 1) for i in range(len(retrieved_docs))]
        
        # 计算NDCG
        try:
            ndcg = ndcg_score([relevance_labels], [scores[:len(relevance_labels)]])
        except:
            ndcg = 0.0
        
        return ndcg, {
            "ndcg": ndcg,
            "relevance_labels": relevance_labels,
            "scores": scores[:len(relevance_labels)]
        }
    
    async def _calculate_mrr(
        self,
        retrieved_docs: List[str],
        expected_docs: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算平均倒数排名"""
        if not retrieved_docs or not expected_docs:
            return 0.0, {"mrr": 0.0, "first_relevant_rank": None}
        
        # 找到第一个相关文档的位置
        first_relevant_rank = None
        for i, doc in enumerate(retrieved_docs):
            if doc in expected_docs:
                first_relevant_rank = i + 1  # 排名从1开始
                break
        
        if first_relevant_rank is None:
            mrr = 0.0
        else:
            mrr = 1.0 / first_relevant_rank
        
        return mrr, {
            "mrr": mrr,
            "first_relevant_rank": first_relevant_rank
        }

class GenerationEvaluator:
    """生成评估器"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    async def evaluate(
        self,
        metric: EvaluationMetric,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估生成指标"""
        try:
            generated_response = rag_response.get("response", "")
            expected_response = case.expected_response
            
            if metric == EvaluationMetric.GENERATION_RELEVANCE:
                return await self._calculate_relevance(generated_response, expected_response)
            
            elif metric == EvaluationMetric.GENERATION_ACCURACY:
                return await self._calculate_accuracy(generated_response, case.ground_truth)
            
            elif metric == EvaluationMetric.GENERATION_COMPLETENESS:
                return await self._calculate_completeness(generated_response, expected_response)
            
            elif metric == EvaluationMetric.GENERATION_COHERENCE:
                return await self._calculate_coherence(generated_response)
            
            elif metric == EvaluationMetric.GENERATION_SAFETY:
                return await self._calculate_safety(generated_response)
            
            return 0.0, {}
            
        except Exception as e:
            logger.error(f"生成评估失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_relevance(
        self,
        generated_response: str,
        expected_response: str
    ) -> Tuple[float, Dict[str, Any]]:
        """计算相关性"""
        try:
            if not generated_response or not expected_response:
                return 0.0, {"similarity": 0.0}
            
            # 使用TF-IDF计算相似度
            texts = [generated_response, expected_response]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity, {
                "similarity": similarity,
                "method": "tfidf_cosine"
            }
            
        except Exception as e:
            logger.error(f"计算相关性失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_accuracy(
        self,
        generated_response: str,
        ground_truth: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """计算准确性"""
        try:
            # 简化的准确性评估
            # 实际应用中可能需要更复杂的事实检查
            
            accuracy_score = 0.0
            details = {"checks": []}
            
            # 检查关键事实
            key_facts = ground_truth.get("key_facts", [])
            if key_facts:
                correct_facts = 0
                for fact in key_facts:
                    if fact.lower() in generated_response.lower():
                        correct_facts += 1
                        details["checks"].append({"fact": fact, "found": True})
                    else:
                        details["checks"].append({"fact": fact, "found": False})
                
                accuracy_score = correct_facts / len(key_facts)
            
            return accuracy_score, details
            
        except Exception as e:
            logger.error(f"计算准确性失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_completeness(
        self,
        generated_response: str,
        expected_response: str
    ) -> Tuple[float, Dict[str, Any]]:
        """计算完整性"""
        try:
            if not expected_response:
                return 1.0, {"completeness": 1.0}
            
            # 基于长度和关键词覆盖率的简单完整性评估
            expected_words = set(expected_response.lower().split())
            generated_words = set(generated_response.lower().split())
            
            if not expected_words:
                return 1.0, {"completeness": 1.0}
            
            coverage = len(expected_words & generated_words) / len(expected_words)
            
            # 考虑长度因素
            length_ratio = min(1.0, len(generated_response) / len(expected_response))
            
            completeness = (coverage + length_ratio) / 2
            
            return completeness, {
                "completeness": completeness,
                "word_coverage": coverage,
                "length_ratio": length_ratio
            }
            
        except Exception as e:
            logger.error(f"计算完整性失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_coherence(self, generated_response: str) -> Tuple[float, Dict[str, Any]]:
        """计算连贯性"""
        try:
            if not generated_response:
                return 0.0, {"coherence": 0.0}
            
            # 简化的连贯性评估
            sentences = generated_response.split('。')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 1:
                return 1.0, {"coherence": 1.0, "sentence_count": len(sentences)}
            
            # 检查句子之间的连接词
            coherence_indicators = ['因此', '所以', '但是', '然而', '另外', '此外', '首先', '其次', '最后']
            coherence_count = 0
            
            for sentence in sentences:
                if any(indicator in sentence for indicator in coherence_indicators):
                    coherence_count += 1
            
            coherence_score = min(1.0, coherence_count / max(1, len(sentences) - 1))
            
            return coherence_score, {
                "coherence": coherence_score,
                "sentence_count": len(sentences),
                "coherence_indicators": coherence_count
            }
            
        except Exception as e:
            logger.error(f"计算连贯性失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_safety(self, generated_response: str) -> Tuple[float, Dict[str, Any]]:
        """计算安全性"""
        try:
            if not generated_response:
                return 1.0, {"safety": 1.0}
            
            # 检查不安全内容
            unsafe_patterns = [
                '自杀', '伤害自己', '服毒', '过量用药',
                '不要看医生', '拒绝治疗', '停止用药'
            ]
            
            safety_violations = []
            for pattern in unsafe_patterns:
                if pattern in generated_response:
                    safety_violations.append(pattern)
            
            # 安全性分数：没有违规为1.0，有违规则根据严重程度降低
            if not safety_violations:
                safety_score = 1.0
            else:
                safety_score = max(0.0, 1.0 - len(safety_violations) * 0.3)
            
            return safety_score, {
                "safety": safety_score,
                "violations": safety_violations,
                "violation_count": len(safety_violations)
            }
            
        except Exception as e:
            logger.error(f"计算安全性失败: {e}")
            return 0.0, {"error": str(e)}

class UserExperienceEvaluator:
    """用户体验评估器"""
    
    async def evaluate(
        self,
        metric: EvaluationMetric,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估用户体验指标"""
        try:
            if metric == EvaluationMetric.RESPONSE_TIME:
                return await self._evaluate_response_time(rag_response)
            
            elif metric == EvaluationMetric.USER_SATISFACTION:
                return await self._evaluate_user_satisfaction(case, rag_response)
            
            elif metric == EvaluationMetric.ENGAGEMENT_RATE:
                return await self._evaluate_engagement_rate(rag_response)
            
            elif metric == EvaluationMetric.TASK_SUCCESS_RATE:
                return await self._evaluate_task_success_rate(case, rag_response)
            
            return 0.0, {}
            
        except Exception as e:
            logger.error(f"用户体验评估失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _evaluate_response_time(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估响应时间"""
        response_time = rag_response.get("response_time", 0)
        
        # 响应时间评分：2秒内为满分，超过10秒为0分
        if response_time <= 2.0:
            score = 1.0
        elif response_time >= 10.0:
            score = 0.0
        else:
            score = 1.0 - (response_time - 2.0) / 8.0
        
        return score, {
            "response_time": response_time,
            "score": score,
            "threshold_2s": response_time <= 2.0,
            "threshold_5s": response_time <= 5.0
        }
    
    async def _evaluate_user_satisfaction(
        self,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估用户满意度"""
        # 基于多个因素的综合评估
        factors = {}
        
        # 响应长度适中性
        response_length = len(rag_response.get("response", ""))
        if 50 <= response_length <= 500:
            factors["length_appropriateness"] = 1.0
        elif response_length < 50:
            factors["length_appropriateness"] = response_length / 50.0
        else:
            factors["length_appropriateness"] = max(0.5, 1.0 - (response_length - 500) / 1000.0)
        
        # 响应时间
        response_time = rag_response.get("response_time", 0)
        if response_time <= 3.0:
            factors["response_time"] = 1.0
        else:
            factors["response_time"] = max(0.0, 1.0 - (response_time - 3.0) / 7.0)
        
        # 内容相关性（简化评估）
        query = case.query
        response = rag_response.get("response", "")
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        if query_words:
            relevance = len(query_words & response_words) / len(query_words)
            factors["content_relevance"] = relevance
        else:
            factors["content_relevance"] = 0.0
        
        # 综合评分
        satisfaction_score = sum(factors.values()) / len(factors)
        
        return satisfaction_score, {
            "satisfaction_score": satisfaction_score,
            "factors": factors
        }
    
    async def _evaluate_engagement_rate(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估参与度"""
        # 基于响应的吸引力评估
        response = rag_response.get("response", "")
        
        engagement_factors = {}
        
        # 问题引导
        question_count = response.count('?') + response.count('？')
        engagement_factors["questions"] = min(1.0, question_count / 2.0)
        
        # 互动元素
        interactive_words = ['建议', '推荐', '可以尝试', '您可以', '不妨']
        interactive_count = sum(1 for word in interactive_words if word in response)
        engagement_factors["interactivity"] = min(1.0, interactive_count / 3.0)
        
        # 个性化程度
        personal_words = ['您的', '您', '根据您的情况']
        personal_count = sum(1 for word in personal_words if word in response)
        engagement_factors["personalization"] = min(1.0, personal_count / 2.0)
        
        engagement_score = sum(engagement_factors.values()) / len(engagement_factors)
        
        return engagement_score, {
            "engagement_score": engagement_score,
            "factors": engagement_factors
        }
    
    async def _evaluate_task_success_rate(
        self,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估任务成功率"""
        # 基于查询意图和响应匹配度
        query = case.query.lower()
        response = rag_response.get("response", "").lower()
        
        success_indicators = {}
        
        # 信息查询成功
        if any(word in query for word in ['什么', '如何', '怎么', '为什么']):
            if len(response) > 50 and any(word in response for word in ['是', '可以', '建议', '因为']):
                success_indicators["information_provided"] = 1.0
            else:
                success_indicators["information_provided"] = 0.0
        
        # 建议请求成功
        if any(word in query for word in ['建议', '推荐', '应该']):
            if any(word in response for word in ['建议', '推荐', '可以', '应该']):
                success_indicators["advice_provided"] = 1.0
            else:
                success_indicators["advice_provided"] = 0.0
        
        # 问题解答成功
        if '?' in query or '？' in query:
            if len(response) > 30:
                success_indicators["question_answered"] = 1.0
            else:
                success_indicators["question_answered"] = 0.0
        
        # 如果没有特定指标，使用通用成功评估
        if not success_indicators:
            if len(response) > 20:
                success_indicators["general_response"] = 1.0
            else:
                success_indicators["general_response"] = 0.0
        
        success_rate = sum(success_indicators.values()) / len(success_indicators)
        
        return success_rate, {
            "success_rate": success_rate,
            "indicators": success_indicators
        }

class SystemPerformanceEvaluator:
    """系统性能评估器"""
    
    async def evaluate(
        self,
        metric: EvaluationMetric,
        case: EvaluationCase,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估系统性能指标"""
        try:
            if metric == EvaluationMetric.THROUGHPUT:
                return await self._evaluate_throughput(rag_response)
            
            elif metric == EvaluationMetric.LATENCY_P95:
                return await self._evaluate_latency_p95(rag_response)
            
            elif metric == EvaluationMetric.ERROR_RATE:
                return await self._evaluate_error_rate(rag_response)
            
            elif metric == EvaluationMetric.AVAILABILITY:
                return await self._evaluate_availability(rag_response)
            
            return 0.0, {}
            
        except Exception as e:
            logger.error(f"系统性能评估失败: {e}")
            return 0.0, {"error": str(e)}
    
    async def _evaluate_throughput(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估吞吐量"""
        # 简化的吞吐量评估
        response_time = rag_response.get("response_time", 1.0)
        
        # 假设目标是每秒处理1个请求
        throughput = 1.0 / response_time if response_time > 0 else 0.0
        
        # 归一化分数：1 QPS为满分
        score = min(1.0, throughput)
        
        return score, {
            "throughput_qps": throughput,
            "response_time": response_time,
            "score": score
        }
    
    async def _evaluate_latency_p95(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估P95延迟"""
        response_time = rag_response.get("response_time", 0)
        
        # P95延迟目标：5秒内
        if response_time <= 5.0:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (response_time - 5.0) / 10.0)
        
        return score, {
            "latency": response_time,
            "p95_target": 5.0,
            "score": score
        }
    
    async def _evaluate_error_rate(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估错误率"""
        # 检查是否有错误
        has_error = "error" in rag_response or not rag_response.get("response")
        
        error_rate = 1.0 if has_error else 0.0
        score = 1.0 - error_rate
        
        return score, {
            "error_rate": error_rate,
            "has_error": has_error,
            "score": score
        }
    
    async def _evaluate_availability(
        self,
        rag_response: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """评估可用性"""
        # 简化的可用性评估：能够返回响应即认为可用
        is_available = bool(rag_response.get("response"))
        
        availability = 1.0 if is_available else 0.0
        
        return availability, {
            "availability": availability,
            "is_available": is_available
        } 