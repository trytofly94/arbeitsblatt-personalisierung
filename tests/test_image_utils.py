"""Tests for image processing utilities."""

from PIL import Image

from worksheet_personalizer.utils.image_utils import (
    cm_to_pixels,
    ensure_rgb,
    render_text_on_image,
    scale_photo,
)


def test_cm_to_pixels_at_72_dpi() -> None:
    """Test centimeter to pixel conversion at 72 DPI."""
    # 1.5 cm at 72 DPI
    result = cm_to_pixels(1.5, 72)

    # 1.5 cm = 0.59 inches, 0.59 * 72 ≈ 42 pixels
    assert result == 42


def test_cm_to_pixels_at_300_dpi() -> None:
    """Test centimeter to pixel conversion at 300 DPI."""
    # 1.5 cm at 300 DPI
    result = cm_to_pixels(1.5, 300)

    # 1.5 cm = 0.59 inches, 0.59 * 300 ≈ 177 pixels
    assert result == 177


def test_scale_photo_landscape() -> None:
    """Test scaling a landscape photo (width > height)."""
    # Create a 1000x600 pixel image
    img = Image.new("RGB", (1000, 600), color="blue")

    # Scale to 1.5 cm at 300 DPI (≈177 pixels long side)
    scaled = scale_photo(img, 1.5, 300)

    # Check that long side (width) is approximately 177 pixels
    assert max(scaled.size) == 177
    assert scaled.size[0] == 177  # Width is long side

    # Check aspect ratio is preserved
    original_ratio = 1000 / 600
    scaled_ratio = scaled.size[0] / scaled.size[1]
    assert abs(original_ratio - scaled_ratio) < 0.01


def test_scale_photo_portrait() -> None:
    """Test scaling a portrait photo (height > width)."""
    # Create a 600x1000 pixel image
    img = Image.new("RGB", (600, 1000), color="red")

    # Scale to 1.5 cm at 300 DPI
    scaled = scale_photo(img, 1.5, 300)

    # Check that long side (height) is approximately 177 pixels
    assert max(scaled.size) == 177
    assert scaled.size[1] == 177  # Height is long side

    # Check aspect ratio is preserved
    original_ratio = 600 / 1000
    scaled_ratio = scaled.size[0] / scaled.size[1]
    assert abs(original_ratio - scaled_ratio) < 0.01


def test_render_text_on_image() -> None:
    """Test rendering text on an image."""
    img = Image.new("RGB", (400, 300), color="white")

    # Render text
    result = render_text_on_image(img, "Test Text", (50, 50), font_size=20)

    # Check that the same image object is returned (modified in-place)
    assert result is img

    # Check that image is not all white anymore (text was added)
    pixels = list(img.getdata())
    assert not all(p == (255, 255, 255) for p in pixels)


def test_ensure_rgb_already_rgb() -> None:
    """Test ensure_rgb with already RGB image."""
    img = Image.new("RGB", (100, 100), color="red")

    result = ensure_rgb(img)

    assert result.mode == "RGB"
    assert result is img  # Should return same object


def test_ensure_rgb_rgba_conversion() -> None:
    """Test ensure_rgb converts RGBA to RGB."""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))

    result = ensure_rgb(img)

    assert result.mode == "RGB"
    assert result.size == img.size


def test_ensure_rgb_grayscale_conversion() -> None:
    """Test ensure_rgb converts grayscale to RGB."""
    img = Image.new("L", (100, 100), color=128)

    result = ensure_rgb(img)

    assert result.mode == "RGB"
    assert result.size == img.size
