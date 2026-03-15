"""
keyboards.py
إنشاء لوحات المفاتيح المضمنة (Inline Keyboards) المستخدمة في البوت
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import RECITERS, FONT_STYLES, CONTENT_TYPES

def admin_main_keyboard():
    """لوحة التحكم الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("▶️ تشغيل/إيقاف النشر", callback_data="admin_start_stop")],
        [InlineKeyboardButton("⏰ ضبط الجدولة", callback_data="admin_schedule")],
        [InlineKeyboardButton("🎤 اختيار قارئ", callback_data="admin_reciter")],
        [InlineKeyboardButton("🖋️ تغيير نمط الخط", callback_data="admin_font")],
        [InlineKeyboardButton("📢 إدارة القنوات", callback_data="admin_channels")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📤 نشر يدوي", callback_data="admin_manual")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    """زر رجوع فقط"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    return InlineKeyboardMarkup(keyboard)

def schedule_settings_keyboard():
    """إعدادات الجدولة"""
    keyboard = [
        [InlineKeyboardButton("🕐 تعيين الساعة", callback_data="schedule_set_hour")],
        [InlineKeyboardButton("🕐 تعيين الدقيقة", callback_data="schedule_set_minute")],
        [InlineKeyboardButton("⏱️ تعيين التكرار (ساعات)", callback_data="schedule_set_interval")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def reciter_selection_keyboard():
    """اختيار القارئ"""
    buttons = []
    for key, reciter in RECITERS.items():
        buttons.append([InlineKeyboardButton(reciter['name'], callback_data=f"reciter_{key}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(buttons)

def font_style_keyboard():
    """اختيار نمط الخط"""
    buttons = []
    for key, style in FONT_STYLES.items():
        # نعرض مثالاً مصغراً
        example = f"{style['prefix']}نص تجريبي{style['suffix']}"
        buttons.append([InlineKeyboardButton(style['name'], callback_data=f"font_{key}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(buttons)

def channels_management_keyboard():
    """إدارة القنوات"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="channel_add")],
        [InlineKeyboardButton("➖ إزالة قناة", callback_data="channel_remove")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def manual_publish_keyboard():
    """نشر يدوي - اختيار نوع المحتوى"""
    buttons = []
    for key, name in CONTENT_TYPES.items():
        buttons.append([InlineKeyboardButton(name, callback_data=f"manual_{key}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(buttons)