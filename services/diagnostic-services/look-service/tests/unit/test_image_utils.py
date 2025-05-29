"""Tests for image utilities."""

from io import BytesIO

import pytest
from PIL import Image

from look_service.exceptions import ImageProcessingError, ValidationError
from look_service.utils.image_utils import (
    convert_image_format,
    create_thumbnail,
    extract_image_features,
    resize_image,
    validate_image,
)


def test_validate_image_success(sample_image_data):
    """Test successful image validation."""
    result = validate_image(sample_image_data)
    assert result is True


def test_validate_image_empty_data():
    """Test validation with empty data."""
    with pytest.raises(ValidationError, match="Empty image data"):
        validate_image(b"")


def test_validate_image_invalid_format(invalid_image_data):
    """Test validation with invalid image format."""
    with pytest.raises(ImageProcessingError):
        validate_image(invalid_image_data)


def test_validate_image_too_large():
    """Test validation with oversized image."""
    # Create a large image data
    large_data = b"x" * (20 * 1024 * 1024)  # 20MB

    with pytest.raises(ValidationError, match="Image too large"):
        validate_image(large_data, max_size=10 * 1024 * 1024)


def test_resize_image(sample_image_data):
    """Test image resizing."""
    resized_data = resize_image(sample_image_data, (50, 50))

    # Verify the resized image
    with Image.open(BytesIO(resized_data)) as img:
        assert img.size == (50, 50)


def test_resize_image_maintain_aspect_ratio(sample_image_data):
    """Test image resizing with aspect ratio maintained."""
    resized_data = resize_image(
        sample_image_data, (200, 100), maintain_aspect_ratio=True
    )

    # Verify the resized image maintains aspect ratio
    with Image.open(BytesIO(resized_data)) as img:
        # Original is 100x100, so with target 200x100, it should be 100x100 (smaller dimension)
        assert img.size[0] <= 200
        assert img.size[1] <= 100


def test_convert_image_format(sample_image_data):
    """Test image format conversion."""
    png_data = convert_image_format(sample_image_data, "PNG")

    # Verify the converted image
    with Image.open(BytesIO(png_data)) as img:
        assert img.format == "PNG"


def test_extract_image_features(sample_image_data):
    """Test image feature extraction."""
    features = extract_image_features(sample_image_data)

    assert "mean_brightness" in features
    assert "std_brightness" in features
    assert "contrast" in features
    assert "aspect_ratio" in features
    assert "mean_red" in features
    assert "mean_green" in features
    assert "mean_blue" in features

    # Check that values are reasonable
    assert isinstance(features["mean_brightness"], float)
    assert isinstance(features["aspect_ratio"], float)
    assert features["aspect_ratio"] == 1.0  # 100x100 is square


def test_create_thumbnail(sample_image_data):
    """Test thumbnail creation."""
    thumbnail_data = create_thumbnail(sample_image_data, (64, 64))

    # Verify the thumbnail
    with Image.open(BytesIO(thumbnail_data)) as img:
        assert img.size[0] <= 64
        assert img.size[1] <= 64


def test_resize_image_invalid_data():
    """Test resizing with invalid image data."""
    with pytest.raises(ImageProcessingError):
        resize_image(b"invalid", (50, 50))


def test_convert_image_format_invalid_data():
    """Test format conversion with invalid image data."""
    with pytest.raises(ImageProcessingError):
        convert_image_format(b"invalid", "PNG")


def test_extract_image_features_invalid_data():
    """Test feature extraction with invalid image data."""
    with pytest.raises(ImageProcessingError):
        extract_image_features(b"invalid")


def test_create_thumbnail_invalid_data():
    """Test thumbnail creation with invalid image data."""
    with pytest.raises(ImageProcessingError):
        create_thumbnail(b"invalid")
