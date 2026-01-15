"""Tests for image processing functionality."""
from django.test import TestCase
from unittest.mock import patch
from io import BytesIO
import base64
from PIL import Image

from ..weaviate import (
    resize_image_if_needed,
    WeaviateImageError,
)


class ResizeImageIfNeededTests(TestCase):
    def _make_base64_image(self, size=(200, 200), mode="RGBA", format="PNG"):
        img = Image.new(mode, size, color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode(), img_bytes, img.size

    def test_shrinks_and_converts_to_rgb_with_min_dimension_clamp(self):
        # Create a larger image that can actually be shrunk
        b64_image, img_bytes, original_size = self._make_base64_image(size=(2000, 2000))
        # Set a very small max size to force shrinking
        max_size_mb = 0.01  # 10KB - very small to force resize

        result = resize_image_if_needed(b64_image, max_size_mb=max_size_mb)

        decoded = base64.b64decode(result)
        # Result should be smaller than or equal to max_size_mb
        self.assertLessEqual(len(decoded), int(max_size_mb * 1024 * 1024))

        with Image.open(BytesIO(decoded)) as img:
            self.assertEqual(img.mode, "RGB")  # alpha removed
            self.assertGreater(img.width, 0)
            self.assertGreater(img.height, 0)
            self.assertLessEqual(img.width, original_size[0])
            self.assertLessEqual(img.height, original_size[1])

    def test_decompression_bomb_guard_raises(self):
        b64_image, img_bytes, _ = self._make_base64_image(size=(100, 100))
        max_size_mb = (len(img_bytes) / (1024 * 1024)) * 0.5  # ensure processing

        with patch('artists.weaviate.service.MAX_IMAGE_PIXELS', 10):
            with self.assertRaises(WeaviateImageError):
                resize_image_if_needed(b64_image, max_size_mb=max_size_mb)
