#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
产品管理器
负责农产品定制、溯源、支付处理和商品推荐等功能
"""

import logging
import uuid
import json
import time
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector
from internal.repository.product_repository import ProductRepository
from internal.repository.order_repository import OrderRepository
from internal.repository.blockchain_repository import BlockchainRepository
from internal.agent.food_therapy_manager import FoodTherapyManager

logger = logging.getLogger(__name__)

class ProductManager:
    """产品管理器"""
    
    def __init__(self):
        """初始化产品管理器"""
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 加载推荐配置
        self.recommendation_config = self.config.get_section('recommendation.product')
        self.weights = self.recommendation_config.get('weights', {
            'constitution_match': 0.35,
            'season_match': 0.25,
            'user_preference': 0.25,
            'health_condition': 0.15
        })
        
        self.min_confidence = self.recommendation_config.get('min_confidence_threshold', 0.6)
        self.max_recommendations = self.recommendation_config.get('max_recommendations', 10)
        
        # 检查区块链溯源特性是否启用
        self.blockchain_tracing_enabled = self.config.get_section('feature_flags').get('blockchain_tracing', True)
        
        # 初始化存储库
        self.product_repo = ProductRepository()
        self.order_repo = OrderRepository()
        self.blockchain_repo = BlockchainRepository() if self.blockchain_tracing_enabled else None
        
        # 初始化食疗管理器
        self.food_therapy_manager = FoodTherapyManager()
        
        logger.info("产品管理器初始化完成，区块链溯源功能: %s", 
                  "已启用" if self.blockchain_tracing_enabled else "未启用")
    
    async def customize_products(
        self,
        user_id: str,
        constitution_type: str,
        health_conditions: List[str],
        preferences: List[str],
        season: str,
        packaging_preference: str,
        quantity: int,
        need_delivery: bool,
        delivery_address: str
    ) -> Dict[str, Any]:
        """
        定制农产品
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_conditions: 健康状况列表
            preferences: 偏好列表
            season: 季节
            packaging_preference: 包装偏好
            quantity: 数量
            need_delivery: 是否需要配送
            delivery_address: 配送地址
            
        Returns:
            包含定制结果的字典
        """
        try:
            # 记录请求指标
            self.metrics.increment_product_customization_count(constitution_type)
            start_time = time.time()
            
            logger.info(f"为用户 {user_id} ({constitution_type}体质) 定制农产品")
            
            # 为用户体质获取适合的产品
            constitution_products = await self.food_therapy_manager.get_products_for_constitution(
                constitution_type, health_conditions, season
            )
            
            # 获取当季产品
            seasonal_products = await self.product_repo.get_seasonal_products(season)
            
            # 根据用户偏好过滤和排序产品
            customized_products = self._customize_product_selection(
                constitution_products, 
                seasonal_products,
                preferences,
                quantity
            )
            
            # 处理包装请求
            packaged_products = await self._apply_packaging_preferences(
                customized_products,
                packaging_preference
            )
            
            # 计算总价格
            total_price = sum(p['price'] * p['quantity'] for p in packaged_products)
            
            # 估算配送时间
            delivery_estimate = datetime.now() + timedelta(days=3)
            if not need_delivery:
                delivery_estimate = datetime.now() + timedelta(days=1)
            
            # 创建定制ID
            customization_id = str(uuid.uuid4())
            
            # 生成支付链接
            payment_link = f"https://pay.suoke.life/products/{customization_id}"
            
            # 保存定制记录
            await self.order_repo.create_product_customization({
                'id': customization_id,
                'user_id': user_id,
                'constitution_type': constitution_type,
                'health_conditions': health_conditions,
                'preferences': preferences,
                'season': season,
                'packaging_preference': packaging_preference,
                'products': packaged_products,
                'total_price': total_price,
                'need_delivery': need_delivery,
                'delivery_address': delivery_address if need_delivery else '',
                'delivery_estimate': delivery_estimate.isoformat(),
                'status': 'PENDING_PAYMENT',
                'created_at': datetime.now().isoformat()
            })
            
            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_product_customization_time(response_time)
            
            # 构建响应
            return {
                'customization_id': customization_id,
                'products': packaged_products,
                'total_price': total_price,
                'delivery_estimate': delivery_estimate.isoformat(),
                'payment_link': payment_link,
                'metadata': {
                    'constitution_type': constitution_type,
                    'season': season
                }
            }
            
        except Exception as e:
            logger.error(f"产品定制失败: {str(e)}", exc_info=True)
            raise
    
    async def trace_product(
        self,
        product_id: str,
        batch_id: str,
        trace_token: str
    ) -> Dict[str, Any]:
        """
        农产品溯源
        
        Args:
            product_id: 产品ID
            batch_id: 批次ID
            trace_token: 溯源令牌
            
        Returns:
            包含溯源结果的字典
        """
        try:
            # 记录请求指标
            self.metrics.increment_product_trace_count()
            start_time = time.time()
            
            logger.info(f"执行产品溯源: 产品ID={product_id}, 批次ID={batch_id}")
            
            # 获取产品信息
            product = await self.product_repo.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"未找到产品: {product_id}")
            
            # 验证批次
            effective_batch_id = batch_id or product.get('default_batch_id')
            if not effective_batch_id:
                raise ValueError("未提供批次ID，且产品没有默认批次")
            
            # 获取溯源记录
            trace_records = []
            
            # 检查区块链溯源是否启用
            if self.blockchain_tracing_enabled and self.blockchain_repo:
                # 从区块链获取溯源数据
                blockchain_records = await self.blockchain_repo.get_trace_records(
                    product_id, effective_batch_id
                )
                
                # 验证数据完整性
                is_verified = await self.blockchain_repo.verify_trace_chain(
                    blockchain_records, trace_token
                )
                
                # 处理溯源记录
                for record in blockchain_records:
                    trace_records.append({
                        'stage_name': record['stage_name'],
                        'location': record['location'],
                        'timestamp': record['timestamp'],
                        'operator': record['operator'],
                        'details': record['details'],
                        'verification_hash': record['verification_hash']
                    })
                
                # 生成区块链验证URL
                blockchain_url = self.blockchain_repo.get_verification_url(product_id, effective_batch_id)
                
            else:
                # 使用传统数据库溯源
                db_records = await self.product_repo.get_trace_records(product_id, effective_batch_id)
                
                # 处理溯源记录
                for record in db_records:
                    # 生成验证哈希
                    verification_data = f"{record['stage_name']}:{record['timestamp']}:{record['operator']}"
                    verification_hash = hashlib.sha256(verification_data.encode()).hexdigest()
                    
                    trace_records.append({
                        'stage_name': record['stage_name'],
                        'location': record['location'],
                        'timestamp': record['timestamp'],
                        'operator': record['operator'],
                        'details': record['details'],
                        'verification_hash': verification_hash
                    })
                
                # 传统溯源为已验证状态
                is_verified = True
                blockchain_url = ""
            
            # 生成QR码URL
            qr_code_url = f"https://trace.suoke.life/products/{product_id}/batch/{effective_batch_id}"
            
            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_product_trace_time(response_time)
            
            # 构建响应
            return {
                'product_name': product['name'],
                'trace_records': trace_records,
                'blockchain_verification_url': blockchain_url,
                'verified': is_verified,
                'qr_code_url': qr_code_url
            }
            
        except Exception as e:
            logger.error(f"产品溯源失败: {str(e)}", exc_info=True)
            raise
    
    async def process_payment(
        self,
        user_id: str,
        order_id: str,
        payment_method: str,
        amount: float,
        currency: str,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        处理支付请求
        
        Args:
            user_id: 用户ID
            order_id: 订单ID
            payment_method: 支付方式
            amount: 金额
            currency: 货币类型
            metadata: 元数据
            
        Returns:
            包含支付结果的字典
        """
        try:
            # 记录请求指标
            self.metrics.increment_payment_request_count(payment_method)
            start_time = time.time()
            
            logger.info(f"处理支付请求: 用户={user_id}, 订单={order_id}, 金额={amount}{currency}")
            
            # 验证订单
            order = await self.order_repo.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"未找到订单: {order_id}")
            
            # 检查订单用户
            if order['user_id'] != user_id:
                raise ValueError("订单用户不匹配")
            
            # 验证金额
            if abs(order['total_price'] - amount) > 0.01:  # 允许1分钱的舍入误差
                raise ValueError(f"支付金额不匹配: 应为 {order['total_price']}，实际为 {amount}")
            
            # 根据支付方式处理支付
            payment_result = await self._process_payment_by_method(
                user_id, order_id, payment_method, amount, currency, metadata or {}
            )
            
            # 支付成功后更新订单状态
            if payment_result['status'] == 'SUCCESS':
                await self.order_repo.update_order_status(
                    order_id, 'PAID', payment_result['transaction_id']
                )
            
            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_payment_processing_time(response_time)
            
            # 构建响应
            return {
                'payment_id': payment_result['payment_id'],
                'status': payment_result['status'],
                'transaction_id': payment_result['transaction_id'],
                'timestamp': payment_result['timestamp'],
                'payment_url': payment_result['payment_url'],
                'receipt_url': payment_result['receipt_url']
            }
            
        except Exception as e:
            logger.error(f"支付处理失败: {str(e)}", exc_info=True)
            raise
    
    async def recommend_products(
        self,
        user_id: str,
        constitution_type: str,
        season: str,
        health_conditions: List[str],
        preferences: List[str],
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        商品推荐
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            season: 季节
            health_conditions: 健康状况
            preferences: 偏好
            max_results: 最大结果数
            
        Returns:
            包含推荐结果的字典
        """
        try:
            # 记录请求指标
            self.metrics.increment_recommendation_request_count()
            start_time = time.time()
            
            logger.info(f"为用户 {user_id} ({constitution_type}体质) 推荐商品")
            
            # 设置最大结果数
            effective_max = min(max_results, self.max_recommendations)
            
            # 获取季节性产品
            seasonal_products = await self.product_repo.get_seasonal_products(season, effective_max)
            
            # 获取体质匹配产品
            constitution_products = await self.food_therapy_manager.get_products_for_constitution(
                constitution_type, health_conditions or [], season, effective_max
            )
            
            # 获取个性化推荐产品
            personalized_products = await self._get_personalized_recommendations(
                user_id, constitution_type, season, health_conditions or [], preferences or [], effective_max
            )
            
            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_recommendation_time(response_time)
            
            # 生成解释信息
            explanation = {
                'seasonal': f"{season}季节适合食用的优质食材",
                'constitution': f"适合{constitution_type}体质的特色食材",
                'personalized': f"根据您的个人情况和偏好定制的推荐"
            }
            
            # 构建响应
            return {
                'seasonal_products': seasonal_products,
                'constitution_specific_products': constitution_products,
                'personalized_products': personalized_products,
                'recommendation_explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"产品推荐失败: {str(e)}", exc_info=True)
            raise
    
    def _customize_product_selection(self, constitution_products: List[Dict[str, Any]],
                                 seasonal_products: List[Dict[str, Any]],
                                 preferences: List[str],
                                 target_quantity: int) -> List[Dict[str, Any]]:
        """
        根据用户偏好定制产品选择
        
        Args:
            constitution_products: 体质匹配产品
            seasonal_products: 季节性产品
            preferences: 用户偏好
            target_quantity: 目标数量
            
        Returns:
            List[Dict[str, Any]]: 定制产品列表
        """
        # 合并产品列表
        all_products = constitution_products.copy()
        
        # 添加不在constitution_products中的seasonal_products
        constitution_ids = {p['id'] for p in constitution_products}
        for product in seasonal_products:
            if product['id'] not in constitution_ids:
                all_products.append(product)
        
        # 按照用户偏好过滤和排序
        filtered_products = []
        for product in all_products:
            # 计算偏好匹配分数
            preference_score = 0
            for pref in preferences:
                if pref.lower() in product.get('tags', []) or pref.lower() in product.get('categories', []):
                    preference_score += 1
            
            # 添加偏好分数
            product_copy = product.copy()
            product_copy['preference_score'] = preference_score
            filtered_products.append(product_copy)
        
        # 按偏好分数和原有排序分数的组合排序
        filtered_products.sort(key=lambda p: (p.get('preference_score', 0), p.get('score', 0)), reverse=True)
        
        # 取目标数量
        selected_products = filtered_products[:target_quantity]
        
        # 设置默认数量
        for product in selected_products:
            product['quantity'] = 1
        
        return selected_products
    
    async def _apply_packaging_preferences(self, products: List[Dict[str, Any]],
                                      packaging_preference: str) -> List[Dict[str, Any]]:
        """
        应用包装偏好
        
        Args:
            products: 产品列表
            packaging_preference: 包装偏好
            
        Returns:
            List[Dict[str, Any]]: 应用包装偏好后的产品列表
        """
        packaged_products = []
        
        for product in products:
            product_copy = product.copy()
            
            # 根据包装偏好调整价格和描述
            if packaging_preference == "ECO_FRIENDLY":
                product_copy['description'] = f"环保包装 - {product_copy['description']}"
                # 环保包装略贵
                product_copy['price'] = product_copy['price'] * 1.05
                
            elif packaging_preference == "GIFT":
                product_copy['description'] = f"精美礼盒 - {product_copy['description']}"
                # 礼品包装更贵
                product_copy['price'] = product_copy['price'] * 1.15
                
            elif packaging_preference == "MINIMAL":
                product_copy['description'] = f"简易包装 - {product_copy['description']}"
                # 简易包装略便宜
                product_copy['price'] = product_copy['price'] * 0.95
            
            # 四舍五入到分
            product_copy['price'] = round(product_copy['price'] * 100) / 100
            
            packaged_products.append(product_copy)
        
        return packaged_products
    
    async def _process_payment_by_method(self, user_id: str, order_id: str,
                                   payment_method: str, amount: float,
                                   currency: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        根据支付方式处理支付
        
        Args:
            user_id: 用户ID
            order_id: 订单ID
            payment_method: 支付方式
            amount: 金额
            currency: 货币类型
            metadata: 元数据
            
        Returns:
            Dict[str, Any]: 支付结果
        """
        # 生成支付ID
        payment_id = str(uuid.uuid4())
        transaction_id = f"trans_{uuid.uuid4().hex[:8]}"
        payment_timestamp = datetime.now().isoformat()
        
        # 不同支付方式的处理逻辑
        if payment_method == "ALIPAY":
            payment_url = f"https://pay.suoke.life/alipay/{payment_id}"
            receipt_url = f"https://pay.suoke.life/receipts/alipay/{payment_id}"
            
        elif payment_method == "WECHAT":
            payment_url = f"https://pay.suoke.life/wechat/{payment_id}"
            receipt_url = f"https://pay.suoke.life/receipts/wechat/{payment_id}"
            
        elif payment_method == "CREDIT_CARD":
            payment_url = f"https://pay.suoke.life/card/{payment_id}"
            receipt_url = f"https://pay.suoke.life/receipts/card/{payment_id}"
            
        else:
            # 默认支付URL
            payment_url = f"https://pay.suoke.life/generic/{payment_id}"
            receipt_url = f"https://pay.suoke.life/receipts/generic/{payment_id}"
        
        # 保存支付记录
        await self.order_repo.create_payment({
            'id': payment_id,
            'user_id': user_id,
            'order_id': order_id,
            'payment_method': payment_method,
            'amount': amount,
            'currency': currency,
            'transaction_id': transaction_id,
            'status': 'SUCCESS',  # 简化实现，实际应等待支付回调
            'created_at': payment_timestamp,
            'metadata': metadata
        })
        
        # 构建结果
        return {
            'payment_id': payment_id,
            'status': 'SUCCESS',  # 简化实现，实际应等待支付回调
            'transaction_id': transaction_id,
            'timestamp': payment_timestamp,
            'payment_url': payment_url,
            'receipt_url': receipt_url
        }
    
    async def _get_personalized_recommendations(self, user_id: str,
                                         constitution_type: str,
                                         season: str,
                                         health_conditions: List[str],
                                         preferences: List[str],
                                         max_results: int) -> List[Dict[str, Any]]:
        """
        获取个性化产品推荐
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            season: 季节
            health_conditions: 健康状况列表
            preferences: 偏好列表
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 个性化推荐产品列表
        """
        try:
            # 获取用户历史购买和浏览记录
            user_history = await self.order_repo.get_user_purchase_history(user_id)
            
            # 获取候选产品池
            candidate_products = await self.product_repo.get_recommendation_candidates(
                constitution_type, season, max_results * 3  # 获取更多候选，之后会过滤
            )
            
            # 为每个产品计算综合推荐分数
            scored_products = []
            for product in candidate_products:
                # 体质匹配分数
                constitution_score = self._calculate_constitution_match_score(
                    product, constitution_type
                )
                
                # 季节匹配分数
                season_score = self._calculate_season_match_score(
                    product, season
                )
                
                # 用户偏好分数
                preference_score = self._calculate_preference_match_score(
                    product, preferences, user_history
                )
                
                # 健康状况分数
                health_score = self._calculate_health_match_score(
                    product, health_conditions
                )
                
                # 综合计算加权分数
                total_score = (
                    self.weights['constitution_match'] * constitution_score +
                    self.weights['season_match'] * season_score +
                    self.weights['user_preference'] * preference_score +
                    self.weights['health_condition'] * health_score
                )
                
                # 记录分数
                product_copy = product.copy()
                product_copy['recommendation_score'] = total_score
                
                # 如果分数高于阈值，添加到结果
                if total_score >= self.min_confidence:
                    scored_products.append(product_copy)
            
            # 排序并限制数量
            scored_products.sort(key=lambda p: p['recommendation_score'], reverse=True)
            top_products = scored_products[:max_results]
            
            # 为每个产品添加推荐理由
            for product in top_products:
                product['recommendation_reason'] = self._generate_recommendation_reason(
                    product, constitution_type, season, health_conditions, preferences
                )
            
            return top_products
            
        except Exception as e:
            logger.error(f"获取个性化推荐失败: {str(e)}", exc_info=True)
            # 出错时返回空列表
            return []
    
    def _calculate_constitution_match_score(self, product: Dict[str, Any],
                                       constitution_type: str) -> float:
        """计算产品与体质的匹配分数"""
        supported_types = product.get('constitution_benefits', {}).keys()
        
        # 如果产品特别适合该体质
        if constitution_type in supported_types:
            benefit_level = product['constitution_benefits'][constitution_type]
            # 根据益处级别返回不同分数
            if benefit_level == "HIGH":
                return 1.0
            elif benefit_level == "MEDIUM":
                return 0.8
            else:
                return 0.6
        
        # 如果产品适合所有体质
        if 'ALL' in supported_types:
            return 0.5
        
        # 不匹配的情况
        return 0.2
    
    def _calculate_season_match_score(self, product: Dict[str, Any],
                                 season: str) -> float:
        """计算产品与季节的匹配分数"""
        product_seasons = product.get('seasons', [])
        
        # 如果产品没有季节信息
        if not product_seasons:
            return 0.5
        
        # 如果完全匹配当前季节
        if season in product_seasons:
            return 1.0
        
        # 如果适合所有季节
        if 'ALL' in product_seasons:
            return 0.8
        
        # 不匹配的情况
        return 0.3
    
    def _calculate_preference_match_score(self, product: Dict[str, Any],
                                     preferences: List[str],
                                     user_history: Dict[str, Any]) -> float:
        """计算产品与用户偏好的匹配分数"""
        # 偏好标签匹配
        preference_matches = 0
        for pref in preferences:
            if pref.lower() in product.get('tags', []) or pref.lower() in product.get('categories', []):
                preference_matches += 1
        
        preference_score = min(1.0, preference_matches / max(1, len(preferences)))
        
        # 用户历史兴趣匹配
        history_score = 0.0
        if user_history:
            # 检查用户是否购买过该类产品
            if product['id'] in user_history.get('purchased_products', []):
                history_score = 0.7  # 购买过，但不要太高以免只推荐用户已购买的
            
            # 检查用户是否浏览过该类产品
            elif product['id'] in user_history.get('viewed_products', []):
                history_score = 0.8
                
            # 检查用户是否购买过同类产品
            elif any(cat in user_history.get('purchased_categories', []) 
                   for cat in product.get('categories', [])):
                history_score = 0.9
        
        # 综合偏好和历史，取较高分
        return max(preference_score, history_score)
    
    def _calculate_health_match_score(self, product: Dict[str, Any],
                                 health_conditions: List[str]) -> float:
        """计算产品与健康状况的匹配分数"""
        if not health_conditions:
            return 0.5  # 没有健康条件，返回中等分数
            
        # 产品的健康益处
        health_benefits = product.get('health_benefits', [])
        
        # 产品的禁忌条件
        contraindications = product.get('contraindications', [])
        
        # 检查是否有禁忌
        for condition in health_conditions:
            if condition in contraindications:
                return 0.1  # 有禁忌，几乎不推荐
        
        # 检查有多少健康条件能得到改善
        benefit_matches = sum(1 for condition in health_conditions if condition in health_benefits)
        
        # 计算匹配比例
        return min(1.0, benefit_matches / max(1, len(health_conditions)))
    
    def _generate_recommendation_reason(self, product: Dict[str, Any],
                                   constitution_type: str,
                                   season: str,
                                   health_conditions: List[str],
                                   preferences: List[str]) -> str:
        """生成产品推荐理由"""
        reasons = []
        
        # 添加体质相关理由
        if constitution_type in product.get('constitution_benefits', {}):
            benefit_level = product['constitution_benefits'][constitution_type]
            if benefit_level == "HIGH":
                reasons.append(f"非常适合{constitution_type}体质")
            elif benefit_level == "MEDIUM":
                reasons.append(f"适合{constitution_type}体质")
            else:
                reasons.append(f"对{constitution_type}体质有益")
        
        # 添加季节相关理由
        if season in product.get('seasons', []):
            reasons.append(f"{season}季节时令食材")
        
        # 添加健康条件相关理由
        matching_benefits = [condition for condition in health_conditions 
                            if condition in product.get('health_benefits', [])]
        if matching_benefits:
            benefits_text = "、".join(matching_benefits[:2])
            reasons.append(f"有助于改善{benefits_text}")
        
        # 添加偏好相关理由
        matching_prefs = [pref for pref in preferences 
                         if pref.lower() in product.get('tags', []) 
                         or pref.lower() in product.get('categories', [])]
        if matching_prefs:
            prefs_text = "、".join(matching_prefs[:2])
            reasons.append(f"符合您对{prefs_text}的偏好")
        
        # 组合理由
        if reasons:
            return "；".join(reasons)
        else:
            return "根据您的整体情况推荐"