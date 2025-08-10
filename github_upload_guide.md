# GitHub 上传和 Railway 部署完整指南

## 第一步：初始化 Git 仓库并上传到 GitHub

### 1. 在项目目录中初始化 Git
```bash
cd f:\program\python脚本\Liquidwiki
git init
```

### 2. 添加远程仓库
```bash
git remote add origin https://github.com/kiimooo/telegrambot1.git
```

### 3. 添加所有文件到 Git
```bash
git add .
```

### 4. 提交代码
```bash
git commit -m "Initial commit: Telegram reminder bot with minute-level reminders"
```

### 5. 推送到 GitHub
```bash
git branch -M main
git push -u origin main
```

## 第二步：在 Railway 部署

### 1. 访问 Railway
- 打开 https://railway.app/
- 使用 GitHub 账号登录

### 2. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的仓库 `kiimooo/telegrambot1`

### 3. 配置环境变量
在 Railway 项目设置中添加环境变量：
- 变量名：`TELEGRAM_BOT_TOKEN`
- 变量值：你的 Telegram Bot Token

### 4. 部署设置
Railway 会自动检测到以下文件并进行配置：
- `Procfile`：定义启动命令
- `requirements.txt`：安装 Python 依赖
- `runtime.txt`：指定 Python 版本

### 5. 监控部署
- 在 Railway 控制台查看部署日志
- 确认机器人成功启动

## 第三步：验证部署

### 1. 检查日志
在 Railway 控制台查看应用日志，应该看到：
```
Telegram提醒机器人启动中...
调度器已启动
Application已启动
机器人已启动，按Ctrl+C停止
```

### 2. 测试机器人
在 Telegram 中：
1. 找到你的机器人
2. 发送 `/start` 命令
3. 测试提醒功能，例如："5分钟后提醒我喝水"

## 项目文件说明

- `telegram_reminder_bot.py`：主程序文件
- `requirements.txt`：Python 依赖包列表
- `Procfile`：Railway 启动命令
- `runtime.txt`：Python 版本指定
- `.gitignore`：Git 忽略文件配置
- `railway_deploy_guide.md`：详细部署指南

## 常见问题解决

### 1. 推送到 GitHub 失败
如果遇到权限问题，可能需要：
- 配置 GitHub Personal Access Token
- 使用 SSH 密钥认证

### 2. Railway 部署失败
检查：
- 环境变量是否正确设置
- `requirements.txt` 中的依赖是否正确
- 日志中的错误信息

### 3. 机器人无响应
确认：
- Bot Token 是否正确
- 机器人是否已启动
- 网络连接是否正常

## Railway 优势

- ✅ **自动部署**：代码推送后自动部署
- ✅ **自动重启**：应用崩溃后自动重启
- ✅ **免费额度**：每月 $5 免费额度
- ✅ **零配置**：自动检测项目类型
- ✅ **实时日志**：实时查看应用日志
- ✅ **环境变量**：安全的配置管理

## 后续维护

### 更新代码
1. 修改本地代码
2. 提交并推送到 GitHub：
   ```bash
   git add .
   git commit -m "更新描述"
   git push
   ```
3. Railway 会自动重新部署

### 查看日志
在 Railway 控制台的 "Deployments" 标签页查看实时日志

### 管理环境变量
在 Railway 项目设置中可以随时修改环境变量

---

**注意**：确保不要将 Bot Token 直接提交到 GitHub 仓库中，始终使用环境变量来管理敏感信息。