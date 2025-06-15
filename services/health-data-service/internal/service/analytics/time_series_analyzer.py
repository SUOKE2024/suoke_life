#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
时间序列数据分析器
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
from uuid import uuid4

# 尝试导入可选依赖
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet库未安装，将使用备用趋势分析方法")

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn库未安装，将使用简化的异常检测方法")


class TimeSeriesAnalyzer:
    """时间序列数据分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化时间序列分析器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.window_sizes = config.get('window_sizes', [7, 14, 30, 90])
        
        # 趋势检测配置
        self.trend_config = config.get('trend_detection', {})
        self.trend_algorithm = self.trend_config.get('algorithm', 'prophet')
        
        # 异常检测配置
        self.anomaly_config = config.get('anomaly_detection', {})
        self.anomaly_algorithm = self.anomaly_config.get('algorithm', 'isolation_forest')
        self.contamination = self.anomaly_config.get('contamination', 0.05)
    
    async def analyze_trend(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        window_days: int = 30,
        predict_days: int = 7
    ) -> Dict[str, Any]:
        """
        分析时间序列趋势
        
        Args:
            data: 时间序列数据
            data_type: 数据类型
            window_days: 分析窗口大小（天）
            predict_days: 预测天数
            
        Returns:
            趋势分析结果
        """
        if not data:
            return {
                "trend": "no_data",
                "trend_value": 0,
                "analysis": "没有足够的数据进行趋势分析"
            }
        
        # 转换数据为DataFrame
        df = self._prepare_dataframe(data)
        
        # 如果数据点太少，直接返回
        if len(df) < 5:
            return {
                "trend": "insufficient_data",
                "trend_value": 0,
                "analysis": "没有足够的数据进行趋势分析（至少需要5个数据点）"
            }
        
        # 根据配置选择趋势分析算法
        if self.trend_algorithm == 'prophet' and PROPHET_AVAILABLE:
            trend_result = self._analyze_with_prophet(df, data_type, predict_days)
        else:
            trend_result = self._analyze_with_simple_trend(df, data_type)
        
        # 添加基本统计信息
        stats = self._calculate_statistics(df)
        trend_result.update(stats)
        
        return trend_result
    
    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """
        检测时间序列中的异常值
        
        Args:
            data: 时间序列数据
            data_type: 数据类型
            window_days: 分析窗口大小（天）
            
        Returns:
            异常检测结果
        """
        if not data:
            return {
                "anomalies": [],
                "analysis": "没有足够的数据进行异常检测"
            }
        
        # 转换数据为DataFrame
        df = self._prepare_dataframe(data)
        
        # 如果数据点太少，直接返回
        if len(df) < 10:
            return {
                "anomalies": [],
                "analysis": "没有足够的数据进行异常检测（至少需要10个数据点）"
            }
        
        # 根据配置选择异常检测算法
        if self.anomaly_algorithm == 'isolation_forest' and SKLEARN_AVAILABLE:
            anomalies = self._detect_anomalies_with_isolation_forest(df, data_type)
        else:
            anomalies = self._detect_anomalies_with_simple_method(df, data_type)
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "analysis": f"检测到{len(anomalies)}个异常点" if anomalies else "未检测到异常"
        }
    
    async def generate_insights(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        从时间序列数据中生成洞察
        
        Args:
            data: 时间序列数据
            data_type: 数据类型
            user_id: 用户ID
            
        Returns:
            洞察列表
        """
        insights = []
        
        # 如果数据太少，直接返回
        if len(data) < 10:
            return []
        
        # 执行各种分析
        for window_days in self.window_sizes:
            # 过滤最近的数据
            recent_data = self._filter_recent_data(data, window_days)
            
            if len(recent_data) < 5:
                continue
            
            # 分析趋势
            trend_result = await self.analyze_trend(recent_data, data_type, window_days)
            trend = trend_result.get("trend")
            trend_value = trend_result.get("trend_value", 0)
            
            # 检测异常
            anomaly_result = await self.detect_anomalies(recent_data, data_type, window_days)
            anomalies = anomaly_result.get("anomalies", [])
            
            # 生成洞察 - 趋势洞察
            if trend in ["increasing", "decreasing"]:
                # 计算相关性分数（0-1，越高越重要）
                relevance = min(abs(trend_value) / 0.5, 1.0) if trend_value else 0.5
                
                # 确定严重程度
                severity = "info"
                if relevance > 0.7:
                    severity = "warning" if trend == "decreasing" else "info"
                
                insight_text = self._generate_trend_insight_text(data_type, trend, trend_value, window_days)
                
                insights.append({
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "timestamp": datetime.utcnow(),
                    "insight_type": "trend",
                    "data_type": data_type,
                    "time_range": {
                        "start": data[0]["timestamp"] if data else datetime.utcnow() - timedelta(days=window_days),
                        "end": datetime.utcnow()
                    },
                    "description": insight_text,
                    "details": {
                        "trend": trend,
                        "trend_value": trend_value,
                        "window_days": window_days,
                        "statistics": {
                            "mean": trend_result.get("mean"),
                            "std": trend_result.get("std"),
                            "min": trend_result.get("min"),
                            "max": trend_result.get("max")
                        }
                    },
                    "severity": severity,
                    "relevance_score": relevance
                })
            
            # 生成洞察 - 异常值洞察
            for anomaly in anomalies:
                # 异常的严重程度（基于z-score）
                z_score = anomaly.get("z_score", 0)
                relevance = min(abs(z_score) / 3.0, 1.0)
                
                severity = "info"
                if abs(z_score) > 3.0:
                    severity = "warning"
                if abs(z_score) > 5.0:
                    severity = "alert"
                
                insight_text = self._generate_anomaly_insight_text(data_type, anomaly)
                
                insights.append({
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "timestamp": datetime.utcnow(),
                    "insight_type": "anomaly",
                    "data_type": data_type,
                    "time_range": {
                        "start": anomaly["timestamp"] - timedelta(hours=12),
                        "end": anomaly["timestamp"] + timedelta(hours=12)
                    },
                    "description": insight_text,
                    "details": anomaly,
                    "severity": severity,
                    "relevance_score": relevance
                })
        
        # 筛选最重要的洞察（避免太多洞察）
        insights.sort(key=lambda x: x["relevance_score"], reverse=True)
        return insights[:5]  # 只返回前5个最相关的洞察
    
    def _prepare_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        将数据转换为Pandas DataFrame
        
        Args:
            data: 时间序列数据
            
        Returns:
            DataFrame对象
        """
        # 转换数据为DataFrame格式
        records = []
        for item in data:
            timestamp = item.get("timestamp")
            value = item.get("value")
            
            # 处理不同类型的值
            if isinstance(value, dict) and "value" in value:
                value = value["value"]
            elif isinstance(value, dict):
                # 尝试找到主要值字段
                for key in ["value", "steps", "heart_rate", "calories", "distance"]:
                    if key in value:
                        value = value[key]
                        break
            
            if timestamp and value is not None:
                records.append({"timestamp": timestamp, "value": value})
        
        df = pd.DataFrame(records)
        
        if not df.empty:
            # 确保时间戳格式正确
            if df["timestamp"].dtype == object:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # 确保值为数值类型
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            
            # 按时间戳排序
            df = df.sort_values("timestamp")
            
            # 删除缺失值
            df = df.dropna()
        
        return df
    
    def _filter_recent_data(self, data: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """
        过滤最近的数据
        
        Args:
            data: 时间序列数据
            days: 天数
            
        Returns:
            过滤后的数据
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [item for item in data if item.get("timestamp", datetime.min) >= cutoff_date]
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算基本统计信息
        
        Args:
            df: DataFrame对象
            
        Returns:
            统计信息
        """
        if df.empty:
            return {
                "mean": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "median": 0,
                "count": 0
            }
        
        return {
            "mean": df["value"].mean(),
            "std": df["value"].std(),
            "min": df["value"].min(),
            "max": df["value"].max(),
            "median": df["value"].median(),
            "count": len(df)
        }
    
    def _analyze_with_prophet(self, df: pd.DataFrame, data_type: str, predict_days: int) -> Dict[str, Any]:
        """
        使用Prophet进行趋势分析
        
        Args:
            df: DataFrame对象
            data_type: 数据类型
            predict_days: 预测天数
            
        Returns:
            趋势分析结果
        """
        try:
            # 准备Prophet所需的数据格式
            prophet_df = df.rename(columns={"timestamp": "ds", "value": "y"})
            
            # 创建并拟合模型
            model = Prophet(
                changepoint_prior_scale=self.trend_config.get("changepoint_prior_scale", 0.05),
                seasonality_mode=self.trend_config.get("seasonality_mode", "multiplicative")
            )
            model.fit(prophet_df)
            
            # 创建未来日期
            future = model.make_future_dataframe(periods=predict_days)
            
            # 预测
            forecast = model.predict(future)
            
            # 分析趋势
            trend_component = forecast["trend"]
            
            if len(trend_component) >= 2:
                start_trend = trend_component.iloc[0]
                end_trend = trend_component.iloc[-1]
                total_change = end_trend - start_trend
                
                # 归一化趋势值（每天的平均变化比例）
                days_span = (forecast["ds"].iloc[-1] - forecast["ds"].iloc[0]).days
                if days_span > 0 and start_trend != 0:
                    normalized_trend = total_change / (days_span * abs(start_trend))
                else:
                    normalized_trend = 0
                
                # 判断趋势方向
                if normalized_trend > 0.01:
                    trend = "increasing"
                elif normalized_trend < -0.01:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                # 构建结果
                result = {
                    "trend": trend,
                    "trend_value": normalized_trend,
                    "analysis": self._get_trend_description(data_type, trend, normalized_trend),
                    "prediction": [
                        {"timestamp": row["ds"], "value": row["yhat"]}
                        for idx, row in forecast.iloc[-predict_days:].iterrows()
                    ],
                    "changepoints": [
                        {"timestamp": date}
                        for date in model.changepoints
                    ] if hasattr(model, "changepoints") else []
                }
                
                return result
            else:
                return {
                    "trend": "insufficient_data",
                    "trend_value": 0,
                    "analysis": "没有足够的数据进行趋势分析（至少需要2个数据点）"
                }
                
        except Exception as e:
            logging.warning(f"Prophet分析失败: {str(e)}")
            # 失败时使用简单方法作为备选
            return self._analyze_with_simple_trend(df, data_type)
    
    def _analyze_with_simple_trend(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """
        使用简单方法进行趋势分析
        
        Args:
            df: DataFrame对象
            data_type: 数据类型
            
        Returns:
            趋势分析结果
        """
        # 至少需要2个点才能计算趋势
        if len(df) < 2:
            return {
                "trend": "insufficient_data",
                "trend_value": 0,
                "analysis": "没有足够的数据进行趋势分析（至少需要2个数据点）"
            }
        
        # 计算时间跨度（天）
        time_span = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds() / (24 * 3600)
        
        if time_span <= 0:
            return {
                "trend": "insufficient_data",
                "trend_value": 0,
                "analysis": "数据时间跨度太短，无法进行趋势分析"
            }
        
        # 计算线性回归
        x = np.array((df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds() / (24 * 3600))
        y = df["value"].values
        
        # 标准化X和Y
        x_norm = (x - np.mean(x)) / np.std(x) if np.std(x) > 0 else np.zeros_like(x)
        y_norm = (y - np.mean(y)) / np.std(y) if np.std(y) > 0 else np.zeros_like(y)
        
        # 计算趋势斜率
        if np.std(x) > 0 and np.std(y) > 0:
            slope = np.sum(x_norm * y_norm) / len(x)
        else:
            slope = 0
        
        # 判断趋势方向
        if slope > 0.1:
            trend = "increasing"
        elif slope < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # 计算变化率
        if len(df) >= 2 and df["value"].iloc[0] != 0:
            first_val = df["value"].iloc[0]
            last_val = df["value"].iloc[-1]
            
            # 归一化趋势值（每天的平均变化比例）
            total_change = last_val - first_val
            normalized_trend = total_change / (time_span * abs(first_val)) if time_span > 0 else 0
        else:
            normalized_trend = 0
        
        return {
            "trend": trend,
            "trend_value": normalized_trend,
            "analysis": self._get_trend_description(data_type, trend, normalized_trend),
            "first_value": df["value"].iloc[0],
            "last_value": df["value"].iloc[-1],
            "slope": slope
        }
    
    def _detect_anomalies_with_isolation_forest(self, df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """
        使用隔离森林算法检测异常值
        
        Args:
            df: DataFrame对象
            data_type: 数据类型
            
        Returns:
            异常检测结果
        """
        try:
            # 准备特征数据
            X = df["value"].values.reshape(-1, 1)
            
            # 标准化数据
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 创建并训练隔离森林模型
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            
            # 预测异常（-1表示异常，1表示正常）
            predictions = model.fit_predict(X_scaled)
            anomaly_scores = model.decision_function(X_scaled)
            
            # 转换成Z分数
            z_scores = -1 * anomaly_scores / np.std(anomaly_scores) if np.std(anomaly_scores) > 0 else np.zeros_like(anomaly_scores)
            
            # 识别异常点
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # 异常点
                    timestamp = df["timestamp"].iloc[i]
                    value = df["value"].iloc[i]
                    
                    # 计算相对差异（与均值的差异百分比）
                    mean_value = df["value"].mean()
                    if mean_value != 0:
                        relative_diff = (value - mean_value) / abs(mean_value)
                    else:
                        relative_diff = 0
                    
                    anomalies.append({
                        "timestamp": timestamp,
                        "value": value,
                        "z_score": float(z_scores[i]),
                        "anomaly_score": float(anomaly_scores[i]),
                        "relative_diff": float(relative_diff),
                        "direction": "high" if value > mean_value else "low"
                    })
            
            return anomalies
        except Exception as e:
            logging.warning(f"隔离森林异常检测失败: {str(e)}")
            # 失败时使用简单方法作为备选
            return self._detect_anomalies_with_simple_method(df, data_type)
    
    def _detect_anomalies_with_simple_method(self, df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """
        使用简单统计方法检测异常值
        
        Args:
            df: DataFrame对象
            data_type: 数据类型
            
        Returns:
            异常检测结果
        """
        anomalies = []
        
        if len(df) < 4:
            return anomalies  # 至少需要4个点才能进行可靠的异常检测
        
        # 计算均值和标准差
        mean_value = df["value"].mean()
        std_value = df["value"].std()
        
        if std_value == 0:
            return anomalies  # 如果标准差为0，则无法进行异常检测
        
        # 使用z-score方法检测异常值
        z_scores = (df["value"] - mean_value) / std_value
        
        # 识别异常点
        threshold = 2.5  # z-score阈值
        for i, z_score in enumerate(z_scores):
            if abs(z_score) > threshold:
                timestamp = df["timestamp"].iloc[i]
                value = df["value"].iloc[i]
                
                # 计算相对差异（与均值的差异百分比）
                if mean_value != 0:
                    relative_diff = (value - mean_value) / abs(mean_value)
                else:
                    relative_diff = 0
                
                anomalies.append({
                    "timestamp": timestamp,
                    "value": value,
                    "z_score": float(z_score),
                    "relative_diff": float(relative_diff),
                    "direction": "high" if value > mean_value else "low"
                })
        
        return anomalies
    
    def _get_trend_description(self, data_type: str, trend: str, trend_value: float) -> str:
        """
        获取趋势描述文本
        
        Args:
            data_type: 数据类型
            trend: 趋势类型
            trend_value: 趋势值
            
        Returns:
            趋势描述文本
        """
        data_type_desc = {
            "steps": "步数",
            "heart_rate": "心率",
            "sleep": "睡眠时长",
            "blood_pressure": "血压",
            "blood_glucose": "血糖",
            "body_mass": "体重",
            "body_fat": "体脂率",
            "activity": "活动量",
            "respiratory_rate": "呼吸率",
            "oxygen_saturation": "血氧饱和度"
        }.get(data_type, data_type)
        
        if trend == "increasing":
            change_pct = abs(trend_value) * 100
            if change_pct > 5:
                return f"您的{data_type_desc}呈明显上升趋势，每天平均增加约{change_pct:.1f}%"
            else:
                return f"您的{data_type_desc}呈缓慢上升趋势，每天平均增加约{change_pct:.1f}%"
        elif trend == "decreasing":
            change_pct = abs(trend_value) * 100
            if change_pct > 5:
                return f"您的{data_type_desc}呈明显下降趋势，每天平均减少约{change_pct:.1f}%"
            else:
                return f"您的{data_type_desc}呈缓慢下降趋势，每天平均减少约{change_pct:.1f}%"
        else:
            return f"您的{data_type_desc}保持稳定，没有明显变化趋势"
    
    def _generate_trend_insight_text(self, data_type: str, trend: str, trend_value: float, window_days: int) -> str:
        """
        生成趋势洞察文本
        
        Args:
            data_type: 数据类型
            trend: 趋势类型
            trend_value: 趋势值
            window_days: 窗口大小（天）
            
        Returns:
            洞察文本
        """
        data_type_desc = {
            "steps": "步数",
            "heart_rate": "心率",
            "sleep": "睡眠时长",
            "blood_pressure": "血压",
            "blood_glucose": "血糖",
            "body_mass": "体重",
            "body_fat": "体脂率",
            "activity": "活动量",
            "respiratory_rate": "呼吸率",
            "oxygen_saturation": "血氧饱和度"
        }.get(data_type, data_type)
        
        time_desc = f"过去{window_days}天"
        
        if trend == "increasing":
            change_pct = abs(trend_value) * 100 * window_days
            intensity = "显著" if change_pct > 20 else "逐渐"
            
            # 根据数据类型给出不同的建议
            if data_type in ["steps", "activity"]:
                return f"{time_desc}，您的{data_type_desc}{intensity}增加了约{change_pct:.1f}%，体现了良好的活动习惯"
            elif data_type in ["body_mass", "body_fat"]:
                return f"{time_desc}，您的{data_type_desc}{intensity}增加了约{change_pct:.1f}%，建议关注饮食和运动习惯"
            else:
                return f"{time_desc}，您的{data_type_desc}{intensity}增加了约{change_pct:.1f}%"
        
        elif trend == "decreasing":
            change_pct = abs(trend_value) * 100 * window_days
            intensity = "显著" if change_pct > 20 else "逐渐"
            
            # 根据数据类型给出不同的建议
            if data_type in ["steps", "activity", "sleep"]:
                return f"{time_desc}，您的{data_type_desc}{intensity}减少了约{change_pct:.1f}%，建议保持良好的生活习惯"
            elif data_type in ["body_mass", "body_fat"]:
                return f"{time_desc}，您的{data_type_desc}{intensity}减少了约{change_pct:.1f}%，反映了良好的减重进展"
            else:
                return f"{time_desc}，您的{data_type_desc}{intensity}减少了约{change_pct:.1f}%"
        
        else:
            return f"{time_desc}，您的{data_type_desc}保持稳定，没有明显变化"
    
    def _generate_anomaly_insight_text(self, data_type: str, anomaly: Dict[str, Any]) -> str:
        """
        生成异常值洞察文本
        
        Args:
            data_type: 数据类型
            anomaly: 异常值信息
            
        Returns:
            洞察文本
        """
        data_type_desc = {
            "steps": "步数",
            "heart_rate": "心率",
            "sleep": "睡眠时长",
            "blood_pressure": "血压",
            "blood_glucose": "血糖",
            "body_mass": "体重",
            "body_fat": "体脂率",
            "activity": "活动量",
            "respiratory_rate": "呼吸率",
            "oxygen_saturation": "血氧饱和度"
        }.get(data_type, data_type)
        
        timestamp = anomaly.get("timestamp")
        value = anomaly.get("value")
        direction = anomaly.get("direction", "")
        relative_diff = anomaly.get("relative_diff", 0)
        
        date_str = timestamp.strftime("%Y年%m月%d日 %H:%M")
        diff_pct = abs(relative_diff) * 100
        
        level_desc = ""
        if diff_pct > 50:
            level_desc = "异常"
        elif diff_pct > 30:
            level_desc = "明显"
        else:
            level_desc = "轻微"
        
        direction_desc = "高于" if direction == "high" else "低于"
        
        return f"在{date_str}，检测到您的{data_type_desc}出现{level_desc}波动，{direction_desc}平均水平约{diff_pct:.1f}%" 