"""
fonts.py
تطبيق أنماط الخطوط المختلفة على النص القرآني
"""

from config import FONT_STYLES
from database import db

def get_current_style() -> dict:
    """الحصول على نمط الخط الحالي من قاعدة البيانات"""
    style_key = db.get_setting('font_style', '1')
    return FONT_STYLES.get(style_key, FONT_STYLES['1'])

def apply_style(text: str, style: dict = None) -> str:
    """
    تطبيق نمط معين على النص
    إذا لم يُمرر نمط، يستخدم النمط الحالي من قاعدة البيانات
    """
    if style is None:
        style = get_current_style()

    return f"{style['prefix']}{text}{style['suffix']}"

def get_styles_list() -> list:
    """إرجاع قائمة الأنماط لعرضها في لوحة التحكم"""
    return [(key, style['name']) for key, style in FONT_STYLES.items()]

def set_font_style(style_key: str) -> bool:
    """تغيير نمط الخط"""
    if style_key in FONT_STYLES:
        db.set_setting('font_style', style_key)
        return True
    return False