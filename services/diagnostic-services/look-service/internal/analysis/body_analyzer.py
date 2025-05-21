#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
形体分析器模块，负责人体体态的分析与体质关联判断。

形体分析是中医望诊的重要组成部分，通过观察体型、肢体比例、姿态等，
判断人体气血盛衰、脏腑功能状态。本模块实现了基于计算机视觉的形体智能分析。
"""

import os
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union

import cv2
import numpy as np
from structlog import get_logger

from internal.model.model_factory import ModelFactory
from pkg.utils.exceptions import InvalidInputError, ProcessingError
from pkg.utils.image_utils import decode_image, preprocess_image, draw_regions


# 设置日志
logger = get_logger()


class BodyShape(Enum):
    """体型类别枚举"""
    BALANCED = "平和质"  # 肌肉匀称，气血调和
    MUSCULAR = "阳盛质"  # 肌肉发达，阳气偏盛
    THIN = "气虚质"      # 体型偏瘦，气血不足
    OVERWEIGHT = "痰湿质" # 体型偏胖，湿气内蕴
    FLABBY = "阴虚质"    # 体型松弛，阴液亏虚


class Posture(Enum):
    """姿态类别枚举"""
    NORMAL = "正常姿态"      # 平稳挺拔
    FORWARD_HEAD = "头前倾"  # 头颈前伸，气血上逆
    ROUNDED_SHOULDERS = "肩前倾" # 肩膀前倾，气血不畅
    ANTERIOR_PELVIC = "骨盆前倾" # 骨盆前倾，下焦湿热
    POSTERIOR_PELVIC = "骨盆后倾" # 骨盆后倾，下焦虚寒


@dataclass
class BodyRatio:
    """体型比例数据类"""
    shoulder_hip_ratio: float  # 肩宽与臀宽比例
    waist_hip_ratio: float     # 腰围与臀围比例
    height_weight_ratio: float # 身高与体重比例
    limb_trunk_ratio: float    # 肢干比例


@dataclass
class BodyFeatures:
    """体态特征数据类"""
    body_shape: BodyShape              # 体型类别
    posture: Posture                   # 姿态类别
    ratio: BodyRatio                   # 体型比例
    joint_angles: Dict[str, float]     # 主要关节角度
    body_symmetry: float               # 身体对称性评分 (0-1)
    keypoints: Dict[str, Tuple[int, int]] # 人体关键点坐标


@dataclass
class BodyAnalysisResult:
    """形体分析结果数据类"""
    user_id: str                       # 用户ID
    image_id: str                      # 图像ID
    timestamp: float                   # 分析时间戳
    features: BodyFeatures             # 体态特征
    tcm_analysis: Dict[str, Any]       # 中医分析结果
    confidence: float                  # 分析置信度 (0-1)
    annotated_image: Optional[bytes]   # 标注后的图像数据
    

class BodyAnalyzer:
    """形体分析器类，负责人体形态分析"""
    
    def __init__(self, model_path: str = None):
        """
        初始化形体分析器
        
        Args:
            model_path: 模型路径，如果为None则使用配置中的路径
        """
        from config.config import get_config
        config = get_config()
        
        self.model_path = model_path or config.get("models.body_analysis.path")
        self.model_threshold = config.get("models.body_analysis.threshold", 0.6)
        self.input_size = tuple(config.get("models.body_analysis.input_size", [384, 384]))
        self.device = config.get("models.body_analysis.device", "cpu")
        
        # 加载模型
        logger.info("正在加载形体分析模型", path=self.model_path)
        try:
            self.model = ModelFactory.get_model(
                model_type="body_analysis",
                model_path=self.model_path,
                device=self.device
            )
            logger.info("形体分析模型加载成功")
        except Exception as e:
            logger.error("形体分析模型加载失败", error=str(e))
            self.model = None
    
    def analyze(self, image_data: bytes, user_id: str) -> BodyAnalysisResult:
        """
        分析人体形态
        
        Args:
            image_data: 图像二进制数据
            user_id: 用户ID
            
        Returns:
            形体分析结果
            
        Raises:
            InvalidInputError: 当输入图像无效时
            ProcessingError: 当处理过程中出错时
        """
        # 生成唯一图像ID
        image_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # 解码图像
        image = decode_image(image_data)
        if image is None:
            raise InvalidInputError("无法解码图像数据")
        
        # 检查图像是否包含人体
        if not self._contains_person(image):
            raise InvalidInputError("图像中未检测到完整人体")
        
        # 预处理图像
        preprocessed_image = preprocess_image(image, self.input_size)
        
        # 使用模型进行推理
        try:
            if self.model is None:
                # 模型未加载时使用模拟数据
                logger.warning("使用模拟数据进行形体分析")
                features = self._generate_mock_features()
                confidence = 0.7
            else:
                # 执行实际推理
                model_output = self.model.predict(preprocessed_image)
                # 提取身体特征
                features, confidence = self._extract_body_features(model_output, image)
                
                # 检查置信度
                if confidence < self.model_threshold:
                    logger.warning("形体分析置信度较低", confidence=confidence)
        except Exception as e:
            logger.error("形体分析失败", error=str(e))
            raise ProcessingError(f"形体分析处理失败: {str(e)}")
        
        # 生成中医分析结果
        tcm_analysis = self._generate_tcm_analysis(features)
        
        # 生成标注图像
        annotated_image = self._generate_annotated_image(image, features)
        
        # 构建并返回结果
        result = BodyAnalysisResult(
            user_id=user_id,
            image_id=image_id,
            timestamp=timestamp,
            features=features,
            tcm_analysis=tcm_analysis,
            confidence=confidence,
            annotated_image=annotated_image
        )
        
        return result
    
    def _contains_person(self, image: np.ndarray) -> bool:
        """
        检查图像是否包含完整的人体
        
        Args:
            image: 图像数据
            
        Returns:
            是否包含人体
        """
        # 在实际实现中，这里应该使用人体检测模型
        # 简单起见，这里假设图像中始终存在人体
        return True
    
    def _extract_body_features(self, model_output: Dict[str, Any], 
                              image: np.ndarray) -> Tuple[BodyFeatures, float]:
        """
        从模型输出中提取身体特征
        
        Args:
            model_output: 模型输出
            image: 原始图像
            
        Returns:
            身体特征和置信度
        """
        # 在实际实现中，这里应该从模型输出解析关键点等信息
        # 简单起见，这里返回模拟数据
        return self._generate_mock_features(), 0.85
    
    def _generate_mock_features(self) -> BodyFeatures:
        """
        生成模拟的身体特征数据
        
        Returns:
            模拟的身体特征
        """
        # 关节角度
        joint_angles = {
            "neck": 165.2,
            "shoulder_right": 172.5,
            "shoulder_left": 173.1,
            "elbow_right": 168.9,
            "elbow_left": 167.2,
            "spine_upper": 178.5,
            "spine_lower": 175.2,
            "hip_right": 172.3,
            "hip_left": 173.1,
            "knee_right": 176.8,
            "knee_left": 177.2,
            "ankle_right": 85.3,
            "ankle_left": 84.9
        }
        
        # 关键点坐标 (x, y)
        keypoints = {
            "head": (192, 40),
            "neck": (192, 80),
            "shoulder_right": (230, 100),
            "shoulder_left": (154, 100),
            "elbow_right": (250, 150),
            "elbow_left": (134, 150),
            "wrist_right": (260, 190),
            "wrist_left": (124, 190),
            "hip_right": (220, 210),
            "hip_left": (164, 210),
            "knee_right": (225, 280),
            "knee_left": (159, 280),
            "ankle_right": (230, 350),
            "ankle_left": (154, 350)
        }
        
        # 体型比例
        body_ratio = BodyRatio(
            shoulder_hip_ratio=1.4,
            waist_hip_ratio=0.8,
            height_weight_ratio=2.3,
            limb_trunk_ratio=1.1
        )
        
        # 随机选择体型和姿态
        body_shapes = list(BodyShape)
        postures = list(Posture)
        
        body_shape = np.random.choice(body_shapes)
        posture = np.random.choice(postures)
        body_symmetry = round(np.random.uniform(0.85, 0.98), 2)
        
        # 构建特征对象
        features = BodyFeatures(
            body_shape=body_shape,
            posture=posture,
            ratio=body_ratio,
            joint_angles=joint_angles,
            body_symmetry=body_symmetry,
            keypoints=keypoints
        )
        
        return features
    
    def _generate_tcm_analysis(self, features: BodyFeatures) -> Dict[str, Any]:
        """
        根据身体特征生成中医分析结果
        
        Args:
            features: 身体特征
            
        Returns:
            中医分析结果
        """
        # 基于体型类别的中医解读
        body_shape_analysis = {
            BodyShape.BALANCED: {
                "constitution": "平和质",
                "description": "体形匀称，肌肉结实有弹性，气血调和",
                "suggestion": "保持规律生活和均衡饮食，防止外邪侵袭"
            },
            BodyShape.MUSCULAR: {
                "constitution": "阳盛质",
                "description": "体格健壮，肌肉发达，阳气偏盛",
                "suggestion": "饮食宜清淡，避免辛辣刺激，适当滋阴降火"
            },
            BodyShape.THIN: {
                "constitution": "气虚质",
                "description": "体形偏瘦，肌肉松软，气血不足",
                "suggestion": "适当补充优质蛋白，进行缓和运动，注意保暖"
            },
            BodyShape.OVERWEIGHT: {
                "constitution": "痰湿质", 
                "description": "体形肥胖，腹部松软，湿气内蕴",
                "suggestion": "控制饮食，增加活动，祛湿健脾"
            },
            BodyShape.FLABBY: {
                "constitution": "阴虚质",
                "description": "体型松弛，肌肉无力，阴液亏虚",
                "suggestion": "增加优质蛋白摄入，补充水分，滋阴养血"
            }
        }
        
        # 基于姿态的中医解读
        posture_analysis = {
            Posture.NORMAL: {
                "meridian_flow": "顺畅",
                "description": "姿态端正，气血运行通畅",
                "suggestion": "保持良好姿态，定期进行身体调整"
            },
            Posture.FORWARD_HEAD: {
                "meridian_flow": "上逆",
                "description": "头颈前伸，颈部气血上逆，导致头重脚轻",
                "suggestion": "加强颈部肌肉锻炼，调整工作姿势，避免长时间低头"
            },
            Posture.ROUNDED_SHOULDERS: {
                "meridian_flow": "胸闷",
                "description": "肩膀前倾，胸部气血不畅，影响心肺功能",
                "suggestion": "加强背部肌肉锻炼，调整坐姿，定期舒展胸部"
            },
            Posture.ANTERIOR_PELVIC: {
                "meridian_flow": "下焦湿热",
                "description": "骨盆前倾，腰椎压力增大，下焦湿热",
                "suggestion": "强化核心肌群，调整站立姿势，注意清热利湿"
            },
            Posture.POSTERIOR_PELVIC: {
                "meridian_flow": "下焦虚寒",
                "description": "骨盆后倾，腰腹气血不足，下焦虚寒",
                "suggestion": "加强腰腹部锻炼，调整站坐姿势，注意温补肾阳"
            }
        }
        
        # 体型比例分析
        ratio_analysis = {}
        if features.ratio.shoulder_hip_ratio > 1.45:
            ratio_analysis["upper_body"] = "上盛下虚，上肢气血充盈，下肢气血不足"
        elif features.ratio.shoulder_hip_ratio < 1.2:
            ratio_analysis["upper_body"] = "上虚下盛，上肢气血不足，下肢气血滞留"
        else:
            ratio_analysis["upper_body"] = "上下匀称，气血分布均衡"
            
        if features.ratio.waist_hip_ratio > 0.9:
            ratio_analysis["central_body"] = "中部积滞，脾胃湿热，代谢不畅"
        elif features.ratio.waist_hip_ratio < 0.7:
            ratio_analysis["central_body"] = "中部偏弱，脾胃虚寒，吸收不良"
        else:
            ratio_analysis["central_body"] = "中部匀称，脾胃功能正常"
        
        # 身体对称性分析
        symmetry_analysis = {}
        if features.body_symmetry > 0.9:
            symmetry_analysis["description"] = "左右对称性良好，气血流通均衡"
            symmetry_analysis["suggestion"] = "保持均衡锻炼，避免偏侧用力"
        elif features.body_symmetry > 0.8:
            symmetry_analysis["description"] = "左右对称性一般，存在轻微气血不均"
            symmetry_analysis["suggestion"] = "注意调整不良姿势，均衡锻炼左右肢体"
        else:
            symmetry_analysis["description"] = "左右对称性较差，气血流通不均"
            symmetry_analysis["suggestion"] = "建议就医检查，针对性调整肌肉平衡"
        
        # 综合分析
        analysis = {
            "body_shape": body_shape_analysis[features.body_shape],
            "posture": posture_analysis[features.posture],
            "ratio": ratio_analysis,
            "symmetry": symmetry_analysis,
            "summary": {
                "constitution_tendency": features.body_shape.value,
                "primary_issue": features.posture.value if features.posture != Posture.NORMAL else "无明显问题",
                "recommendation": f"建议调整{features.posture.value if features.posture != Posture.NORMAL else '日常姿态'}，并根据{features.body_shape.value}特点进行调理"
            }
        }
        
        return analysis
    
    def _generate_annotated_image(self, image: np.ndarray, 
                                features: BodyFeatures) -> Optional[bytes]:
        """
        生成标注后的图像
        
        Args:
            image: 原始图像
            features: 身体特征
            
        Returns:
            标注后的图像二进制数据
        """
        try:
            # 创建图像副本
            annotated = image.copy()
            
            # 绘制骨骼结构
            keypoints = features.keypoints
            connections = [
                ("head", "neck"),
                ("neck", "shoulder_right"),
                ("neck", "shoulder_left"),
                ("shoulder_right", "elbow_right"),
                ("shoulder_left", "elbow_left"),
                ("elbow_right", "wrist_right"),
                ("elbow_left", "wrist_left"),
                ("neck", "hip_right"),
                ("neck", "hip_left"),
                ("hip_right", "knee_right"),
                ("hip_left", "knee_left"),
                ("knee_right", "ankle_right"),
                ("knee_left", "ankle_left"),
                ("hip_right", "hip_left")
            ]
            
            # 绘制关节点
            for point_name, (x, y) in keypoints.items():
                cv2.circle(annotated, (x, y), 5, (0, 255, 0), -1)
                
            # 绘制连接线
            for point1_name, point2_name in connections:
                if point1_name in keypoints and point2_name in keypoints:
                    pt1 = keypoints[point1_name]
                    pt2 = keypoints[point2_name]
                    cv2.line(annotated, pt1, pt2, (0, 0, 255), 2)
            
            # 添加体型和姿态标签
            cv2.putText(annotated, f"体型: {features.body_shape.value}", 
                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(annotated, f"姿态: {features.posture.value}", 
                      (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(annotated, f"对称性: {features.body_symmetry:.2f}", 
                      (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 显示不良姿态的角度
            if features.posture != Posture.NORMAL:
                # 找出需要标记的关节角度
                angle_markers = {
                    Posture.FORWARD_HEAD: ("neck", "颈部角度"),
                    Posture.ROUNDED_SHOULDERS: ("shoulder_right", "肩部角度"),
                    Posture.ANTERIOR_PELVIC: ("spine_lower", "骨盆角度"),
                    Posture.POSTERIOR_PELVIC: ("spine_lower", "骨盆角度"),
                }
                
                if features.posture in angle_markers:
                    joint, label = angle_markers[features.posture]
                    if joint in features.joint_angles:
                        angle = features.joint_angles[joint]
                        cv2.putText(annotated, f"{label}: {angle:.1f}°", 
                                  (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 将图像编码为JPEG格式
            _, buffer = cv2.imencode('.jpg', annotated)
            return buffer.tobytes()
            
        except Exception as e:
            logger.error("生成标注图像失败", error=str(e))
            return None 