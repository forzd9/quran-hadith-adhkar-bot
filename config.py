"""
config.py
إعدادات البوت الرئيسية - جميع الثوابت والإعدادات
"""

# توكن البوت (مقدم من المستخدم)
BOT_TOKEN = "7606145337:AAF8igbcL_zNB4dG7rozpChms2l4N6AfMNQ"

# معرف المطور (الأدمن الرئيسي)
ADMIN_ID = 6891530912

# مسار قاعدة البيانات
DATABASE_PATH = "islamic_bot.db"

# إعدادات السجل
LOG_FILE = "bot.log"
LOG_LEVEL = "INFO"

# واجهات برمجة التطبيقات (APIs)
QURAN_API_BASE = "http://api.alquran.cloud/v1"
HADITH_API_BASE = "https://api.hadith.gading.dev"
TAFSIR_API_BASE = "https://quranenc.com/api/v1/translation"
ADHKAR_API_URL = "https://raw.githubusercontent.com/nawafalqari/azkar-api/main/azkar.json"
QURAN_AUDIO_API = "https://api.quran.com/api/v4"

# قائمة القراء المتاحين (معرفاتهم و أسماؤهم)
RECITERS = {
    "1": {"name": "عبد الباسط عبد الصمد", "id": 1},
    "2": {"name": "مشاري العفاسي", "id": 7},
    "3": {"name": "ماهر المعيقلي", "id": 16},
    "4": {"name": "عبد الرحمن السديس", "id": 2},
    "5": {"name": "سعود الشريم", "id": 3},
    "6": {"name": "محمد صديق المنشاوي", "id": 5},
    "7": {"name": "أحمد العجمي", "id": 8},
    "8": {"name": "أبو بكر الشاطري", "id": 9},
    "9": {"name": "علي الحذيفي", "id": 4},
}

# أنماط خطوط النص (لإضافة زخرفة على نص القرآن)
FONT_STYLES = {
    "1": {"prefix": "﴿ ", "suffix": " ﴾", "name": "قوسين عاديين"},
    "2": {"prefix": "۞ ", "suffix": " ۞", "name": "علامة الحزب"},
    "3": {"prefix": "❖ ", "suffix": " ❖", "name": "معين"},
    "4": {"prefix": "⦗ ", "suffix": " ⦘", "name": "قوسين مربعين"},
    "5": {"prefix": "「 ", "suffix": " 」", "name": "قوسين يابانيين"},
}

# خيارات النشر التلقائي (الافتراضية)
DEFAULT_SCHEDULE_HOUR = 9
DEFAULT_SCHEDULE_MINUTE = 0
DEFAULT_INTERVAL_HOURS = 3

# أنواع المحتوى المدعومة للنشر
CONTENT_TYPES = {
    "verse": "آية + تفسير",
    "hadith": "حديث نبوي",
    "adhkar": "أذكار",
    "quote": "مقولة إسلامية",
}

# إعدادات المهلات وإعادة المحاولة
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2

# إعدادات التخزين المؤقت (Cache)
CACHE_TTL = 3600  # ثانية (ساعة واحدة)