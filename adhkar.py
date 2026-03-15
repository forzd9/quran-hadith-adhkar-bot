"""
adhkar.py
جلب الأذكار والأدعية من API
"""

import random
from typing import Optional, Dict, List
from logger import logger
from utils import fetch_with_retry
from cache import cache
from config import ADHKAR_API_URL

async def get_azkar() -> Optional[List]:
    """
    جلب جميع الأذكار من API (تخزين مؤقت طويل المدى)
    """
    cache_key = "all_azkar"
    cached = cache.get(cache_key)
    if cached:
        return cached

    data = await fetch_with_retry(ADHKAR_API_URL)

    if data and isinstance(data, list):
        # تخزين لمدة يوم كامل (نادر التغيير)
        cache.set(cache_key, data, ttl=86400)
        return data

    logger.error("Failed to fetch azkar")
    return None

async def get_random_adhkar() -> Optional[Dict]:
    """
    جلب ذكر عشوائي من الأذكار
    """
    azkar = await get_azkar()
    if not azkar:
        return None

    # اختيار فئة عشوائية (صباح، مساء، نوم، ...)
    category = random.choice(azkar)

    # الفئة تحتوي على 'title' و 'content' (قائمة)
    if not category.get('content'):
        # إذا لم توجد محتويات، نعيد المحاولة
        return await get_random_adhkar()

    # اختيار ذكر عشوائي من المحتوى
    zekr_item = random.choice(category['content'])

    return {
        'category': category.get('title', 'أذكار'),
        'zekr': zekr_item.get('zekr'),
        'count': zekr_item.get('count', 1),
        'description': zekr_item.get('description', '')
    }

def format_adhkar(adhkar: Dict) -> str:
    """تنسيق الذكر للعرض"""
    message = f"🕋 *{adhkar['category']}*\n\n"
    message += f"{adhkar['zekr']}\n\n"
    if adhkar['count'] > 1:
        message += f"🔄 *التكرار:* {adhkar['count']} مرات\n"
    if adhkar['description']:
        message += f"📝 *الفضل:* {adhkar['description']}"
    return message