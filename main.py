#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py
نقطة الدخول الرئيسية للبوت - إعداد وتشغيل التطبيق
"""

import asyncio
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from telegram import Update
from logger import logger
from config import BOT_TOKEN
from database import db
from admin_panel import admin_panel, admin_callback_handler, handle_admin_input
from scheduler import PublishingScheduler
import messages as msg
from utils import is_admin
from quran import get_verse_with_details
from hadith import get_random_hadith, format_hadith
from adhkar import get_random_adhkar, format_adhkar
import fonts
import utils  # تأكد من استيراد utils

# المتغيرات العامة (سيتم تعيينها لاحقاً)
application = None
scheduler = None

async def publish_content(application, content_type: str):
    """
    دالة النشر الأساسية - تستخدم للنشر التلقائي واليدوي
    """
    channels = db.get_active_channels()
    if not channels:
        logger.warning("No channels to publish")
        return

    logger.info(f"Publishing {content_type} to {len(channels)} channels")

    # تجهيز المحتوى حسب النوع
    message_text = ""
    audio_file = None
    parse_mode = 'Markdown'

    if content_type == 'verse':
        verse_data = await get_verse_with_details()
        if verse_data:
            current_font = fonts.get_current_style()
            message_text = utils.format_verse_info(
                verse_data['surah'],
                verse_data['ayah_number'],
                verse_data['text'],
                verse_data.get('tafsir'),
                verse_data.get('reciter_name'),
                current_font
            )
            audio_file = verse_data.get('audio_url')
    elif content_type == 'hadith':
        hadith = await get_random_hadith()
        if hadith:
            message_text = format_hadith(hadith)
    elif content_type == 'adhkar':
        adhkar = await get_random_adhkar()
        if adhkar:
            message_text = format_adhkar(adhkar)
    else:
        # نوع غير معروف
        return

    if not message_text:
        logger.error(f"Failed to generate content for {content_type}")
        return

    # إرسال إلى جميع القنوات
    for channel in channels:
        try:
            if audio_file and content_type == 'verse':
                # نرسل الصوت مع تعليق (caption)
                await application.bot.send_audio(
                    chat_id=channel['chat_id'],
                    audio=audio_file,
                    caption=message_text[:1024],  # حد التسمية التوضيحية
                    parse_mode=parse_mode
                )
            else:
                await application.bot.send_message(
                    chat_id=channel['chat_id'],
                    text=message_text,
                    parse_mode=parse_mode
                )
            db.add_stat(content_type, channel['chat_id'])
            logger.info(f"Published {content_type} to {channel['chat_id']}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel['chat_id']}: {e}")

async def publish_job_callback(context):
    """
    دالة النشر التلقائي - تستدعى من المجدول
    """
    content_type = context.job.data if context.job and context.job.data else 'verse'
    await publish_content(context.application, content_type)

async def start(update: Update, context):
    """معالج أمر /start"""
    user = update.effective_user
    db.update_user(user.id, user.first_name, user.username)
    await update.message.reply_text(msg.START_MESSAGE, parse_mode='Markdown')
    logger.info(f"User {user.id} started the bot")

async def help_command(update: Update, context):
    """معالج أمر /help"""
    await update.message.reply_text(msg.HELP_MESSAGE, parse_mode='Markdown')

async def admin_command(update: Update, context):
    """معالج أمر /admin - يوجه إلى لوحة التحكم"""
    await admin_panel(update, context)

async def error_handler(update: Update, context):
    """معالج الأخطاء العام"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(msg.ERROR_MESSAGE)
    except:
        pass

def main():
    """الدالة الرئيسية لبدء البوت"""
    global application, scheduler

    logger.info("Starting Islamic Bot...")

    # بناء التطبيق
    application = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .concurrent_updates(True) \
        .build()

    # إنشاء المجدول وتمرير job_queue
    scheduler = PublishingScheduler(application.job_queue)
    # تخزين المجدول في bot_data ليتمكن الجميع من الوصول إليه
    application.bot_data['scheduler'] = scheduler
    # تخزين دالة النشر لاستخدامها في admin_panel عند النشر اليدوي
    application.bot_data['publish_func'] = publish_content

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))

    # معالج callback queries (الأزرار)
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^(admin_|publish_|schedule_|reciter_|font_|channel_|del_|manual_)"))

    # معالج الإدخالات النصية للأدمن (إضافة قناة، تغيير إعدادات)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_admin_input
    ))

    # معالج الأخطاء
    application.add_error_handler(error_handler)

    # بدء المجدول إذا كان مفعلاً
    scheduler.schedule()

    logger.info("Bot is polling...")
    application.run_polling()

if __name__ == "__main__":
    main()