"""Image processing utilities."""

from io import BytesIO

from PIL import Image

from ..core.config import settings
from ..core.logging import get_logger
from ..exceptions import ImageProcessingError, ValidationError

logger = get_logger(__name__)

def validate_image(
    image_data: bytes,
    max_size: int | None = None,
    allowed_formats: list[str] | None = None,
) -> bool:
    """Validate image data.

    Args:
        image_data: Raw image bytes
        max_size: Maximum file size in bytes
        allowed_formats: List of allowed image formats

    Returns:
        True if image is valid

    Raises:
        ValidationError: If image validation fails
    """
    if not image_data:
        raise ValidationError("Empty image data")

    # Check file size
    max_size = max_size or settings.max_file_size
    if len(image_data) > max_size:
        raise ValidationError(
            f"Image too large: {len(image_data)} bytes (max: {max_size})"
        )

    try:
        # Try to open image with PIL
        with Image.open(BytesIO(image_data)) as img:
            # Check format
            allowed_formats = allowed_formats or settings.allowed_extensions
            # Convert both to lowercase for comparison
            allowed_formats_lower = [fmt.lower() for fmt in allowed_formats]
            if img.format and img.format.lower() not in allowed_formats_lower:
                raise ValidationError(f"Unsupported image format: {img.format}")

            # Check image dimensions
            width, height = img.size
            if width < 32 or height < 32:
                raise ValidationError("Image too small (minimum 32x32 pixels)")

            if width > 4096 or height > 4096:
                raise ValidationError("Image too large (maximum 4096x4096 pixels)")

            logger.debug(
                "Image validated",
                format=img.format,
                size=f"{width}x{height}",
                mode=img.mode,
            )

            return True

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ImageProcessingError(f"Failed to validate image: {str(e)}")

def resize_image(
    image_data: bytes,
    target_size: tuple[int, int],
    maintain_aspect_ratio: bool = True,
) -> bytes:
    """Resize image to target size.

    Args:
        image_data: Raw image bytes
        target_size: Target (width, height)
        maintain_aspect_ratio: Whether to maintain aspect ratio

    Returns:
        Resized image bytes

    Raises:
        ImageProcessingError: If resize fails
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            original_size = img.size

            if maintain_aspect_ratio:
                # Calculate new size maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                new_size = img.size
            else:
                # Resize to exact dimensions
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                new_size = target_size

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Save to bytes
            output = BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)

            logger.debug(
                "Image resized",
                original_size=f"{original_size[0]}x{original_size[1]}",
                new_size=f"{new_size[0]}x{new_size[1]}",
            )

            return output.getvalue()

    except Exception as e:
        raise ImageProcessingError(f"Failed to resize image: {str(e)}")

def convert_image_format(
    image_data: bytes,
    target_format: str = "JPEG",
    quality: int = 85,
) -> bytes:
    """Convert image to target format.

    Args:
        image_data: Raw image bytes
        target_format: Target format (JPEG, PNG, etc.)
        quality: JPEG quality (1-100)

    Returns:
        Converted image bytes

    Raises:
        ImageProcessingError: If conversion fails
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Convert to RGB for JPEG
            if target_format.upper() == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Save to bytes
            output = BytesIO()
            save_kwargs = {"format": target_format, "optimize": True}

            if target_format.upper() == "JPEG":
                save_kwargs["quality"] = quality

            img.save(output, **save_kwargs)

            logger.debug(
                "Image format converted",
                original_format=img.format,
                target_format=target_format,
                size=f"{img.size[0]}x{img.size[1]}",
            )

            return output.getvalue()

    except Exception as e:
        raise ImageProcessingError(f"Failed to convert image format: {str(e)}")

def extract_image_features(image_data: bytes) -> dict[str, float]:
    """Extract basic image features.

    Args:
        image_data: Raw image bytes

    Returns:
        Dictionary of image features

    Raises:
        ImageProcessingError: If feature extraction fails
    """
    try:
        # Open image
        image = Image.open(BytesIO(image_data))

        # Convert to numpy array
        img_array = np.array(image)

        # Calculate basic features
        features = {
            "mean_brightness": float(np.mean(img_array)),
            "std_brightness": float(np.std(img_array)),
            "contrast": float(np.std(img_array) / np.mean(img_array)) if np.mean(img_array) > 0 else 0.0,
            "aspect_ratio": float(image.width / image.height),
        }

        # Add color features if RGB
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            features.update({
                "mean_red": float(np.mean(img_array[:, :, 0])),
                "mean_green": float(np.mean(img_array[:, :, 1])),
                "mean_blue": float(np.mean(img_array[:, :, 2])),
            })

        logger.debug("Image features extracted", features=features)
        return features

    except Exception as e:
        logger.error("Failed to extract image features", error=str(e))
        raise ImageProcessingError(f"Feature extraction failed: {e}") from e

def create_thumbnail(
    image_data: bytes,
    size: tuple[int, int] = (128, 128),
) -> bytes:
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
            img.save(output, format="JPEG", quality=80, optimize=True)

            logger.debug(
                "Thumbnail created",
                original_size=f"{img.size[0]}x{img.size[1]}",
                thumbnail_size=f"{size[0]}x{size[1]}",
            )

            return output.getvalue()

    except Exception as e:
        raise ImageProcessingError(f"Failed to create thumbnail: {str(e)}")
