import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp"
UPLOAD_DIR = TEMP_DIR / "uploads"
RESULT_DIR = TEMP_DIR / "results"

# Create directories
TEMP_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# GPU settings
DEVICE_TEXT = "gpu:0"
DEVICE_FORMULA = "gpu"

# OCR settings
DPI = 144  # Resolution for PDF to image conversion

# Translation settings
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-ko"  # MarianMT English to Korean
TRANSLATION_DEVICE = "cuda"  # Use GPU for translation
TRANSLATION_BATCH_SIZE = 8

# File upload settings
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf"}

# Processing settings
CLEANUP_AFTER_HOURS = 24  # Clean up temp files after 24 hours
