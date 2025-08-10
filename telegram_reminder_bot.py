#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 提醒机器人
功能：自动解析用户输入的时间+事件文本，在指定时间发送提醒
"""

import os
import logging
import asyncio
import re
import threading
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict
import json

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

import dateparser
from dateparser.search import search_dates
import tzlocal
from flask import Flask

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramReminderBot:
    def __init__(self, token: str):
        """初始化机器人"""
        self.token = token
        self.bot = Bot(token=token)
        # 使用简单的Application初始化方式
        self.application = Application.builder().token(token).build()
        
        # 初始化调度器
        jobstores = {'default': MemoryJobStore()}
        executors = {'default': AsyncIOExecutor()}
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 10  # 容忍±10秒误差
        }
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=str(tzlocal.get_localzone())
        )
        
        # 存储用户提醒数据
        self.user_reminders: Dict[int, List[Dict]] = {}
        
        # 注册处理器
        self._register_handlers()
        
    def _register_handlers(self):
        """注册消息处理器"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_reminder))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        help_text = """
🤖 *欢迎使用Telegram提醒机器人！*

📝 *使用方法：*
直接发送「时间 + 事件」消息，我会在指定时间提醒你！

⏰ *支持的时间格式：*
• 绝对时间：`2025-01-15 14:30` 或 `14:30`
• 相对时间：`1小时后` `明天上午9点` `下周一15:00`
• 天级提醒：`五天后` `3天后`
• 小时级提醒：`五小时后` `2小时后`
• 分钟级提醒：`5分钟后` `十分钟后` `30分钟后`

📋 *可用命令：*
• `/start` - 显示帮助信息
• `/list` - 查看未来24小时内的提醒

💡 *示例：*
• `明天10点 项目会议`
• `五小时后 睡觉`
• `五天后 续费提醒`
• `5分钟后 洗澡`
• `十分钟后 休息一下`
• `2025-01-15 14:30 重要会议`

开始设置你的第一个提醒吧！
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /list 命令，显示未来24小时内的提醒"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_reminders or not self.user_reminders[user_id]:
            await update.message.reply_text("📭 暂无待办提醒事项")
            return
            
        now = datetime.now()
        tomorrow = now + timedelta(hours=24)
        
        upcoming_reminders = []
        for reminder in self.user_reminders[user_id]:
            reminder_time = datetime.fromisoformat(reminder['time'])
            if now <= reminder_time <= tomorrow:
                upcoming_reminders.append(reminder)
                
        if not upcoming_reminders:
            await update.message.reply_text("📭 未来24小时内暂无提醒事项")
            return
            
        # 按时间排序
        upcoming_reminders.sort(key=lambda x: x['time'])
        
        reminder_list = "📋 *未来24小时内的提醒：*\n\n"
        for i, reminder in enumerate(upcoming_reminders, 1):
            reminder_time = datetime.fromisoformat(reminder['time'])
            time_str = reminder_time.strftime("%m-%d %H:%M")
            reminder_list += f"{i}. `{time_str}` - {reminder['event']}\n"
            
        await update.message.reply_text(reminder_list, parse_mode='Markdown')
        
    def parse_time_and_event(self, text: str) -> Tuple[Optional[datetime], Optional[str]]:
        """解析时间和事件"""
        try:
            now = datetime.now()
            
            # 中文数字转换字典
            chinese_numbers = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24,
                '三十': 30, '四十': 40, '五十': 50, '六十': 60
            }
            
            # 首先尝试解析天级相对时间（如：五天后、3天后）
            day_patterns = [
                r'(\d+)\s*天后',  # 数字+天后
                r'([一二三四五六七八九十]+)\s*天后',  # 中文数字+天后
                r'(\d+)\s*day[s]?\s*later',  # 英文格式
                r'in\s*(\d+)\s*day[s]?',  # 英文格式
                r'after\s*(\d+)\s*day[s]?'  # 英文格式
            ]
            
            for pattern in day_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    time_str = match.group(0)
                    day_str = match.group(1)
                    
                    if day_str in chinese_numbers:
                        days = chinese_numbers[day_str]
                    elif day_str.isdigit():
                        days = int(day_str)
                    else:
                        continue
                    
                    # 计算目标时间
                    target_time = now + timedelta(days=days)
                    
                    # 提取事件文本
                    event_text = re.sub(re.escape(time_str), '', text, count=1).strip()
                    event_text = re.sub(r'^\s*[-–—]\s*', '', event_text)
                    event_text = re.sub(r'\s*[-–—]\s*$', '', event_text)
                    event_text = event_text.strip()
                    
                    if not event_text:
                        event_text = "提醒事项"
                    
                    # 检查事件文本长度
                    if len(event_text.encode('utf-8')) > 200:
                        return None, None
                    
                    logger.info(f"解析天级提醒: {days}天后 - {event_text}")
                    return target_time, event_text
            
            # 然后尝试解析小时级相对时间（如：五小时后、3小时后）
            hour_patterns = [
                r'(\d+)\s*小时后',  # 数字+小时后
                r'([一二三四五六七八九十]+)\s*小时后',  # 中文数字+小时后
                r'(\d+)\s*hour[s]?\s*later',  # 英文格式
                r'in\s*(\d+)\s*hour[s]?',  # 英文格式
                r'after\s*(\d+)\s*hour[s]?'  # 英文格式
            ]
            
            for pattern in hour_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    time_str = match.group(0)
                    hour_str = match.group(1)
                    
                    if hour_str in chinese_numbers:
                        hours = chinese_numbers[hour_str]
                    elif hour_str.isdigit():
                        hours = int(hour_str)
                    else:
                        continue
                    
                    # 计算目标时间
                    target_time = now + timedelta(hours=hours)
                    
                    # 提取事件文本
                    event_text = re.sub(re.escape(time_str), '', text, count=1).strip()
                    event_text = re.sub(r'^\s*[-–—]\s*', '', event_text)
                    event_text = re.sub(r'\s*[-–—]\s*$', '', event_text)
                    event_text = event_text.strip()
                    
                    if not event_text:
                        event_text = "提醒事项"
                    
                    # 检查事件文本长度
                    if len(event_text.encode('utf-8')) > 200:
                        return None, None
                    
                    logger.info(f"解析小时级提醒: {hours}小时后 - {event_text}")
                    return target_time, event_text
            
            # 最后尝试解析分钟级相对时间（如：5分钟后、十分钟后）
            minute_patterns = [
                r'(\d+)\s*分钟后',  # 数字+分钟后
                r'([一二三四五六七八九十]+)\s*分钟后',  # 中文数字+分钟后
                r'(\d+)\s*min\s*later',  # 英文格式
                r'in\s*(\d+)\s*min',  # 英文格式
                r'after\s*(\d+)\s*min'  # 英文格式
            ]
            
            for pattern in minute_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    time_str = match.group(0)
                    minute_str = match.group(1)
                    
                    if minute_str in chinese_numbers:
                        minutes = chinese_numbers[minute_str]
                    elif minute_str.isdigit():
                        minutes = int(minute_str)
                    else:
                        continue
                    
                    # 计算目标时间
                    target_time = now + timedelta(minutes=minutes)
                    
                    # 提取事件文本
                    event_text = re.sub(re.escape(time_str), '', text, count=1).strip()
                    event_text = re.sub(r'^\s*[-–—]\s*', '', event_text)
                    event_text = re.sub(r'\s*[-–—]\s*$', '', event_text)
                    event_text = event_text.strip()
                    
                    if not event_text:
                        event_text = "提醒事项"
                    
                    # 检查事件文本长度
                    if len(event_text.encode('utf-8')) > 200:
                        return None, None
                    
                    logger.info(f"解析分钟级提醒: {minutes}分钟后 - {event_text}")
                    return target_time, event_text
            
            # 如果没有匹配到分钟级时间，使用原有的dateparser逻辑
            dates_found = search_dates(
                text,
                languages=['zh', 'en'],
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': now,
                    'RETURN_AS_TIMEZONE_AWARE': False
                }
            )
            
            if not dates_found:
                return None, None
                
            # 获取第一个找到的时间
            time_str, parsed_time = dates_found[0]

            # 如果解析结果仍旧在过去（如显式给出过去的绝对时间），认为无效
            if parsed_time <= now:
                return None, None
            
            # 提取事件文本（仅移除首个匹配时间子串）
            event_text = re.sub(re.escape(time_str), '', text, count=1).strip()
            
            # 清理事件文本
            event_text = re.sub(r'^\s*[-–—]\s*', '', event_text)
            event_text = re.sub(r'\s*[-–—]\s*$', '', event_text)
            event_text = event_text.strip()
            
            if not event_text:
                return parsed_time, "提醒事项"
                
            # 检查事件文本长度
            if len(event_text.encode('utf-8')) > 200:
                return None, None
                
            return parsed_time, event_text
            
        except Exception as e:
            logger.error(f"解析时间失败: {e}")
            return None, None
            
    async def handle_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理提醒设置消息"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # 解析时间和事件
        reminder_time, event = self.parse_time_and_event(message_text)
        
        if not reminder_time or not event:
            error_msg = "❌ 无法解析时间或事件，请检查格式\n\n" \
                       "正确格式示例：\n" \
                       "• `明天10点 项目会议`\n" \
                       "• `五小时后 睡觉`\n" \
                       "• `五天后 续费提醒`\n" \
                       "• `5分钟后 休息`\n" \
                       "• `2025-01-15 14:30 重要会议`"
            await update.message.reply_text(error_msg, parse_mode='Markdown')
            return
            
        # 检查时间是否过于接近当前时间（至少1分钟后）
        now = datetime.now()
        # 移除不必要的最小间隔限制，仅要求是未来时间（已在解析阶段保证）
        # if reminder_time <= now + timedelta(minutes=1):
        #     await update.message.reply_text("❌ 提醒时间至少需要在1分钟后")
        #     return
            
        # 保存提醒信息
        reminder_data = {
            'time': reminder_time.isoformat(),
            'event': event,
            'user_id': user_id,
            'chat_id': update.effective_chat.id,
            'job_id': f"reminder_{user_id}_{int(reminder_time.timestamp())}",
            'retry_count': 0  # 失败重试计数
        }
        
        if user_id not in self.user_reminders:
            self.user_reminders[user_id] = []
        self.user_reminders[user_id].append(reminder_data)
        
        # 添加调度任务（容忍±10秒误差）
        self.scheduler.add_job(
            self.send_reminder,
            'date',
            run_date=reminder_time,
            args=[reminder_data],
            id=reminder_data['job_id'],
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=10
        )
        
        # 确认消息
        time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
        confirm_msg = f"✅ 提醒已设置！\n\n" \
                     f"⏰ 时间：`{time_str}`\n" \
                     f"📝 事件：{event}"
        await update.message.reply_text(confirm_msg, parse_mode='Markdown')
        
    async def send_reminder(self, reminder_data: Dict):
        """发送提醒消息"""
        try:
            chat_id = reminder_data['chat_id']
            event = reminder_data['event']
            user_id = reminder_data['user_id']
            
            reminder_msg = f"⏰ *提醒时间到了！*\n\n📝 {event}"
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=reminder_msg,
                parse_mode='Markdown'
            )
            
            # 从用户提醒列表中移除已完成的提醒
            if user_id in self.user_reminders:
                self.user_reminders[user_id] = [
                    r for r in self.user_reminders[user_id] 
                    if r['job_id'] != reminder_data['job_id']
                ]
                
            logger.info(f"提醒发送成功: {event}")
            
        except TelegramError as e:
            logger.error(f"发送提醒失败: {e}")
            await self._schedule_retry(reminder_data)
        except Exception as e:
            logger.error(f"发送提醒发生未知错误: {e}")
            await self._schedule_retry(reminder_data)

    async def _schedule_retry(self, reminder_data: Dict):
        """调度失败重试任务：至少2次，间隔5分钟"""
        retry_count = reminder_data.get('retry_count', 0)
        if retry_count >= 2:
            # 达到最大重试次数，通知用户失败
            try:
                await self.bot.send_message(
                    chat_id=reminder_data['chat_id'],
                    text=f"❗提醒发送失败（已重试{retry_count}次）：{reminder_data['event']}",
                )
            except Exception:
                pass
            return
        
        updated_data = dict(reminder_data)
        updated_data['retry_count'] = retry_count + 1
        run_at = datetime.now() + timedelta(minutes=5)
        job_id = f"{reminder_data['job_id']}_retry_{updated_data['retry_count']}"
        logger.info(f"调度第{updated_data['retry_count']}次重试，时间：{run_at}")
        # 使用APScheduler安排重试
        self.scheduler.add_job(
            self.retry_send_reminder,
            'date',
            run_date=run_at,
            args=[updated_data],
            id=job_id,
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=10
        )

    async def retry_send_reminder(self, reminder_data: Dict):
        """执行重试发送逻辑"""
        try:
            await self.bot.send_message(
                chat_id=reminder_data['chat_id'],
                text=f"⏰ *延迟提醒*\n\n📝 {reminder_data['event']}",
                parse_mode='Markdown'
            )
            # 成功后从用户提醒列表移除
            user_id = reminder_data['user_id']
            if user_id in self.user_reminders:
                self.user_reminders[user_id] = [
                    r for r in self.user_reminders[user_id]
                    if r['job_id'] != reminder_data['job_id']
                ]
            logger.info("重试提醒发送成功")
        except Exception as e:
            logger.error(f"重试提醒仍失败: {e}")
            # 若未达到两次，则继续调度下一次重试
            await self._schedule_retry(reminder_data)
            
    async def run(self):
        """启动机器人"""
        try:
            # 启动调度器
            self.scheduler.start()
            logger.info("调度器已启动")
            
            # 手动启动机器人
            logger.info("Telegram提醒机器人启动中...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # 保持运行
            logger.info("机器人已启动，按Ctrl+C停止")
            try:
                # 使用无限循环保持程序运行
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("收到停止信号")
            
        except Exception as e:
            logger.error(f"机器人运行错误: {e}")
        finally:
            # 清理资源
            try:
                await self.application.stop()
                await self.application.shutdown()
            except:
                pass
            self.scheduler.shutdown()
            logger.info("机器人已停止")

# 为云平台添加健康检查端点
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Telegram Reminder Bot is running! 🤖"

@app.route('/health')
def health():
    return "OK"

async def main():
    """主函数"""
    # 优先从环境变量获取Token（推荐用于生产环境）
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # 如果环境变量未设置，使用默认Token（开发环境）
    if not token:
        token = "8495151574:AAGBRdMb1qvdS0qCdQEH4pl8xkDuc_97s6Q"
        logger.warning("使用默认Token，建议在生产环境中设置TELEGRAM_BOT_TOKEN环境变量")
    
    if not token or token.startswith("你的"):
        logger.error("❌ 错误：请设置有效的TELEGRAM_BOT_TOKEN环境变量")
        print("获取Token方法：")
        print("1. 在Telegram中搜索 @BotFather")
        print("2. 发送 /newbot 创建新机器人")
        print("3. 按提示设置机器人名称")
        print("4. 获得Token后设置环境变量：")
        print("   Windows: set TELEGRAM_BOT_TOKEN=你的token")
        print("   Linux/Mac: export TELEGRAM_BOT_TOKEN=你的token")
        return
    
    logger.info("🤖 Telegram提醒机器人启动中...")
    
    # 为云平台添加端口监听（健康检查）
    port = int(os.getenv('PORT', 8080))
    
    # 在单独线程中运行Flask应用（健康检查）
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    logger.info(f"🌐 健康检查服务启动在端口 {port}")
        
    # 创建并运行机器人
    bot = TelegramReminderBot(token)
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n机器人已停止")

if __name__ == "__main__":
    asyncio.run(main())