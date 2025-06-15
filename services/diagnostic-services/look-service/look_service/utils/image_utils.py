from typing import Dict, List, Any, Optional, Union, Tuple

"""
image_utils - 索克生活项目模块
"""

from ..core.config import settings
from ..core.logging import get_logger
from ..exceptions import ImageProcessingError, ValidationError
from PIL import Image
from io import BytesIO

import numpy as np

"""Image processing utilities."""

logger = get_logger(__name__)

def validate_image(
    image_data: bytes,
    max_size: Optional[int] = None,
    allowed_formats: Optional[List[str]] = None,
) -> bool:
    """验证图像数据
    
    Args:
        image_data: 原始图像字节数据
        max_size: 最大文件大小（字节）
        allowed_formats: 允许的图像格式列表
        
    Returns:
        如果图像有效则返回True
        
    Raises:
        ValidationError: 如果图像验证失败
    """
    if not image_data:
        raise ValidationError("图像数据为空")

    # 检查文件大小
    max_size = max_size or settings.max_file_size
    if len(image_data) > max_size:
        raise ValidationError(
            f"图像过大: {len(image_data)} 字节 (最大: {max_size})"
        )

    try:
        # 尝试用PIL打开图像
        with Image.open(BytesIO(image_data)) as img:
            # 检查格式
            allowed_formats = allowed_formats or settings.allowed_extensions
            # 转换为小写进行比较
            allowed_formats_lower = [fmt.lower() for fmt in allowed_formats]
            if img.format and img.format.lower() not in allowed_formats_lower:
                raise ValidationError(f"不支持的图像格式: {img.format}")

            # 检查图像尺寸
            width, height = img.size
            if width < 32 or height < 32:
                raise ValidationError("图像过小 (最小 32x32 像素)")

            if width > 4096 or height > 4096:
                raise ValidationError("图像过大 (最大 4096x4096 像素)")

            logger.debug(
                "图像验证通过",
                format=img.format,
                size=f"{width}x{height}",
                mode=img.mode,
            )

            return True

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ImageProcessingError(f"图像验证失败: {str(e)}")

def resize_image(
    image: Union[Image.Image, bytes],
    max_size: int = 1024,
    maintain_aspect_ratio: bool = True,
) -> Image.Image:
    """调整图像大小
    
    Args:
        image: PIL图像对象或字节数据
        max_size: 最大尺寸
        maintain_aspect_ratio: 是否保持宽高比
        
    Returns:
        调整大小后的PIL图像对象
        
    Raises:
        ImageProcessingError: 如果调整大小失败
    """
    try:
        # 如果输入是字节数据，先转换为PIL图像
        if isinstance(image, bytes):
            image = Image.open(BytesIO(image))
        
        original_size = image.size
        
        if maintain_aspect_ratio:
            # 计算新尺寸，保持宽高比
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            new_size = image.size
        else:
            # 调整到确切尺寸
            image = image.resize((max_size, max_size), Image.Resampling.LANCZOS)
            new_size = (max_size, max_size)

        # 如果需要，转换为RGB
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        logger.debug(
            "图像大小已调整",
            original_size=f"{original_size[0]}x{original_size[1]}",
            new_size=f"{new_size[0]}x{new_size[1]}",
        )

        return image

    except Exception as e:
        raise ImageProcessingError(f"调整图像大小失败: {str(e)}")

def convert_image_format(
    image_data: bytes,
    target_format: str = "JPEG",
    quality: int = 85,
) -> bytes:
    """转换图像格式
    
    Args:
        image_data: 原始图像字节数据
        target_format: 目标格式 (JPEG, PNG等)
        quality: JPEG质量 (1-100)
        
    Returns:
        转换后的图像字节数据
        
    Raises:
        ImageProcessingError: 如果转换失败
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            # 为JPEG转换为RGB
            if target_format.upper() == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # 保存为字节
            output = BytesIO()
            save_kwargs = {"format": target_format, "optimize": True}

            if target_format.upper() == "JPEG":
                save_kwargs["quality"] = quality

            img.save(output, **save_kwargs)

            logger.debug(
                "图像格式已转换",
                original_format=img.format,
                target_format=target_format,
                size=f"{img.size[0]}x{img.size[1]}",
            )

            return output.getvalue()

    except Exception as e:
        raise ImageProcessingError(f"转换图像格式失败: {str(e)}")

def extract_image_features(image_data: bytes) -> Dict[str, float]:
    """提取基本图像特征
    
    Args:
        image_data: 原始图像字节数据
        
    Returns:
        图像特征字典
        
    Raises:
        ImageProcessingError: 如果特征提取失败
    """
    try:
        # 打开图像
        image = Image.open(BytesIO(image_data))

        # 转换为numpy数组
        img_array = np.array(image)

        # 计算基本特征
        features = {
            "mean_brightness": float(np.mean(img_array)),
            "std_brightness": float(np.std(img_array)),
            "contrast": float(np.std(img_array) / np.mean(img_array)) if np.mean(img_array) > 0 else 0.0,
            "aspect_ratio": float(image.width / image.height),
            "width": float(image.width),
            "height": float(image.height),
            "channels": len(img_array.shape) if len(img_array.shape) > 2 else 1,
        }

        # 如果是彩色图像，计算颜色特征
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            features.update({
                "mean_red": float(np.mean(img_array[:, :, 0])),
                "mean_green": float(np.mean(img_array[:, :, 1])),
                "mean_blue": float(np.mean(img_array[:, :, 2])),
            })

        logger.debug("图像特征提取完成", features=features)
        return features

    except Exception as e:
        raise ImageProcessingError(f"提取图像特征失败: {str(e)}")

def create_thumbnail(
    image_data: bytes,
    size: tuple[int, int] = (128, 128),
) - > bytes:
    """Create thumbnail from image.

    Args:
        image_data: Raw image bytes
        size: Thumbnail size

    Returns:
        Thumbnail image bytes

    Raises:
        ImageProcessingError: If thumbnail creation fails
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Save to bytes
            output = BytesIO()
            img.save(output, format = "JPEG", quality = 80, optimize = True)

            logger.debug(
                "Thumbnail created",
                original_size = f"{img.size[0]}x{img.size[1]}",
                thumbnail_size = f"{size[0]}x{size[1]}",
            )

            return output.getvalue()

    except Exception as e:
        raise ImageProcessingError(f"Failed to create thumbnail: {str(e)}")

def preprocess_image_for_ml(
    image_data: bytes,
    target_size: Tuple[int, int] = (224, 224),
    normalize: bool = True,
) -> np.ndarray:
    """为机器学习预处理图像
    
    Args:
        image_data: 原始图像字节数据
        target_size: 目标尺寸 (width, height)
        normalize: 是否归一化像素值
        
    Returns:
        预处理后的numpy数组
        
    Raises:
        ImageProcessingError: 如果预处理失败
    """
    try:
        # 打开并转换图像
        with Image.open(BytesIO(image_data)) as img:
            # 转换为RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # 转换为numpy数组
            img_array = np.array(img, dtype=np.float32)
            
            # 归一化
            if normalize:
                img_array = img_array / 255.0
            
            logger.debug(
                "图像预处理完成",
                shape=img_array.shape,
                dtype=str(img_array.dtype),
                min_val=float(np.min(img_array)),
                max_val=float(np.max(img_array)),
            )
            
            return img_array

    except Exception as e:
        raise ImageProcessingError(f"图像预处理失败: {str(e)}")

def detect_image_quality(image_data: bytes) -> Dict[str, Any]:
    """检测图像质量
    
    Args:
        image_data: 原始图像字节数据
        
    Returns:
        图像质量评估结果
        
    Raises:
        ImageProcessingError: 如果质量检测失败
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            img_array = np.array(img)
            
            # 计算质量指标
            quality_metrics = {
                "sharpness": _calculate_sharpness(img_array),
                "brightness": _calculate_brightness(img_array),
                "contrast": _calculate_contrast(img_array),
                "noise_level": _estimate_noise_level(img_array),
                "overall_quality": "good",  # 简化的质量评估
            }
            
            # 基于指标评估整体质量
            if quality_metrics["sharpness"] < 0.1:
                quality_metrics["overall_quality"] = "poor"
            elif quality_metrics["contrast"] < 0.2:
                quality_metrics["overall_quality"] = "fair"
            
            logger.debug("图像质量检测完成", metrics=quality_metrics)
            return quality_metrics

    except Exception as e:
        raise ImageProcessingError(f"图像质量检测失败: {str(e)}")

def _calculate_sharpness(img_array: np.ndarray) -> float:
    """计算图像锐度"""
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array
    
    # 使用Laplacian算子计算锐度
    laplacian = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
    convolved = np.abs(np.convolve(gray.flatten(), laplacian.flatten(), mode='same'))
    return float(np.mean(convolved))

def _calculate_brightness(img_array: np.ndarray) -> float:
    """计算图像亮度"""
    return float(np.mean(img_array) / 255.0)

def _calculate_contrast(img_array: np.ndarray) -> float:
    """计算图像对比度"""
    return float(np.std(img_array) / 255.0)

def _estimate_noise_level(img_array: np.ndarray) -> float:
    """估计图像噪声水平"""
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array
    
    # 简单的噪声估计
    noise = np.std(gray - np.mean(gray))
    return float(noise / 255.0)
