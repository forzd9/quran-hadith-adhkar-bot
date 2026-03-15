"""
admin_panel.py
لوحة تحكم الأدمن - جميع أوامر الإدارة والتفاعل مع الأزرار
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from logger import logger
from database import db
from config import RECITERS, FONT_STYLES
from utils import is_admin
from keyboards import *
import messages as msg

# حالات المحادثة (لإضافة القنوات)
ADD_CHANNEL = 1

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض لوحة التحكم الرئيسية للأدمن"""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ هذا الأمر مخصص للمشرفين فقط.")
        return

    keyboard = admin_main_keyboard()
    await update.message.reply_text(
        msg.ADMIN_PANEL_WELCOME,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    logger.info(f"Admin panel opened by {user.id}")

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار في لوحة التحكم"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    if not is_admin(user.id):
        await query.edit_message_text("⛔ غير مصرح لك.")
        return

    data = query.data
    logger.info(f"Admin callback: {data} from {user.id}")

    # الحصول على المجدول من bot_data
    scheduler = context.application.bot_data.get('scheduler')

    if data == "admin_start_stop":
        # تفعيل/تعطيل النشر
        enabled = db.get_setting('publishing_enabled') == 'true'
        status = "🟢 مفعل" if enabled else "🔴 معطل"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تفعيل", callback_data="publish_enable"),
             InlineKeyboardButton("❌ تعطيل", callback_data="publish_disable")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]
        ])
        await query.edit_message_text(
            f"حالة النشر التلقائي: {status}\nاختر الإجراء:",
            reply_markup=keyboard
        )

    elif data == "publish_enable":
        if scheduler:
            scheduler.enable()
            await query.edit_message_text("✅ تم تفعيل النشر التلقائي.")
        else:
            await query.edit_message_text("❌ خطأ في المجدول.")

    elif data == "publish_disable":
        if scheduler:
            scheduler.disable()
            await query.edit_message_text("✅ تم تعطيل النشر التلقائي.")
        else:
            await query.edit_message_text("❌ خطأ في المجدول.")

    elif data == "admin_schedule":
        # عرض إعدادات الجدولة
        hour = db.get_setting('schedule_hour', '9')
        minute = db.get_setting('schedule_minute', '0')
        interval = db.get_setting('interval_hours', '3')
        text = f"⏰ الإعدادات الحالية:\n" \
               f"• وقت البدء: {hour}:{minute:02d}\n" \
               f"• التكرار: كل {interval} ساعة"
        keyboard = schedule_settings_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "schedule_set_hour":
        context.user_data['waiting_for'] = 'hour'
        await query.edit_message_text(
            "أرسل الساعة (0-23) بصيغة رقم فقط:",
            reply_markup=back_keyboard()
        )
        return

    elif data == "schedule_set_minute":
        context.user_data['waiting_for'] = 'minute'
        await query.edit_message_text(
            "أرسل الدقيقة (0-59) بصيغة رقم فقط:",
            reply_markup=back_keyboard()
        )
        return

    elif data == "schedule_set_interval":
        context.user_data['waiting_for'] = 'interval'
        await query.edit_message_text(
            "أرسل عدد الساعات بين كل نشر (1-24):",
            reply_markup=back_keyboard()
        )
        return

    elif data == "admin_reciter":
        # اختيار القارئ
        keyboard = reciter_selection_keyboard()
        await query.edit_message_text(
            "🎤 اختر القارئ المفضل:",
            reply_markup=keyboard
        )

    elif data.startswith("reciter_"):
        reciter_key = data.replace("reciter_", "")
        if reciter_key in RECITERS:
            db.set_setting('selected_reciter', reciter_key)
            await query.edit_message_text(
                f"✅ تم اختيار {RECITERS[reciter_key]['name']} كقارئ افتراضي."
            )

    elif data == "admin_font":
        # تغيير نمط الخط
        keyboard = font_style_keyboard()
        await query.edit_message_text(
            "🖋️ اختر نمط الخط للنص القرآني:",
            reply_markup=keyboard
        )

    elif data.startswith("font_"):
        style_key = data.replace("font_", "")
        from fonts import set_font_style
        if set_font_style(style_key):
            await query.edit_message_text(
                f"✅ تم تغيير نمط الخط إلى: {FONT_STYLES[style_key]['name']}"
            )

    elif data == "admin_channels":
        # إدارة القنوات
        channels = db.get_active_channels()
        text = f"📢 القنوات النشطة ({len(channels)}):\n\n"
        if channels:
            for i, ch in enumerate(channels, 1):
                text += f"{i}. {ch['chat_title']} (ID: {ch['chat_id']})\n"
        else:
            text += "لا توجد قنوات مضافة بعد."

        keyboard = channels_management_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "channel_add":
        context.user_data['waiting_for'] = 'channel_id'
        await query.edit_message_text(
            "📌 أرسل معرف القناة (مثال: @channel_username) أو ID الرقمي.\n"
            "تأكد من إضافة البوت كمشرف في القناة.",
            reply_markup=back_keyboard()
        )
        return

    elif data == "channel_remove":
        # عرض قائمة القنوات للحذف
        channels = db.get_active_channels()
        if not channels:
            await query.edit_message_text("لا توجد قنوات لإزالتها.", reply_markup=back_keyboard())
            return
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(ch['chat_title'][:20], callback_data=f"del_{ch['chat_id']}")]
            for ch in channels
        ] + [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_channels")]])
        await query.edit_message_text("اختر القناة لإزالتها:", reply_markup=keyboard)

    elif data.startswith("del_"):
        chat_id = int(data.replace("del_", ""))
        db.remove_channel(chat_id)
        await query.edit_message_text("✅ تم إزالة القناة.", reply_markup=back_keyboard())

    elif data == "admin_stats":
        stats = db.get_stats_summary()
        text = f"📊 *إحصائيات البوت*\n\n"
        text += f"👥 المستخدمون: {stats['users']}\n"
        text += f"📢 القنوات: {stats['channels']}\n"
        text += f"📨 إجمالي الرسائل: {stats['total']}\n"
        text += f"📨 آخر 24 ساعة: {stats['last_24h']}\n\n"
        text += "*حسب النوع:*\n"
        for ct, count in stats['by_type'].items():
            text += f"• {ct}: {count}\n"
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=back_keyboard())

    elif data == "admin_manual":
        # نشر يدوي
        keyboard = manual_publish_keyboard()
        await query.edit_message_text(
            "📤 اختر نوع المحتوى للنشر اليدوي:",
            reply_markup=keyboard
        )

    elif data.startswith("manual_"):
        content_type = data.replace("manual_", "")
        # الحصول على دالة النشر من bot_data
        publish_func = context.application.bot_data.get('publish_func')
        if publish_func:
            await publish_func(context.application, content_type)
            await query.edit_message_text(f"✅ تم نشر {content_type} في جميع القنوات النشطة.")
        else:
            await query.edit_message_text("❌ خطأ في دالة النشر.")

    elif data == "admin_back":
        await query.edit_message_text(
            msg.ADMIN_PANEL_WELCOME,
            reply_markup=admin_main_keyboard(),
            parse_mode='Markdown'
        )

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الإدخالات النصية من الأدمن (إضافة قناة، تغيير إعدادات)"""
    user = update.effective_user
    if not is_admin(user.id):
        return

    waiting = context.user_data.get('waiting_for')
    if not waiting:
        return

    text = update.message.text.strip()
    scheduler = context.application.bot_data.get('scheduler')

    if waiting == 'hour':
        if text.isdigit() and 0 <= int(text) <= 23:
            db.set_setting('schedule_hour', text)
            if scheduler:
                scheduler.update_settings(hour=int(text))
            await update.message.reply_text(f"✅ تم تعيين الساعة إلى {text}.")
        else:
            await update.message.reply_text("❌ قيمة غير صالحة. يجب أن تكون رقم بين 0 و 23.")

    elif waiting == 'minute':
        if text.isdigit() and 0 <= int(text) <= 59:
            db.set_setting('schedule_minute', text)
            if scheduler:
                scheduler.update_settings(minute=int(text))
            await update.message.reply_text(f"✅ تم تعيين الدقيقة إلى {text}.")
        else:
            await update.message.reply_text("❌ قيمة غير صالحة. يجب أن تكون رقم بين 0 و 59.")

    elif waiting == 'interval':
        if text.isdigit() and 1 <= int(text) <= 24:
            db.set_setting('interval_hours', text)
            if scheduler:
                scheduler.update_settings(interval=int(text))
            await update.message.reply_text(f"✅ تم تعيين التكرار إلى كل {text} ساعة.")
        else:
            await update.message.reply_text("❌ قيمة غير صالحة. يجب أن تكون رقم بين 1 و 24.")

    elif waiting == 'channel_id':
        # محاولة إضافة القناة
        chat_id = text
        if text.startswith('@'):
            try:
                chat = await context.bot.get_chat(text)
                chat_id = chat.id
                title = chat.title
            except Exception as e:
                await update.message.reply_text(f"❌ لا يمكن العثور على القناة: {e}")
                context.user_data.pop('waiting_for', None)
                return
        else:
            try:
                chat_id = int(text)
                chat = await context.bot.get_chat(chat_id)
                title = chat.title
            except:
                await update.message.reply_text("❌ معرف غير صالح. تأكد من صحة ID.")
                context.user_data.pop('waiting_for', None)
                return

        db.add_channel(chat_id, title, chat.type, user.id)
        await update.message.reply_text(f"✅ تم إضافة القناة {title} بنجاح.")

    context.user_data.pop('waiting_for', None)