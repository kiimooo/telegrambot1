# Telegram 提醒机器人

基于Python实现的Telegram Bot，支持自然语言时间解析和自动提醒功能。

## 功能特性

- ✅ **自然语言时间解析**：支持绝对时间和相对时间描述
- ✅ **智能事件提取**：自动分离时间和事件文本
- ✅ **异步任务调度**：使用APScheduler实现精确定时提醒
- ✅ **失败重试机制**：最多2次重试，间隔5分钟
- ✅ **Telegram交互**：完整的Bot命令支持

## 环境要求

- Python 3.8+
- 有效的Telegram Bot Token

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置运行

1. **获取Telegram Bot Token**
   - 在Telegram中找到 `@BotFather`
   - 发送 `/newbot` 创建新机器人
   - 按提示设置机器人名称并获得Token

2. **设置环境变量**
   ```bash
   # Windows
   set TELEGRAM_BOT_TOKEN=你的token
   
   # Linux/Mac
   export TELEGRAM_BOT_TOKEN=你的token
   ```

3. **启动机器人**
   ```bash
   python telegram_reminder_bot.py
   ```

## 使用方法

### 基本命令

- `/start` - 显示帮助信息
- `/list` - 查看未来24小时内的提醒

### 设置提醒

直接发送「时间 + 事件」消息：

**支持的时间格式：**
- 绝对时间：`2025-01-15 14:30` 或 `14:30`
- 相对时间：`1小时后` `明天上午9点` `下周一15:00`

**示例：**
- `明天10点 项目会议`
- `1小时后 喝水`
- `2025-01-15 14:30 重要会议`

## 技术规格

- **时间解析库**：dateparser + search_dates
- **任务调度**：APScheduler (AsyncIOScheduler)
- **时间误差**：±10秒
- **重试机制**：失败后最多2次重试，间隔5分钟
- **事件文本限制**：UTF-8编码下≤200字符

## 项目结构

```
Liquidwiki/
├── telegram_reminder_bot.py  # 主程序文件
├── requirements.txt          # 依赖包列表
└── README.md                # 项目说明
```

## 安全说明

- Bot Token通过环境变量配置，避免硬编码
- 所有用户数据仅存储在内存中
- 遵循Telegram API最佳实践

## 故障排除

1. **时间解析失败**
   - 检查时间格式是否符合支持的格式
   - 确保时间是未来时间

2. **提醒发送失败**
   - 检查网络连接
   - 验证Bot Token是否有效
   - 系统会自动重试最多2次

3. **调度器异常**
   - 确保系统时间同步
   - 检查时区设置是否正确

## 开发团队

产品需求文档编号：TGBOT-REMINDER-001  
版本：1.0  
优先级：P0（最高紧急级别）