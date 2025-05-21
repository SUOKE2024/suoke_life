#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理工具模块

提供图像质量检查、预处理和格式转换功能。
"""

import io
import base64
from typing import Tuple, Dict, Any, Optional, List, Union

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

from pkg.utils.exceptions import InvalidInputError


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    从二进制数据加载图像
    
    Args:
        image_bytes: 图像的二进制数据
        
    Returns:
        numpy数组格式的图像 (BGR)
        
    Raises:
        InvalidInputError: 当图像无法解码时
    """
    if not image_bytes:
        raise InvalidInputError("图像数据为空")
    
    try:
        # 尝试解码图像
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise InvalidInputError("无法解码图像数据")
        
        return image
    except Exception as e:
        raise InvalidInputError(f"图像加载失败: {str(e)}")


def load_image_from_base64(base64_str: str) -> np.ndarray:
    """
    从Base64字符串加载图像
    
    Args:
        base64_str: Base64编码的图像字符串
        
    Returns:
        numpy数组格式的图像 (BGR)
        
    Raises:
        InvalidInputError: 当Base64数据无效或图像无法解码时
    """
    try:
        # 如果字符串包含前缀，去掉前缀
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
            
        # 解码Base64数据
        image_bytes = base64.b64decode(base64_str)
        
        # 加载图像
        return load_image_from_bytes(image_bytes)
    except Exception as e:
        raise InvalidInputError(f"Base64图像加载失败: {str(e)}")


def convert_to_base64(image: np.ndarray, format: str = 'jpeg', quality: int = 90) -> str:
    """
    将图像转换为Base64字符串
    
    Args:
        image: 图像 (BGR)
        format: 输出格式 ('jpeg' 或 'png')
        quality: 图像质量 (1-100, 仅用于JPEG)
        
    Returns:
        Base64编码的图像字符串
    """
    # 根据指定格式设置图像编码参数
    if format.lower() == 'jpeg' or format.lower() == 'jpg':
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        mime_type = 'image/jpeg'
        ext = '.jpg'
    elif format.lower() == 'png':
        encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), min(9, max(0, 10 - quality // 10))]
        mime_type = 'image/png'
        ext = '.png'
    else:
        raise ValueError(f"不支持的格式: {format}")
    
    # 编码图像
    _, buffer = cv2.imencode(ext, image, encode_param)
    
    # 转换为Base64
    base64_str = base64.b64encode(buffer).decode('utf-8')
    
    # 添加MIME类型前缀
    return f"data:{mime_type};base64,{base64_str}"


def resize_image(image: np.ndarray, width: int, height: int, 
                 keep_aspect_ratio: bool = True, 
                 interpolation: int = cv2.INTER_AREA) -> np.ndarray:
    """
    调整图像大小
    
    Args:
        image: 输入图像 (BGR)
        width: 目标宽度
        height: 目标高度
        keep_aspect_ratio: 是否保持长宽比
        interpolation: 插值方法
        
    Returns:
        调整大小后的图像
    """
    if keep_aspect_ratio:
        h, w = image.shape[:2]
        
        # 计算目标长宽比和原始长宽比
        target_ratio = width / height
        original_ratio = w / h
        
        if original_ratio > target_ratio:
            # 如果原始图像更宽，则以宽度为准
            new_width = width
            new_height = int(width / original_ratio)
        else:
            # 如果原始图像更高，则以高度为准
            new_height = height
            new_width = int(height * original_ratio)
            
        # 调整大小
        resized = cv2.resize(image, (new_width, new_height), interpolation=interpolation)
        
        # 创建目标大小的空白图像 (黑色背景)
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 计算粘贴位置 (居中)
        y_offset = (height - new_height) // 2
        x_offset = (width - new_width) // 2
        
        # 粘贴调整大小后的图像
        result[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
        
        return result
    else:
        # 直接调整到目标大小，可能会变形
        return cv2.resize(image, (width, height), interpolation=interpolation)


def crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    裁剪图像
    
    Args:
        image: 输入图像 (BGR)
        x: 左上角x坐标
        y: 左上角y坐标
        width: 裁剪宽度
        height: 裁剪高度
        
    Returns:
        裁剪后的图像
        
    Raises:
        ValueError: 当裁剪区域超出图像范围时
    """
    h, w = image.shape[:2]
    
    # 验证裁剪区域是否有效
    if x < 0 or y < 0 or x + width > w or y + height > h:
        raise ValueError("裁剪区域超出图像范围")
    
    return image[y:y+height, x:x+width].copy()


def check_image_quality(image: np.ndarray) -> Dict[str, Any]:
    """
    检查图像质量
    
    评估图像的清晰度、亮度、对比度和噪声水平。
    
    Args:
        image: 输入图像 (BGR)
        
    Returns:
        包含图像质量指标的字典
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 图像尺寸
    height, width = gray.shape
    image_size = height * width
    
    # 清晰度 (拉普拉斯方差)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness = min(1.0, lap_var / 500)  # 标准化，最大值为1.0
    
    # 亮度 (平均像素值)
    brightness = np.mean(gray) / 255.0
    
    # 对比度 (像素值标准差)
    contrast = np.std(gray) / 128.0
    
    # 噪声水平估计 (模糊后的均方差)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    noise_level = np.sqrt(np.mean((gray.astype(float) - blurred.astype(float)) ** 2)) / 255.0
    
    # 整体质量评分 (0-100)
    overall_score = int((0.4 * sharpness + 0.3 * (1.0 - abs(brightness - 0.5) * 2) + 
                      0.2 * min(contrast, 1.0) + 0.1 * (1.0 - noise_level)) * 100)
    
    return {
        "resolution": {
            "width": width,
            "height": height,
            "megapixels": round(image_size / 1000000, 2)
        },
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "noise_level": round(noise_level, 2),
        "overall_score": overall_score,
        "is_acceptable": overall_score >= 50
    }


def enhance_image(image: np.ndarray, sharpness: float = 1.0, brightness: float = 1.0, 
                 contrast: float = 1.0, color: float = 1.0) -> np.ndarray:
    """
    增强图像质量
    
    Args:
        image: 输入图像 (BGR)
        sharpness: 锐度增强系数 (1.0为原始值)
        brightness: 亮度增强系数 (1.0为原始值)
        contrast: 对比度增强系数 (1.0为原始值)
        color: 色彩增强系数 (1.0为原始值)
        
    Returns:
        增强后的图像
    """
    # 转换为RGB (PIL使用RGB格式)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 转换为PIL图像
    pil_image = Image.fromarray(image_rgb)
    
    # 亮度增强
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(brightness)
    
    # 对比度增强
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(contrast)
    
    # 色彩增强
    if color != 1.0:
        enhancer = ImageEnhance.Color(pil_image)
        pil_image = enhancer.enhance(color)
    
    # 锐度增强
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(sharpness)
    
    # 转换回OpenCV格式
    enhanced_rgb = np.array(pil_image)
    enhanced_bgr = cv2.cvtColor(enhanced_rgb, cv2.COLOR_RGB2BGR)
    
    return enhanced_bgr


def auto_enhance_image(image: np.ndarray) -> np.ndarray:
    """
    自动增强图像
    
    根据图像质量评估自动调整亮度、对比度和锐度。
    
    Args:
        image: 输入图像 (BGR)
        
    Returns:
        增强后的图像
    """
    # 获取图像质量指标
    quality = check_image_quality(image)
    
    # 根据亮度调整
    brightness_factor = 1.0
    if quality["brightness"] < 0.3:
        # 图像过暗
        brightness_factor = 1.5
    elif quality["brightness"] > 0.7:
        # 图像过亮
        brightness_factor = 0.7
    
    # 根据对比度调整
    contrast_factor = 1.0
    if quality["contrast"] < 0.3:
        # 对比度过低
        contrast_factor = 1.5
    elif quality["contrast"] > 0.7:
        # 对比度过高
        contrast_factor = 0.8
    
    # 根据锐度调整
    sharpness_factor = 1.0
    if quality["sharpness"] < 0.3:
        # 图像不清晰
        sharpness_factor = 2.0
    
    # 应用增强
    return enhance_image(
        image, 
        sharpness=sharpness_factor,
        brightness=brightness_factor,
        contrast=contrast_factor
    )


def detect_faces(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    检测图像中的人脸
    
    使用OpenCV的Haar级联分类器检测人脸，并返回人脸区域和关键点。
    
    Args:
        image: 输入图像 (BGR)
        
    Returns:
        包含人脸信息的字典列表，每个字典包含：
        - bbox: [x, y, width, height]
        - confidence: 置信度
    """
    # 创建人脸检测器
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    
    # 格式化结果
    results = []
    for i, (x, y, w, h) in enumerate(faces):
        results.append({
            "id": i,
            "bbox": [int(x), int(y), int(w), int(h)],
            "confidence": 0.9  # Haar分类器不提供置信度，使用默认值
        })
    
    return results


def extract_dominant_colors(image: np.ndarray, n_colors: int = 5) -> List[Dict[str, Any]]:
    """
    提取图像中的主要颜色
    
    使用K-means聚类提取图像中的主要颜色。
    
    Args:
        image: 输入图像 (BGR)
        n_colors: 要提取的颜色数量
        
    Returns:
        包含颜色信息的字典列表，每个字典包含：
        - rgb: [r, g, b]
        - hex: 十六进制颜色值
        - percentage: 占比百分比
    """
    # 将图像重塑为像素列表
    pixels = image.reshape(-1, 3).astype(np.float32)
    
    # 将BGR转为RGB
    pixels = pixels[:, ::-1]
    
    # 执行K-means聚类
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # 计算每个聚类的像素数量
    counts = np.bincount(labels.flatten())
    
    # 按像素数量从大到小排序
    indices = np.argsort(counts)[::-1]
    
    # 总像素数
    total_pixels = labels.size
    
    # 构建结果
    colors = []
    for i in indices[:n_colors]:
        center = centers[i]
        rgb = [int(center[0]), int(center[1]), int(center[2])]
        hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
        percentage = (counts[i] / total_pixels) * 100
        
        colors.append({
            "rgb": rgb,
            "hex": hex_color,
            "percentage": round(percentage, 2)
        })
    
    return colors


def create_thumbnail(image: np.ndarray, max_size: int = 200, 
                    quality: int = 80) -> bytes:
    """
    创建缩略图
    
    Args:
        image: 输入图像 (BGR)
        max_size: 缩略图的最大边长
        quality: JPEG质量 (1-100)
        
    Returns:
        缩略图的二进制数据
    """
    # 获取原始图像尺寸
    height, width = image.shape[:2]
    
    # 计算缩放比例
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    # 调整大小
    thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # 编码为JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', thumbnail, encode_param)
    
    return buffer.tobytes()


def normalize_image_for_model(image: np.ndarray, target_size: Tuple[int, int] = (224, 224),
                             mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
                             std: Tuple[float, float, float] = (0.229, 0.224, 0.225)) -> np.ndarray:
    """
    规范化图像用于模型输入
    
    Args:
        image: 输入图像 (BGR)
        target_size: 目标尺寸 (宽度, 高度)
        mean: RGB均值，用于标准化
        std: RGB标准差，用于标准化
        
    Returns:
        规范化后的图像，形状为 (1, C, H, W)，范围为 [-1, 1]
    """
    # 调整大小
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    # BGR转RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # 转换为浮点数并归一化
    rgb = rgb.astype(np.float32) / 255.0
    
    # 标准化
    normalized = (rgb - mean) / std
    
    # 转换为 (C, H, W) 格式
    chw = normalized.transpose(2, 0, 1)
    
    # 添加批次维度 (1, C, H, W)
    batch = np.expand_dims(chw, axis=0)
    
    return batch 