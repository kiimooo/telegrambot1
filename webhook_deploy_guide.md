# Telegram 机器人 Webhook 模式部署指南

## 概述

本机器人已切换到 **Webhook 模式**，可以完美解决 Render 平台的多实例冲突问题。Webhook 模式下，Telegram 服务器会主动推送消息到你的应用，避免了 Long Polling 模式的多实例冲突。

## 🚀 Render 部署步骤

### 1. 推送代码到 GitHub

确保最新的 Webhook 版本代码已推送到 GitHub 仓库。

### 2. 在 Render 创建 Web Service

1. 登录 [Render](https://render.com)
2. 点击 "New" → "Web Service"
3. 连接你的 GitHub 仓库
4. 配置如下：
   - **Name**: `telegram-reminder-bot`（或你喜欢的名称）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_reminder_bot.py`

### 3. 设置环境变量

在 Render 的 "Environment" 标签页中添加以下环境变量：

#### 必需变量：
- **TELEGRAM_BOT_TOKEN**: 你的机器人 Token
- **WEBHOOK_URL**: `https://你的应用名称.onrender.com/webhook`

#### 示例：
```
TELEGRAM_BOT_TOKEN=8495151574:AAGBRdMb1qvdS0qCdQEH4pl8xkDuc_97s6Q
WEBHOOK_URL=https://telegram-reminder-bot-abc123.onrender.com/webhook
```

> **注意**: `WEBHOOK_URL` 中的域名需要替换为你实际的 Render 应用域名。

### 4. 部署应用

1. 点击 "Create Web Service"
2. 等待部署完成（通常需要几分钟）
3. 部署成功后，你会看到应用的 URL

### 5. 验证部署

1. 访问 `https://你的应用名称.onrender.com/` 应该看到："Telegram Reminder Bot is running! 🤖"
2. 访问 `https://你的应用名称.onrender.com/health` 应该看到："OK"
3. 在 Telegram 中向你的机器人发送 `/start` 命令测试功能

## 🔧 技术优势

### Webhook 模式 vs Long Polling 模式

| 特性 | Webhook 模式 ✅ | Long Polling 模式 ❌ |
|------|----------------|---------------------|
| 多实例冲突 | 无冲突 | 409 Conflict 错误 |
| 资源消耗 | 低（被动接收） | 高（主动轮询） |
| 实时性 | 即时推送 | 轮询延迟 |
| Render 兼容性 | 完美兼容 | 多实例问题 |
| 网络流量 | 低 | 高 |

### 解决的问题

1. **多实例冲突**: Render 的预启动和零停机部署不再导致冲突
2. **资源优化**: 不需要持续轮询，降低 CPU 和网络使用
3. **更好的响应**: 消息推送更及时
4. **稳定性**: 避免了 `getUpdates` API 的限制

## 🛠️ 故障排查

### 常见问题

#### 1. 机器人不响应消息

**检查步骤**:
- 确认 `TELEGRAM_BOT_TOKEN` 设置正确
- 确认 `WEBHOOK_URL` 设置正确且可访问
- 查看 Render 日志是否有错误信息

#### 2. Webhook 设置失败

**可能原因**:
- `WEBHOOK_URL` 格式错误
- 应用未完全启动
- SSL 证书问题（Render 自动提供 HTTPS）

**解决方法**:
```bash
# 手动检查 Webhook 状态（可选）
curl -X POST "https://api.telegram.org/bot你的TOKEN/getWebhookInfo"
```

#### 3. 环境变量未生效

- 确保在 Render 控制台正确设置了环境变量
- 重新部署应用使环境变量生效

### 日志查看

在 Render 控制台的 "Logs" 标签页可以查看应用日志：

```
🤖 Telegram提醒机器人启动中（Webhook模式）...
调度器已启动
机器人应用已初始化
Webhook 已设置: https://your-app.onrender.com/webhook
✅ 机器人初始化完成（Webhook模式）
🌐 启动 Flask 服务器在端口 10000
```

## 📝 注意事项

1. **HTTPS 要求**: Telegram Webhook 要求 HTTPS，Render 自动提供
2. **端口配置**: Render 会自动设置 `PORT` 环境变量
3. **域名变更**: 如果 Render 域名变更，需要更新 `WEBHOOK_URL`
4. **Token 安全**: 不要在代码中硬编码 Token，使用环境变量

## 🎉 完成

恭喜！你的 Telegram 提醒机器人现在运行在 Webhook 模式下，完全解决了 Render 平台的多实例冲突问题。机器人现在可以稳定运行，不会再出现 409 错误。

如有问题，请检查 Render 日志或参考故障排查部分。