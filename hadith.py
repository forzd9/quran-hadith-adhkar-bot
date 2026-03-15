"""
hadith.py
جلب الأحاديث النبوية من الـ API
"""

import random
from typing import Optional, Dict
from logger import logger
from utils import fetch_with_retry
from cache import cache
from config import HADITH_API_BASE

# قائمة بكتب الحديث المتاحة
HADITH_BOOKS = [
    "bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah",
    "ahmed", "darimi", "malik", "shamail"
]

async def get_random_hadith() -> Optional[Dict]:
    """
    جلب حديث عشوائي من أحد الكتب
    """
    # اختيار كتاب عشوائي
    book = random.choice(HADITH_BOOKS)

    cache_key = f"hadith_{book}_random"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # جلب حديث عشوائي: نطلب الصفحة الأولى ثم نختار حديثاً عشوائياً
    url = f"{HADITH_API_BASE}/books/{book}"
    data = await fetch_with_retry(url)

    if not data or not data.get('data'):
        logger.error(f"Failed to fetch hadith book {book}")
        return None

    # بعض APIs تعيد قائمة بالأحاديث في 'data'
    hadiths = data.get('data', [])
    if not hadiths:
        return None

    # اختيار حديث عشوائي
    hadith = random.choice(hadiths)

    result = {
        'book': book,
        'number': hadith.get('number'),
        'arab': hadith.get('arab'),
        'id': hadith.get('id'),
        'narrator': hadith.get('narrator'),
        'grade': hadith.get('grade', 'لم يذكر')
    }

    # تخزين في cache لمدة ساعة
    cache.set(cache_key, result, ttl=3600)
    return result

def format_hadith(hadith: Dict) -> str:
    """تنسيق نص الحديث للعرض"""
    message = f"📚 *حديث شريف*\n\n"
    message += f"_{hadith['narrator']}_\n\n" if hadith.get('narrator') else ""
    message += f"{hadith['arab']}\n\n"
    message += f"🔍 *الدرجة:* {hadith['grade']}\n"
    message += f"📖 *المصدر:* {hadith['book']} (رقم {hadith['number']})"
    return message