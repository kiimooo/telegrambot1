# 🚀 Telegram机器人快速部署指南

## 📋 推荐平台（按优先级排序）

### 🥇 Render（最推荐）
**为什么选择Render？**
- ✅ 完全免费750小时/月
- ✅ 自动重启和HTTPS
- ✅ 零配置部署
- ✅ GitHub集成

**部署步骤：**
1. 将代码推送到GitHub
2. 访问 [render.com](https://render.com) 注册
3. 连接GitHub仓库
4. 创建Web Service
5. 设置环境变量 `TELEGRAM_BOT_TOKEN`
6. 点击部署

### 🥈 Fly.io（性能最佳）
**优势：**
- ✅ 全球边缘部署
- ✅ $5免费额度
- ✅ 低延迟

**部署步骤：**
1. 安装Fly CLI
2. 运行 `fly launch`
3. 设置Token: `fly secrets set TELEGRAM_BOT_TOKEN=你的token`
4. 部署: `fly deploy`

### 🥉 PythonAnywhere（最简单）
**优势：**
- ✅ 永久免费1个应用
- ✅ 专门支持Python
- ✅ Web界面管理

**部署步骤：**
1. 注册 [pythonanywhere.com](https://www.pythonanywhere.com)
2. 上传代码文件
3. 安装依赖
4. 创建Always-On Task

---

## 📁 必需文件清单

✅ 已准备好的文件：
- `telegram_reminder_bot.py` - 主程序（已优化云部署）
- `requirements.txt` - 依赖列表（已添加Flask）
- `render.yaml` - Render配置
- `fly.toml` - Fly.io配置
- `Procfile` - 通用配置
- `.gitignore` - Git忽略文件

---

## 🔧 环境变量设置

所有平台都需要设置：
- **变量名**: `TELEGRAM_BOT_TOKEN`
- **变量值**: 你的机器人Token

---

## 🎯 一键部署命令

### Render部署
```bash
# 1. 推送到GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. 在Render网站完成剩余步骤
```

### Fly.io部署
```bash
# 1. 安装CLI（Windows PowerShell）
iwr https://fly.io/install.ps1 -useb | iex

# 2. 登录和部署
fly auth login
fly launch
fly secrets set TELEGRAM_BOT_TOKEN=你的token
fly deploy
```

---

## ✅ 部署验证

部署成功后，测试机器人：
1. 在Telegram中找到你的机器人
2. 发送 `/start` 命令
3. 尝试设置提醒：`明天上午9点开会`
4. 检查平台日志确认运行状态

---

## 🔍 故障排查

**机器人无响应？**
- 检查Token是否正确设置
- 查看平台部署日志
- 确认健康检查通过

**部署失败？**
- 检查requirements.txt格式
- 确认所有文件已推送到GitHub
- 查看构建日志错误信息

---

## 💡 成功提示

🎉 **恭喜！** 你的Telegram提醒机器人现在运行在云端，具备：
- ✅ 24/7不间断运行
- ✅ 自动重启功能
- ✅ 免费托管
- ✅ 全球访问

现在你可以随时随地使用机器人设置提醒了！