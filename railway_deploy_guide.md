# Railway部署Telegram提醒机器人详细指南

## 🚀 Railway部署完整流程

### 第一步：准备工作

#### 1.1 注册Railway账号
- 访问 [railway.app](https://railway.app)
- 使用GitHub账号登录（推荐）
- 完成邮箱验证

#### 1.2 准备GitHub仓库
- 如果还没有GitHub账号，先注册一个
- 创建新的仓库用于存放机器人代码

### 第二步：代码准备和上传

#### 2.1 检查项目文件
确保你的项目包含以下文件：
- `telegram_reminder_bot.py` - 主程序文件
- `requirements.txt` - Python依赖文件
- `README.md` - 项目说明（可选）

#### 2.2 创建Railway配置文件
在项目根目录创建以下文件：

**创建 `railway.toml`**（可选，用于高级配置）：
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python telegram_reminder_bot.py"
restartPolicyType = "always"
```

**创建 `Procfile`**（可选，指定启动命令）：
```
web: python telegram_reminder_bot.py
```

#### 2.3 上传代码到GitHub

**方法A：使用Git命令行**
```bash
# 在项目目录执行
git init
git add .
git commit -m "Initial commit: Telegram reminder bot"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

**方法B：使用GitHub Desktop**
1. 下载并安装GitHub Desktop
2. 创建新仓库
3. 将文件拖拽到仓库中
4. 提交并推送

**方法C：直接在GitHub网页上传**
1. 在GitHub创建新仓库
2. 点击"uploading an existing file"
3. 拖拽文件上传
4. 提交更改

### 第三步：Railway部署

#### 3.1 连接GitHub仓库
1. 登录Railway控制台
2. 点击"New Project"
3. 选择"Deploy from GitHub repo"
4. 授权Railway访问你的GitHub账号
5. 选择包含机器人代码的仓库

#### 3.2 配置部署设置
1. Railway会自动检测Python项目
2. 确认构建命令：`pip install -r requirements.txt`
3. 确认启动命令：`python telegram_reminder_bot.py`

#### 3.3 配置环境变量（如果需要）
虽然我们已经把Token写入代码，但为了安全考虑，建议使用环境变量：

1. 在Railway项目设置中找到"Variables"选项
2. 添加环境变量：
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: `8495151574:AAGBRdMb1qvdS0qCdQEH4pl8xkDuc_97s6Q`

然后修改代码使用环境变量优先：
```python
# 在main函数中
token = os.getenv('TELEGRAM_BOT_TOKEN', "8495151574:AAGBRdMb1qvdS0qCdQEH4pl8xkDuc_97s6Q")
```

#### 3.4 部署项目
1. 点击"Deploy"按钮
2. Railway开始构建和部署
3. 等待部署完成（通常2-5分钟）

### 第四步：验证部署

#### 4.1 查看部署状态
- 在Railway控制台查看部署日志
- 确认没有错误信息
- 看到"机器人已启动"的日志信息

#### 4.2 测试机器人功能
1. 在Telegram中找到你的机器人
2. 发送 `/start` 命令
3. 测试设置提醒功能
4. 验证分钟级提醒是否正常工作

### 第五步：监控和维护

#### 5.1 查看日志
- 在Railway控制台的"Deployments"页面查看实时日志
- 监控机器人运行状态

#### 5.2 自动重启配置
Railway默认会在应用崩溃时自动重启，无需额外配置。

#### 5.3 更新代码
当需要更新机器人代码时：
1. 修改本地代码
2. 推送到GitHub仓库
3. Railway会自动检测更改并重新部署

### 第六步：高级配置（可选）

#### 6.1 自定义域名
- 在Railway项目设置中可以配置自定义域名
- 虽然机器人不需要Web界面，但可以用于健康检查

#### 6.2 数据库集成
如果将来需要数据库：
- Railway支持PostgreSQL、MySQL等数据库
- 可以在项目中添加数据库服务

#### 6.3 监控告警
- 可以集成第三方监控服务
- 设置机器人离线告警

## 🔧 故障排查

### 常见问题及解决方案

#### 问题1：部署失败
**可能原因**：
- requirements.txt文件格式错误
- Python版本不兼容

**解决方案**：
- 检查requirements.txt格式
- 在项目根目录添加`runtime.txt`指定Python版本：
  ```
  python-3.9.18
  ```

#### 问题2：机器人无响应
**可能原因**：
- Token配置错误
- 网络连接问题

**解决方案**：
- 检查环境变量配置
- 查看Railway部署日志

#### 问题3：应用休眠
**Railway特点**：
- 免费版有使用限制
- 长时间无活动可能休眠

**解决方案**：
- 升级到付费计划
- 或者接受偶尔的冷启动延迟

## 💰 费用说明

### Railway免费额度
- 每月$5免费额度
- 包含500小时运行时间
- 对于个人机器人使用通常足够

### 付费计划
- Hobby计划：$5/月
- Pro计划：$20/月
- 提供更多资源和功能

## 📋 部署检查清单

- [ ] Railway账号注册完成
- [ ] GitHub仓库创建并上传代码
- [ ] requirements.txt文件正确
- [ ] Railway项目创建并连接GitHub
- [ ] 环境变量配置（如果使用）
- [ ] 部署成功无错误
- [ ] 机器人功能测试通过
- [ ] 日志监控配置

## 🎯 总结

Railway是部署Telegram机器人的优秀选择，具有以下优势：
- 配置简单，几分钟即可完成部署
- 与GitHub深度集成，支持自动部署
- 免费额度对个人使用足够
- 自动重启和监控功能
- 良好的开发者体验

按照本指南操作，你的Telegram提醒机器人很快就能在云端稳定运行！