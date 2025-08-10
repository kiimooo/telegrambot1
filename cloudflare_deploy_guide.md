# Telegram机器人免费部署指南 - Cloudflare Workers & 其他平台

## 🚨 重要提醒

由于Railway不再提供免费服务，我们为您提供多个免费替代方案。**推荐使用Render或Fly.io**，因为它们对Python支持最好且部署简单。

## 📋 免费平台对比

| 平台 | 免费额度 | Python支持 | 部署难度 | 推荐指数 |
|------|----------|-------------|----------|----------|
| **Render** | 750小时/月 | ✅ 原生支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Fly.io** | $5信用额度 | ✅ 原生支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **PythonAnywhere** | 1个应用 | ✅ 专门支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Koyeb** | 1个服务 | ✅ 原生支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cloudflare Workers** | 100,000请求/天 | ✅ 新支持 | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🥇 方案一：Render部署（强烈推荐）

### 为什么选择Render？
- ✅ **完全免费**：750小时/月（约31天）
- ✅ **零配置**：自动检测Python项目
- ✅ **自动重启**：应用崩溃自动恢复
- ✅ **HTTPS支持**：免费SSL证书
- ✅ **Git集成**：推送代码自动部署

### 部署步骤

#### 1. 准备代码
确保项目包含以下文件：
- `telegram_reminder_bot.py`（主程序）
- `requirements.txt`（依赖列表）
- `render.yaml`（新建配置文件）

#### 2. 创建render.yaml
```yaml
services:
  - type: web
    name: telegram-reminder-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python telegram_reminder_bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
```

#### 3. 注册Render账号
1. 访问 [render.com](https://render.com)
2. 使用GitHub账号注册
3. 连接你的GitHub仓库

#### 4. 创建Web Service
1. 点击"New" → "Web Service"
2. 选择你的GitHub仓库
3. 配置设置：
   - **Name**: telegram-reminder-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_reminder_bot.py`

#### 5. 设置环境变量
在Render控制台中添加：
- **Key**: `TELEGRAM_BOT_TOKEN`
- **Value**: 你的机器人Token

#### 6. 部署
点击"Create Web Service"，Render会自动部署你的应用。

---

## 🥈 方案二：Fly.io部署

### 优势
- ✅ **全球边缘部署**：低延迟
- ✅ **$5免费额度**：足够小型机器人使用
- ✅ **Docker支持**：灵活配置

### 部署步骤

#### 1. 安装Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. 创建fly.toml
```toml
app = "telegram-reminder-bot"
primary_region = "nrt"  # 东京节点，延迟较低

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[[services.tcp_checks]]
  grace_period = "1s"
  interval = "15s"
  restart_limit = 0
  timeout = "2s"
```

#### 3. 部署命令
```bash
# 登录Fly.io
fly auth login

# 初始化应用
fly launch

# 设置环境变量
fly secrets set TELEGRAM_BOT_TOKEN=你的机器人Token

# 部署
fly deploy
```

---

## 🥉 方案三：PythonAnywhere部署

### 优势
- ✅ **专门支持Python**：无需配置
- ✅ **永久免费**：1个应用永久免费
- ✅ **简单易用**：Web界面管理

### 部署步骤

#### 1. 注册账号
访问 [pythonanywhere.com](https://www.pythonanywhere.com) 注册免费账号

#### 2. 上传代码
1. 进入"Files"页面
2. 上传你的Python文件
3. 在控制台安装依赖：
```bash
pip3.10 install --user python-telegram-bot schedule
```

#### 3. 创建Always-On Task
1. 进入"Tasks"页面
2. 创建新任务
3. 命令：`python3.10 /home/yourusername/telegram_reminder_bot.py`
4. 设置环境变量：`TELEGRAM_BOT_TOKEN=你的Token`

---

## 🔧 代码修改（适配所有平台）

### 修改telegram_reminder_bot.py

需要对现有代码进行小幅修改以适配云平台：

```python
# 在文件开头添加
import os
from flask import Flask

# 为某些平台添加健康检查端点
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK"

# 修改main函数
def main():
    # 优先从环境变量获取Token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        # 如果环境变量未设置，使用默认Token（仅用于本地测试）
        token = "你的默认Token"  # 替换为你的实际Token
        print("⚠️ 警告：使用默认Token，建议设置环境变量TELEGRAM_BOT_TOKEN")
    
    if not token or token == "你的默认Token":
        print("❌ 错误：请设置有效的TELEGRAM_BOT_TOKEN环境变量")
        print("设置方法：")
        print("  Linux/Mac: export TELEGRAM_BOT_TOKEN=你的token")
        print("  Windows: set TELEGRAM_BOT_TOKEN=你的token")
        return
    
    # 启动机器人
    bot = TelegramReminderBot(token)
    
    # 为云平台添加端口监听
    port = int(os.getenv('PORT', 8080))
    
    # 在单独线程中运行Flask应用（健康检查）
    import threading
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    
    # 运行机器人
    bot.run()

if __name__ == '__main__':
    main()
```

### 更新requirements.txt
```txt
python-telegram-bot==20.7
schedule==1.2.0
flask==2.3.3
```

---

## 🚀 快速部署检查清单

### ✅ 文件准备
- [ ] `telegram_reminder_bot.py`（已修改）
- [ ] `requirements.txt`（已更新）
- [ ] 平台配置文件（render.yaml/fly.toml等）
- [ ] `.gitignore`（已存在）

### ✅ 账号准备
- [ ] GitHub账号（代码托管）
- [ ] 选择的云平台账号
- [ ] Telegram Bot Token

### ✅ 部署步骤
- [ ] 代码推送到GitHub
- [ ] 连接云平台与GitHub
- [ ] 设置环境变量
- [ ] 启动部署
- [ ] 测试机器人功能

---

## 🔍 故障排查

### 常见问题

1. **机器人无响应**
   - 检查Token是否正确设置
   - 查看平台日志
   - 确认网络连接

2. **部署失败**
   - 检查requirements.txt格式
   - 确认Python版本兼容性
   - 查看构建日志

3. **应用休眠**
   - Render免费版会在无活动时休眠
   - 可以设置定时ping保持活跃

### 日志查看
- **Render**: Dashboard → Logs
- **Fly.io**: `fly logs`
- **PythonAnywhere**: Tasks → Log files

---

## 💡 推荐方案总结

1. **首选：Render**
   - 最简单的部署流程
   - 750小时免费额度充足
   - 自动HTTPS和重启

2. **备选：Fly.io**
   - 全球边缘部署，性能更好
   - $5信用额度，按使用量计费
   - 更灵活的配置选项

3. **稳定选择：PythonAnywhere**
   - 专门为Python设计
   - 永久免费1个应用
   - 简单的Web界面管理

选择任一平台都能让你的Telegram提醒机器人稳定运行，并具备自动重启功能！