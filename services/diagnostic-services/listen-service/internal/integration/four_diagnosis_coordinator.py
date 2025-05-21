#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
四诊合参协调器

负责与其他诊断服务(望诊、问诊、切诊)协调，实现中医四诊合参。
"""
import os
import sys
import time
import logging
import json
import yaml
import re
import grpc
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from internal.model.diagnosis_model import ListenDiagnosisResult
from pkg.utils.config_loader import get_config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConnectionInfo:
    """服务连接信息"""
    host: str
    port: int
    timeout: int
    retry_count: int
    retry_interval: int
    auth_token: Optional[str] = None
    use_ssl: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None

@dataclass
class DiagnosisContext:
    """诊断上下文，包含各诊断方法的结果"""
    user_id: str
    session_id: str
    timestamp: int
    listen_result: Optional[Dict[str, Any]] = None  # 闻诊结果
    look_result: Optional[Dict[str, Any]] = None    # 望诊结果
    inquiry_result: Optional[Dict[str, Any]] = None # 问诊结果
    palpation_result: Optional[Dict[str, Any]] = None # 切诊结果
    combined_result: Optional[Dict[str, Any]] = None  # 合参结果

class FourDiagnosisCoordinator:
    """四诊合参协调器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化协调器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config = self._load_config(config_path)
        self.enabled = self.config.get("four_diagnosis_coordination.enabled", False)
        
        if not self.enabled:
            logger.info("四诊合参功能未启用")
            return
        
        # 加载协同规则
        self.rules = self._load_coordination_rules()
        
        # 服务连接信息
        self.service_connections = {
            "inquiry": self._create_service_connection("inquiry_service"),
            "look": self._create_service_connection("look_service"),
            "palpation": self._create_service_connection("palpation_service"),
            "xiaoai": self._create_service_connection("xiaoai_service"),
        }
        
        # 诊断上下文缓存
        self.diagnosis_contexts = {}
        self.context_lock = threading.RLock()
        
        logger.info("四诊合参协调器初始化完成")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置"""
        if config_path is None:
            config_path = os.path.join(project_root, "config/integration.yaml")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 转换为扁平结构以便使用get方法
            flat_config = {}
            self._flatten_dict(config, flat_config)
            return flat_config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def _flatten_dict(self, d: Dict[str, Any], result: Dict[str, Any], prefix: str = ""):
        """将嵌套字典转换为扁平结构"""
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                self._flatten_dict(v, result, key)
            else:
                result[key] = v
    
    def _create_service_connection(self, service_key: str) -> ServiceConnectionInfo:
        """创建服务连接信息"""
        return ServiceConnectionInfo(
            host=self.config.get(f"{service_key}.host", "localhost"),
            port=self.config.get(f"{service_key}.port", 50000),
            timeout=self.config.get(f"{service_key}.timeout", 10),
            retry_count=self.config.get(f"{service_key}.retry_count", 3),
            retry_interval=self.config.get(f"{service_key}.retry_interval", 1),
            auth_token=self.config.get(f"{service_key}.auth.token", None),
            use_ssl=self.config.get(f"{service_key}.ssl.enabled", False),
            cert_file=self.config.get(f"{service_key}.ssl.cert_file", None),
            key_file=self.config.get(f"{service_key}.ssl.key_file", None)
        )
    
    def _load_coordination_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载协同规则"""
        rules = {}
        
        # 获取所有规则类型
        rule_types = []
        for key in self.config:
            match = re.match(r"four_diagnosis_coordination\.coordination_rules\.(\w+)", key)
            if match:
                rule_type = match.group(1)
                if rule_type not in rule_types:
                    rule_types.append(rule_type)
        
        # 加载每种类型的规则
        for rule_type in rule_types:
            rule_key = f"four_diagnosis_coordination.coordination_rules.{rule_type}"
            rules_list = []
            
            # 找出此类型的所有规则
            i = 0
            while True:
                condition_key = f"{rule_key}.{i}.condition"
                action_key = f"{rule_key}.{i}.action"
                description_key = f"{rule_key}.{i}.description"
                
                if condition_key not in self.config:
                    break
                
                rules_list.append({
                    "condition": self.config.get(condition_key),
                    "action": self.config.get(action_key),
                    "description": self.config.get(description_key, ""),
                })
                
                i += 1
            
            if rules_list:
                rules[rule_type] = rules_list
        
        return rules
    
    def create_grpc_channel(self, service_key: str) -> grpc.Channel:
        """
        创建gRPC通道
        
        Args:
            service_key: 服务键名(inquiry, look, palpation, xiaoai)
        
        Returns:
            gRPC通道
        """
        conn_info = self.service_connections.get(service_key)
        if not conn_info:
            raise ValueError(f"未找到服务配置: {service_key}")
        
        # 创建认证凭据
        credentials = None
        if conn_info.auth_token:
            auth_interceptor = self._create_auth_interceptor(conn_info.auth_token)
            credentials = grpc.composite_channel_credentials(
                grpc.local_channel_credentials(),
                grpc.metadata_call_credentials(auth_interceptor)
            )
        
        # 创建通道
        target = f"{conn_info.host}:{conn_info.port}"
        if conn_info.use_ssl:
            if credentials:
                channel = grpc.secure_channel(target, credentials)
            else:
                channel = grpc.secure_channel(target, grpc.local_channel_credentials())
        else:
            if credentials:
                channel = grpc.intercept_channel(
                    grpc.insecure_channel(target),
                    auth_interceptor
                )
            else:
                channel = grpc.insecure_channel(target)
        
        return channel
    
    def _create_auth_interceptor(self, token: str) -> Callable:
        """创建认证拦截器"""
        def auth_interceptor(context, callback):
            metadata = (('authorization', f'Bearer {token}'),)
            callback(metadata, None)
        return auth_interceptor
    
    def register_listen_result(self, user_id: str, session_id: str, 
                              result: ListenDiagnosisResult) -> Dict[str, Any]:
        """
        注册闻诊结果并进行合参
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            result: 闻诊结果
        
        Returns:
            合参结果
        """
        if not self.enabled:
            logger.info("四诊合参功能未启用，仅返回闻诊结果")
            return result.to_dict()
        
        # 序列化闻诊结果
        listen_result = result.to_dict()
        
        with self.context_lock:
            # 获取或创建诊断上下文
            context_key = f"{user_id}:{session_id}"
            if context_key in self.diagnosis_contexts:
                context = self.diagnosis_contexts[context_key]
            else:
                context = DiagnosisContext(
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=int(time.time())
                )
                self.diagnosis_contexts[context_key] = context
            
            # 更新闻诊结果
            context.listen_result = listen_result
            
            # 尝试获取其他诊断结果
            self._fetch_other_diagnosis_results(context)
            
            # 执行四诊合参
            combined_result = self._perform_coordination(context)
            
            # 更新合参结果
            context.combined_result = combined_result
            
            return combined_result
    
    def _fetch_other_diagnosis_results(self, context: DiagnosisContext):
        """
        获取其他诊断结果
        
        Args:
            context: 诊断上下文
        """
        # 异步获取各诊断结果
        threads = []
        
        if not context.inquiry_result:
            inquiry_thread = threading.Thread(
                target=self._fetch_inquiry_result,
                args=(context,)
            )
            threads.append(inquiry_thread)
        
        if not context.look_result:
            look_thread = threading.Thread(
                target=self._fetch_look_result,
                args=(context,)
            )
            threads.append(look_thread)
        
        if not context.palpation_result:
            palpation_thread = threading.Thread(
                target=self._fetch_palpation_result,
                args=(context,)
            )
            threads.append(palpation_thread)
        
        # 启动线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成，最多等待5秒
        for thread in threads:
            thread.join(timeout=5)
    
    def _fetch_inquiry_result(self, context: DiagnosisContext):
        """获取问诊结果"""
        try:
            # 这里应使用问诊服务的gRPC客户端获取结果
            # 简化实现，实际项目中应使用问诊服务的客户端
            pass
        except Exception as e:
            logger.error(f"获取问诊结果失败: {str(e)}")
    
    def _fetch_look_result(self, context: DiagnosisContext):
        """获取望诊结果"""
        try:
            # 这里应使用望诊服务的gRPC客户端获取结果
            # 简化实现，实际项目中应使用望诊服务的客户端
            pass
        except Exception as e:
            logger.error(f"获取望诊结果失败: {str(e)}")
    
    def _fetch_palpation_result(self, context: DiagnosisContext):
        """获取切诊结果"""
        try:
            # 这里应使用切诊服务的gRPC客户端获取结果
            # 简化实现，实际项目中应使用切诊服务的客户端
            pass
        except Exception as e:
            logger.error(f"获取切诊结果失败: {str(e)}")
    
    def _perform_coordination(self, context: DiagnosisContext) -> Dict[str, Any]:
        """
        执行四诊合参
        
        Args:
            context: 诊断上下文
        
        Returns:
            合参结果
        """
        # 如果只有闻诊结果，直接返回
        if not any([context.inquiry_result, context.look_result, context.palpation_result]):
            logger.info("仅有闻诊结果，无法进行四诊合参")
            return context.listen_result
        
        # 构建合参基础结果
        combined_result = {
            "diagnosis_id": f"combined_{context.session_id}_{context.timestamp}",
            "user_id": context.user_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp,
            "available_diagnosis": {
                "listen": context.listen_result is not None,
                "inquiry": context.inquiry_result is not None,
                "look": context.look_result is not None,
                "palpation": context.palpation_result is not None
            },
            "tcm_patterns": self._combine_tcm_patterns(context),
            "constitution_relevance": self._combine_constitution_relevance(context),
            "diagnostic_features": self._combine_diagnostic_features(context),
            "confidence": self._calculate_combined_confidence(context),
            "analysis_summary": self._generate_analysis_summary(context),
            "source": "four_diagnosis_coordination"
        }
        
        # 应用协同规则
        self._apply_coordination_rules(context, combined_result)
        
        return combined_result
    
    def _combine_tcm_patterns(self, context: DiagnosisContext) -> Dict[str, float]:
        """
        合并中医证型评分
        
        Args:
            context: 诊断上下文
        
        Returns:
            合并的证型评分
        """
        combined_patterns = {}
        
        # 获取权重
        weights = {
            "listen": float(self.config.get("four_diagnosis_coordination.weights.listen", 0.25)),
            "inquiry": float(self.config.get("four_diagnosis_coordination.weights.inquiry", 0.3)),
            "look": float(self.config.get("four_diagnosis_coordination.weights.look", 0.25)),
            "palpation": float(self.config.get("four_diagnosis_coordination.weights.palpation", 0.2))
        }
        
        # 收集所有证型
        all_patterns = set()
        if context.listen_result and "tcm_patterns" in context.listen_result:
            all_patterns.update(context.listen_result["tcm_patterns"].keys())
        
        if context.inquiry_result and "tcm_patterns" in context.inquiry_result:
            all_patterns.update(context.inquiry_result["tcm_patterns"].keys())
        
        if context.look_result and "tcm_patterns" in context.look_result:
            all_patterns.update(context.look_result["tcm_patterns"].keys())
        
        if context.palpation_result and "tcm_patterns" in context.palpation_result:
            all_patterns.update(context.palpation_result["tcm_patterns"].keys())
        
        # 合并评分
        for pattern in all_patterns:
            score = 0
            effective_weight = 0
            
            if context.listen_result and "tcm_patterns" in context.listen_result:
                if pattern in context.listen_result["tcm_patterns"]:
                    score += context.listen_result["tcm_patterns"][pattern] * weights["listen"]
                    effective_weight += weights["listen"]
            
            if context.inquiry_result and "tcm_patterns" in context.inquiry_result:
                if pattern in context.inquiry_result["tcm_patterns"]:
                    score += context.inquiry_result["tcm_patterns"][pattern] * weights["inquiry"]
                    effective_weight += weights["inquiry"]
            
            if context.look_result and "tcm_patterns" in context.look_result:
                if pattern in context.look_result["tcm_patterns"]:
                    score += context.look_result["tcm_patterns"][pattern] * weights["look"]
                    effective_weight += weights["look"]
            
            if context.palpation_result and "tcm_patterns" in context.palpation_result:
                if pattern in context.palpation_result["tcm_patterns"]:
                    score += context.palpation_result["tcm_patterns"][pattern] * weights["palpation"]
                    effective_weight += weights["palpation"]
            
            if effective_weight > 0:
                combined_patterns[pattern] = score / effective_weight
        
        return combined_patterns
    
    def _combine_constitution_relevance(self, context: DiagnosisContext) -> Dict[str, float]:
        """
        合并体质相关度评分
        
        Args:
            context: 诊断上下文
        
        Returns:
            合并的体质相关度
        """
        combined_constitutions = {}
        
        # 获取权重
        weights = {
            "listen": float(self.config.get("four_diagnosis_coordination.weights.listen", 0.25)),
            "inquiry": float(self.config.get("four_diagnosis_coordination.weights.inquiry", 0.3)),
            "look": float(self.config.get("four_diagnosis_coordination.weights.look", 0.25)),
            "palpation": float(self.config.get("four_diagnosis_coordination.weights.palpation", 0.2))
        }
        
        # 收集所有体质类型
        all_constitutions = set()
        if context.listen_result and "constitution_relevance" in context.listen_result:
            all_constitutions.update(context.listen_result["constitution_relevance"].keys())
        
        if context.inquiry_result and "constitution_relevance" in context.inquiry_result:
            all_constitutions.update(context.inquiry_result["constitution_relevance"].keys())
        
        if context.look_result and "constitution_relevance" in context.look_result:
            all_constitutions.update(context.look_result["constitution_relevance"].keys())
        
        if context.palpation_result and "constitution_relevance" in context.palpation_result:
            all_constitutions.update(context.palpation_result["constitution_relevance"].keys())
        
        # 合并评分
        for constitution in all_constitutions:
            score = 0
            effective_weight = 0
            
            if context.listen_result and "constitution_relevance" in context.listen_result:
                if constitution in context.listen_result["constitution_relevance"]:
                    score += context.listen_result["constitution_relevance"][constitution] * weights["listen"]
                    effective_weight += weights["listen"]
            
            if context.inquiry_result and "constitution_relevance" in context.inquiry_result:
                if constitution in context.inquiry_result["constitution_relevance"]:
                    score += context.inquiry_result["constitution_relevance"][constitution] * weights["inquiry"]
                    effective_weight += weights["inquiry"]
            
            if context.look_result and "constitution_relevance" in context.look_result:
                if constitution in context.look_result["constitution_relevance"]:
                    score += context.look_result["constitution_relevance"][constitution] * weights["look"]
                    effective_weight += weights["look"]
            
            if context.palpation_result and "constitution_relevance" in context.palpation_result:
                if constitution in context.palpation_result["constitution_relevance"]:
                    score += context.palpation_result["constitution_relevance"][constitution] * weights["palpation"]
                    effective_weight += weights["palpation"]
            
            if effective_weight > 0:
                combined_constitutions[constitution] = score / effective_weight
        
        return combined_constitutions
    
    def _combine_diagnostic_features(self, context: DiagnosisContext) -> List[Dict[str, Any]]:
        """
        合并诊断特征
        
        Args:
            context: 诊断上下文
        
        Returns:
            合并的诊断特征列表
        """
        combined_features = []
        
        # 收集各诊断方法的特征
        features_by_category = {}
        
        if context.listen_result and "features" in context.listen_result:
            for feature in context.listen_result["features"]:
                category = feature.get("category", "listen")
                if category not in features_by_category:
                    features_by_category[category] = []
                features_by_category[category].append({
                    **feature,
                    "source": "listen"
                })
        
        if context.inquiry_result and "features" in context.inquiry_result:
            for feature in context.inquiry_result["features"]:
                category = feature.get("category", "inquiry")
                if category not in features_by_category:
                    features_by_category[category] = []
                features_by_category[category].append({
                    **feature,
                    "source": "inquiry"
                })
        
        if context.look_result and "features" in context.look_result:
            for feature in context.look_result["features"]:
                category = feature.get("category", "look")
                if category not in features_by_category:
                    features_by_category[category] = []
                features_by_category[category].append({
                    **feature,
                    "source": "look"
                })
        
        if context.palpation_result and "features" in context.palpation_result:
            for feature in context.palpation_result["features"]:
                category = feature.get("category", "palpation")
                if category not in features_by_category:
                    features_by_category[category] = []
                features_by_category[category].append({
                    **feature,
                    "source": "palpation"
                })
        
        # 按类别合并特征
        for category, features in features_by_category.items():
            # 按特征名称分组
            features_by_name = {}
            for feature in features:
                name = feature["feature_name"]
                if name not in features_by_name:
                    features_by_name[name] = []
                features_by_name[name].append(feature)
            
            # 合并每个名称的特征
            for name, name_features in features_by_name.items():
                if len(name_features) == 1:
                    # 只有一个来源，直接使用
                    combined_features.append(name_features[0])
                else:
                    # 多个来源，合并值和置信度
                    sources = [f["source"] for f in name_features]
                    confidences = [f.get("confidence", 0.5) for f in name_features]
                    
                    # 选择置信度最高的值
                    best_idx = confidences.index(max(confidences))
                    
                    combined_features.append({
                        "feature_name": name,
                        "value": name_features[best_idx]["value"],
                        "category": category,
                        "confidence": sum(confidences) / len(confidences),
                        "sources": sources
                    })
        
        return combined_features
    
    def _calculate_combined_confidence(self, context: DiagnosisContext) -> float:
        """
        计算合并后的置信度
        
        Args:
            context: 诊断上下文
        
        Returns:
            合并置信度
        """
        confidences = []
        weights = {
            "listen": float(self.config.get("four_diagnosis_coordination.weights.listen", 0.25)),
            "inquiry": float(self.config.get("four_diagnosis_coordination.weights.inquiry", 0.3)),
            "look": float(self.config.get("four_diagnosis_coordination.weights.look", 0.25)),
            "palpation": float(self.config.get("four_diagnosis_coordination.weights.palpation", 0.2))
        }
        
        total_weight = 0
        
        if context.listen_result:
            listen_confidence = context.listen_result.get("confidence", 0.5)
            confidences.append(listen_confidence * weights["listen"])
            total_weight += weights["listen"]
        
        if context.inquiry_result:
            inquiry_confidence = context.inquiry_result.get("confidence", 0.5)
            confidences.append(inquiry_confidence * weights["inquiry"])
            total_weight += weights["inquiry"]
        
        if context.look_result:
            look_confidence = context.look_result.get("confidence", 0.5)
            confidences.append(look_confidence * weights["look"])
            total_weight += weights["look"]
        
        if context.palpation_result:
            palpation_confidence = context.palpation_result.get("confidence", 0.5)
            confidences.append(palpation_confidence * weights["palpation"])
            total_weight += weights["palpation"]
        
        if total_weight > 0 and confidences:
            return sum(confidences) / total_weight
        
        return 0.5  # 默认置信度
    
    def _generate_analysis_summary(self, context: DiagnosisContext) -> str:
        """
        生成分析总结
        
        Args:
            context: 诊断上下文
        
        Returns:
            分析总结文本
        """
        # 简单拼接各诊断方法的总结
        summaries = []
        
        if context.listen_result and "analysis_summary" in context.listen_result:
            summaries.append(f"【闻诊】{context.listen_result['analysis_summary']}")
        
        if context.inquiry_result and "analysis_summary" in context.inquiry_result:
            summaries.append(f"【问诊】{context.inquiry_result['analysis_summary']}")
        
        if context.look_result and "analysis_summary" in context.look_result:
            summaries.append(f"【望诊】{context.look_result['analysis_summary']}")
        
        if context.palpation_result and "analysis_summary" in context.palpation_result:
            summaries.append(f"【切诊】{context.palpation_result['analysis_summary']}")
        
        if not summaries:
            return "暂无分析总结"
        
        # 生成四诊合参总结
        combined_summary = "。".join(summaries)
        
        # 获取主要证型
        combined_patterns = self._combine_tcm_patterns(context)
        if combined_patterns:
            # 获取评分最高的前3个证型
            top_patterns = sorted(
                combined_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            pattern_str = "、".join([f"{p[0]}({p[1]:.2f})" for p in top_patterns])
            combined_summary += f"。综合四诊所见，主要证型为：{pattern_str}。"
        
        # 获取主要体质
        combined_constitutions = self._combine_constitution_relevance(context)
        if combined_constitutions:
            # 获取评分最高的前2个体质
            top_constitutions = sorted(
                combined_constitutions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
            
            constitution_str = "、".join([f"{c[0]}({c[1]:.2f})" for c in top_constitutions])
            combined_summary += f"体质偏向于{constitution_str}。"
        
        return combined_summary
    
    def _apply_coordination_rules(self, context: DiagnosisContext, result: Dict[str, Any]):
        """
        应用协同规则
        
        Args:
            context: 诊断上下文
            result: 合参结果
        """
        if not self.rules:
            return
        
        # 创建规则运行环境
        env = {
            "listen": context.listen_result or {},
            "inquiry": context.inquiry_result or {},
            "look": context.look_result or {},
            "palpation": context.palpation_result or {},
            "result": result
        }
        
        # 定义规则动作
        def boost_confidence(value):
            """提升置信度"""
            current = result.get("confidence", 0.5)
            new_value = min(current + value, 1.0)
            result["confidence"] = new_value
            return new_value
        
        def suggest_diagnosis(syndrome_name):
            """推荐证型"""
            tcm_patterns = result.get("tcm_patterns", {})
            if syndrome_name in tcm_patterns:
                tcm_patterns[syndrome_name] = min(tcm_patterns[syndrome_name] + 0.2, 1.0)
            else:
                tcm_patterns[syndrome_name] = 0.8
            result["tcm_patterns"] = tcm_patterns
            return tcm_patterns[syndrome_name]
        
        # 添加动作到环境
        env["boost_confidence"] = boost_confidence
        env["suggest_diagnosis"] = suggest_diagnosis
        
        # 执行规则
        applied_rules = []
        
        for rule_type, rules in self.rules.items():
            for rule in rules:
                condition = rule["condition"]
                action = rule["action"]
                description = rule["description"]
                
                try:
                    # 评估条件
                    condition_met = eval(condition, {"__builtins__": {}}, env)
                    
                    if condition_met:
                        # 执行动作
                        eval(action, {"__builtins__": {}}, env)
                        applied_rules.append({
                            "rule_type": rule_type,
                            "condition": condition,
                            "action": action,
                            "description": description
                        })
                except Exception as e:
                    logger.error(f"执行规则失败: {str(e)}, 规则: {condition} -> {action}")
        
        # 添加应用的规则到结果
        if applied_rules:
            result["applied_rules"] = applied_rules

# 单例模式
_coordinator_instance = None

def get_coordinator(config_path: Optional[str] = None) -> FourDiagnosisCoordinator:
    """获取四诊合参协调器单例"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = FourDiagnosisCoordinator(config_path)
    return _coordinator_instance 