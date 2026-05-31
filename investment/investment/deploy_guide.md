# 投资时机决策模拟器 - 部署指南

## 方案一：Streamlit Cloud 部署（推荐，免费）

### 步骤1：准备GitHub仓库
1. 访问 https://github.com 并登录
2. 创建新仓库，命名为 `investment-decision-simulator`
3. 上传以下文件到仓库：
   - app.py
   - calculator.py
   - visualizer.py
   - validator.py
   - requirements.txt

### 步骤2：部署到Streamlit Cloud
1. 访问 https://streamlit.io/cloud
2. 使用GitHub账号登录
3. 点击 "New app"
4. 选择您的GitHub仓库
5. 主文件路径填写：`app.py`
6. 点击 "Deploy"

### 步骤3：分享链接
- 部署完成后，您会获得一个永久链接，如：
  `https://yourname-investment-decision-simulator.streamlit.app`
- 把这个链接分享给任何人，他们随时都可以访问

---

## 方案二：PythonAnywhere 部署（免费）

### 步骤1：注册账号
1. 访问 https://www.pythonanywhere.com
2. 注册免费账号

### 步骤2：上传代码
1. 登录后进入 "Files" 标签
2. 创建新目录 `investment-simulator`
3. 上传所有Python文件

### 步骤3：创建Web应用
1. 进入 "Web" 标签
2. 点击 "Add a new web app"
3. 选择 "Flask" 或手动配置
4. 修改WSGI配置文件，指向您的app

---

## 方案三：Heroku 部署

### 步骤1：准备文件
创建 `Procfile` 文件，内容：
```
web: streamlit run app.py --server.port $PORT
```

### 步骤2：部署
1. 注册Heroku账号
2. 安装Heroku CLI
3. 使用Git部署：
```bash
heroku create investment-simulator
heroku git:remote -a investment-simulator
git add .
git commit -m "Initial commit"
git push heroku master
```

---

## 方案四：VPS服务器部署（适合技术用户）

### 购买VPS
推荐：阿里云、腾讯云、AWS、DigitalOcean等

### 部署步骤
```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 安装Python和依赖
apt update
apt install python3 python3-pip
pip3 install streamlit numpy pandas matplotlib

# 3. 上传代码（使用scp或git）
scp -r d:\investment root@your-server-ip:/root/

# 4. 运行程序
cd /root/investment
streamlit run app.py --server.port 80
```

### 使用systemd保持运行
创建服务文件 `/etc/systemd/system/investment.service`：
```ini
[Unit]
Description=Investment Decision Simulator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/investment
ExecStart=/usr/local/bin/streamlit run app.py --server.port 80 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
systemctl enable investment
systemctl start investment
```

---

## 推荐方案总结

| 方案 | 费用 | 难度 | 稳定性 | 适合人群 |
|------|------|------|--------|----------|
| Streamlit Cloud | 免费 | 简单 | 高 | 所有人 |
| PythonAnywhere | 免费 | 中等 | 中 | 有一定基础 |
| Heroku | 免费/付费 | 中等 | 中 | 开发者 |
| VPS | 付费 | 较难 | 高 | 技术用户 |

**强烈推荐使用 Streamlit Cloud**，因为它是：
- ✅ 完全免费
- ✅ 部署简单（只需几次点击）
- ✅ 自动维护，无需管理服务器
- ✅ 提供HTTPS安全连接
- ✅ 支持自定义域名

---

## 快速开始

如果您想立即开始，我建议：

1. **创建GitHub账号**（如果还没有）
2. **创建新仓库**并上传代码文件
3. **访问 Streamlit Cloud** 并部署
4. **获得永久链接**，分享给任何人

整个过程大约需要15-30分钟，之后任何人都可以随时访问您的程序，无需您在线！