"""
logger.py
إعداد نظام تسجيل الأحداث (Logging) للبوت
"""

import logging
import sys
from config import LOG_FILE, LOG_LEVEL

def setup_logger():
    """إعداد وإرجاع كائن السجل الرئيسي"""
    # إنشاء المنسق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # معالج الملف
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # معالج الكونسول
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # إعداد الجذر
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger

# إنشاء السجل فوراً للاستخدام في باقي الملفات
logger = setup_logger()