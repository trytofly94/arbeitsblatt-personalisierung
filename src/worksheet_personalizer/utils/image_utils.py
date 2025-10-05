"""Image processing utilities for worksheet personalization.

This module provides functions for image transformations, scaling, and
text rendering.
"""

import logging
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def cm_to_pixels(cm: float, dpi: int) -> int:
    """Convert centimeters to pixels based on DPI.

    Args:
        cm: Length in centimeters
        dpi: Dots per inch (resolution)

    Returns:
        Length in pixels (rounded to nearest integer)

    Example:
        >>> cm_to_pixels(1.5, 72)  # 1.5 cm at 72 DPI
        42
        >>> cm_to_pixels(1.5, 300)  # 1.5 cm at 300 DPI
        177
    """
    # 1 inch = 2.54 cm
    inches = cm / 2.54
    pixels = int(inches * dpi)
    return pixels


def scale_photo(image: Image.Image, target_size_cm: float, dpi: int) -> Image.Image:
    """Scale a photo to a target size while maintaining aspect ratio.

    The photo is scaled so that its longer side matches the target size.
    The aspect ratio is preserved.

    Args:
        image: PIL Image object to scale
        target_size_cm: Target size for the long side in centimeters
        dpi: Target DPI for conversion

    Returns:
        Scaled PIL Image object

    Example:
        >>> img = Image.open("photo.jpg")  # 1000x800 pixels
        >>> scaled = scale_photo(img, 1.5, 300)
        >>> max(scaled.size)  # Long side should be ~177 pixels
        177
    """
    # Convert target size from cm to pixels
    target_pixels = cm_to_pixels(target_size_cm, dpi)

    # Get current dimensions
    width, height = image.size

    # Determine the long side
    long_side = max(width, height)

    # Calculate scale factor
    scale_factor = target_pixels / long_side

    # Calculate new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize image with high-quality resampling
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    logger.debug(
        f"Scaled image from {width}x{height} to {new_width}x{new_height} "
        f"(target: {target_pixels}px for {target_size_cm}cm at {dpi} DPI)"
    )

    return scaled_image


def render_text_on_image(
    image: Image.Image,
    text: str,
    position: tuple[int, int],
    font_size: int = 12,
    font_path: Optional[Path] = None,
    color: tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Render text on an image.

    Args:
        image: PIL Image object to draw text on
        text: Text string to render
        position: (x, y) coordinates for text position (top-left corner)
        font_size: Font size in points (default: 12)
        font_path: Optional path to TrueType font file. If None, uses default font
        color: RGB color tuple (default: black)

    Returns:
        Image with text rendered (same object as input, modified in-place)

    Example:
        >>> img = Image.open("worksheet.png")
        >>> render_text_on_image(img, "Max Mustermann", (100, 50))
    """
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        if font_path and font_path.exists():
            font = ImageFont.truetype(str(font_path), font_size)
            logger.debug(f"Using custom font: {font_path}")
        else:
            # Try to load a default TrueType font
            try:
                # Common font locations on different systems
                font = ImageFont.truetype("Arial.ttf", font_size)
            except OSError:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except OSError:
                    # Fall back to default bitmap font
                    font = ImageFont.load_default()
                    logger.warning("Using default bitmap font; TrueType font not found")
    except Exception as e:
        logger.warning(f"Error loading font: {e}. Using default font.")
        font = ImageFont.load_default()

    # Draw text
    draw.text(position, text, fill=color, font=font)

    logger.debug(f"Rendered text '{text}' at position {position}")

    return image


def ensure_rgb(image: Image.Image) -> Image.Image:
    """Ensure image is in RGB mode for compositing.

    Converts images with alpha channel (RGBA, LA) or other modes to RGB.

    Args:
        image: PIL Image object

    Returns:
        Image in RGB mode

    Example:
        >>> img = Image.open("photo.png")  # RGBA mode
        >>> rgb_img = ensure_rgb(img)
        >>> rgb_img.mode
        'RGB'
    """
    if image.mode == "RGB":
        return image

    if image.mode in ("RGBA", "LA"):
        # Create white background
        background = Image.new("RGB", image.size, (255, 255, 255))
        # Paste image using alpha channel as mask
        background.paste(image, mask=image.split()[-1])  # Alpha is last channel
        logger.debug(f"Converted {image.mode} to RGB with white background")
        return background

    # For other modes, convert directly
    rgb_image = image.convert("RGB")
    logger.debug(f"Converted {image.mode} to RGB")
    return rgb_image
