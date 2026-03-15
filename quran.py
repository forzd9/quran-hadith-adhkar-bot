"""
quran.py
جلب آيات القرآن، التفسير، والتلاوات الصوتية من الـ APIs
"""

from typing import Optional, Dict, Tuple
from logger import logger
from utils import fetch_with_retry
from cache import cache
from config import QURAN_API_BASE, TAFSIR_API_BASE, QURAN_AUDIO_API, RECITERS

async def get_random_verse() -> Optional[Dict]:
    """
    جلب آية عشوائية من القرآن
    """
    # نستخدم cache للتقليل من الطلبات المتكررة
    cache_key = "random_verse"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # جلب سورة عشوائية (1-114)
    import random
    surah = random.randint(1, 114)

    # جلب معلومات السورة
    url = f"{QURAN_API_BASE}/surah/{surah}/ar.alafasy"
    data = await fetch_with_retry(url)

    if not data or not data.get('data'):
        logger.error(f"Failed to fetch surah {surah}")
        return None

    surah_data = data['data']
    ayahs = surah_data.get('ayahs', [])

    if not ayahs:
        return None

    # اختيار آية عشوائية من السورة
    ayah = random.choice(ayahs)

    result = {
        'surah': surah,
        'surah_name': surah_data.get('name'),
        'ayah_number': ayah.get('numberInSurah'),
        'text': ayah.get('text'),
        'juz': ayah.get('juz'),
        'page': ayah.get('page')
    }

    # تخزين في cache لمدة ساعة
    cache.set(cache_key, result, ttl=3600)
    return result

async def get_tafsir(surah: int, ayah: int) -> Optional[str]:
    """
    جلب تفسير آية معينة
    نستخدم quranenc API للتفسير الميسر
    """
    cache_key = f"tafsir_{surah}_{ayah}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    url = f"{TAFSIR_API_BASE}/sura/ar_muyassar/{surah}"
    data = await fetch_with_retry(url)

    if data and data.get('result'):
        # البحث عن الآية المطلوبة في النتائج
        for item in data['result']:
            if item.get('aya') == ayah:
                tafsir = item.get('translation')
                cache.set(cache_key, tafsir, ttl=86400)  # 24 ساعة
                return tafsir

    logger.warning(f"No tafsir found for {surah}:{ayah}")
    return "لم نتمكن من جلب التفسير حالياً."

async def get_audio_url(surah: int, reciter_id: int) -> Optional[str]:
    """
    الحصول على رابط التلاوة لسورة معينة من قارئ معين
    """
    cache_key = f"audio_{reciter_id}_{surah}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # استخدام api.quran.com
    url = f"{QURAN_AUDIO_API}/chapter_recitations/{reciter_id}/{surah}"
    data = await fetch_with_retry(url)

    if data and data.get('audio_file'):
        audio_url = data['audio_file'].get('audio_url')
        if audio_url:
            cache.set(cache_key, audio_url, ttl=86400)  # 24 ساعة
            return audio_url

    logger.warning(f"No audio for reciter {reciter_id}, surah {surah}")
    return None

async def get_verse_with_details() -> Optional[Dict]:
    """
    جلب آية مع تفاصيلها (نص + تفسير + صوت)
    """
    verse = await get_random_verse()
    if not verse:
        return None

    surah = verse['surah']
    ayah = verse['ayah_number']

    # جلب التفسير
    tafsir = await get_tafsir(surah, ayah)

    # جلب معلومات القارئ المختار
    reciter_key = db.get_setting('selected_reciter', '1')
    reciter = RECITERS.get(reciter_key, RECITERS['1'])

    # جلب رابط التلاوة
    audio_url = await get_audio_url(surah, reciter['id'])

    return {
        **verse,
        'tafsir': tafsir,
        'reciter_name': reciter['name'],
        'audio_url': audio_url
    }