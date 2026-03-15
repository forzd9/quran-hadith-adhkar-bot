"""
utils.py
دوال مساعدة عامة: تنسيق، طلب مع إعادة محاولة، تحقق، إلخ.
"""

import asyncio
import httpx
from typing import Optional, Dict, Any
from logger import logger
from config import REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
import random

async def fetch_with_retry(url: str, params: Dict = None) -> Optional[Dict]:
    """
    إجراء طلب HTTP مع إعادة محاولة تلقائية عند الفشل
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                logger.info(f"API request succeeded: {url}")
                return response.json()
        except Exception as e:
            logger.warning(f"API request failed (attempt {attempt}/{MAX_RETRIES}): {url} - {e}")
            if attempt < MAX_RETRIES:
                wait_time = RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"API request failed after {MAX_RETRIES} attempts: {url}")
                return None

def is_admin(user_id: int) -> bool:
    """التحقق من أن المستخدم هو الأدمن الرئيسي"""
    from config import ADMIN_ID
    return user_id == ADMIN_ID

def escape_markdown(text: str) -> str:
    """تأمين النص لماركداون تليجرام (إذا استخدمنا MarkdownV2)"""
    # نستخدم HTML بدلاً من Markdown لتبسيط الأمور، لكن هذه دالة احتياطية
    import re
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def chunk_text(text: str, max_length: int = 4000) -> list:
    """تقسيم النص الطويل إلى أجزاء مناسبة لتليجرام"""
    lines = text.split('\n')
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + '\n'

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def format_verse_info(surah: int, ayah: int, text: str, tafsir: str = None,
                      reciter_name: str = None, font_style: Dict = None) -> str:
    """تنسيق رسالة الآية بشكل جميل"""
    from fonts import apply_style

    # تطبيق نمط الخط على النص
    styled_text = apply_style(text, font_style) if font_style else text

    message = f"📖 *سورة {get_surah_name(surah)} — الآية {ayah}*\n\n"
    message += f"{styled_text}\n\n"

    if reciter_name:
        message += f"🎧 *القارئ:* {reciter_name}\n"

    if tafsir:
        # اختصار التفسير إذا كان طويلاً
        if len(tafsir) > 500:
            tafsir = tafsir[:500] + "…"
        message += f"\n📜 *تفسير الآية:*\n{tafsir}\n"

    return message

def get_surah_name(surah_number: int) -> str:
    """الحصول على اسم السورة بالعربية"""
    surah_names = {
        1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
        6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
        11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
        16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
        21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
        26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
        31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
        36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
        41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
        46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
        51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
        56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
        61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
        66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
        71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
        76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
        81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
        86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
        91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
        96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
        101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
        106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
        111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
    }
    return surah_names.get(surah_number, f"السورة {surah_number}")
    # ... (باقي الدوال) ...

def format_verse_info(surah: int, ayah: int, text: str, tafsir: str = None,
                      reciter_name: str = None, font_style: Dict = None) -> str:
    """تنسيق رسالة الآية بشكل جميل"""
    from fonts import apply_style

    # تطبيق نمط الخط على النص
    styled_text = apply_style(text, font_style) if font_style else text

    message = f"📖 *سورة {get_surah_name(surah)} — الآية {ayah}*\n\n"
    message += f"{styled_text}\n\n"

    if reciter_name:
        message += f"🎧 *القارئ:* {reciter_name}\n"

    if tafsir:
        # اختصار التفسير إذا كان طويلاً
        if len(tafsir) > 500:
            tafsir = tafsir[:500] + "…"
        message += f"\n📜 *تفسير الآية:*\n{tafsir}\n"

    return message