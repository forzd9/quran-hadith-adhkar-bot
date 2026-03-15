"""
scheduler.py
إدارة المهام المجدولة للنشر التلقائي باستخدام JobQueue من PTB
"""

from telegram.ext import JobQueue
from telegram.ext import ContextTypes
from logger import logger
from database import db
import random

class PublishingScheduler:
    """فئة إدارة جدولة النشر"""

    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.publish_job = None
        self._load_settings()

    def _load_settings(self):
        """تحميل الإعدادات من قاعدة البيانات"""
        self.enabled = db.get_setting('publishing_enabled') == 'true'
        self.hour = int(db.get_setting('schedule_hour', '9'))
        self.minute = int(db.get_setting('schedule_minute', '0'))
        self.interval = int(db.get_setting('interval_hours', '3'))

    async def publish_content(self, context: ContextTypes.DEFAULT_TYPE):
        """
        دالة النشر التي يستدعيها المجدول
        """
        if not self.enabled:
            logger.info("Publishing is disabled, skipping scheduled job")
            return

        # اختيار نوع المحتوى عشوائياً
        content_type = random.choice(['verse', 'hadith', 'adhkar'])
        logger.info(f"Scheduled publishing {content_type}")

        # استدعاء دالة النشر الرئيسية المخزنة في bot_data
        publish_func = context.application.bot_data.get('publish_func')
        if publish_func:
            await publish_func(context.application, content_type)
        else:
            logger.error("publish_func not found in bot_data")

    def schedule(self):
        """جدولة المهمة حسب الإعدادات"""
        if self.publish_job:
            self.publish_job.schedule_removal()

        if not self.enabled:
            logger.info("Publishing scheduler is disabled")
            return

        # جدولة النشر كل X ساعات
        self.publish_job = self.job_queue.run_repeating(
            self.publish_content,
            interval=self.interval * 3600,  # تحويل الساعات إلى ثواني
            first=10,  # يبدأ بعد 10 ثواني من التشغيل
            name="auto_publish"
        )
        logger.info(f"Scheduled publishing every {self.interval} hours")

    def enable(self):
        """تفعيل النشر التلقائي"""
        self.enabled = True
        db.set_setting('publishing_enabled', 'true')
        self.schedule()
        logger.info("Auto publishing enabled")

    def disable(self):
        """تعطيل النشر التلقائي"""
        self.enabled = False
        db.set_setting('publishing_enabled', 'false')
        if self.publish_job:
            self.publish_job.schedule_removal()
        logger.info("Auto publishing disabled")

    def update_settings(self, hour: int = None, minute: int = None, interval: int = None):
        """تحديث إعدادات الجدولة"""
        if hour is not None:
            self.hour = hour
            db.set_setting('schedule_hour', str(hour))
        if minute is not None:
            self.minute = minute
            db.set_setting('schedule_minute', str(minute))
        if interval is not None:
            self.interval = interval
            db.set_setting('interval_hours', str(interval))

        self.schedule()  # إعادة الجدولة بالإعدادات الجديدة