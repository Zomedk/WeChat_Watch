# WeChat Article Monitor 快速上手

## 一、核心文件速查

```
backend/
├── main.py              # 入口，FastAPI启动
├── get_cookie.py        # 本地扫码登录，生成cookie
├── requirements.txt     # Python依赖
├── Dockerfile           # Docker镜像构建
├── .env                 # 环境变量配置
├── wechat_auth_state.json  # 微信登录状态（cookie）
├── wechat_monitor.db    # SQLite数据库
├── downloads/           # 下载的文章存储
│
├── app/
│   ├── api/routes.py    # API路由
│   ├── api/login.py     # 登录相关路由
│   ├── services/
│   │   ├── wechat_service.py  # 微信API封装
│   │   └── ai_service.py      # AI摘要服务
│   ├── scheduler/tasks.py    # 定时同步任务
│   ├── models/schemas.py     # 数据库模型
│   └── static/index.html     # 前端页面
```

## 二、Cookie更新流程

### 1. 本地生成Cookie

```bash
cd backend
python get_cookie.py
# 浏览器自动打开，扫码登录后自动保存到 wechat_auth_state.json
```

### 2. SCP推送到服务器

```bash
# Cookie文件路径：backend/wechat_auth_state.json
# 服务器路径需要看docker-compose.yml的volume映射

# 查看docker-compose.yml中的volume配置：
# volumes:
#   - ./backend/wechat_auth_state.json:/app/wechat_auth_state.json

# 推送到服务器的backend目录（假设服务器IP是YOUR_SERVER_IP）
scp backend/wechat_auth_state.json user@YOUR_SERVER_IP:/path/to/wechat-article-monitor/backend/

# 然后重启容器使新cookie生效
ssh user@YOUR_SERVER_IP "cd /path/to/wechat-article-monitor && docker-compose restart"
```

### 3. 完整Cookie更新脚本（本地执行）

```bash
# cookie_update.sh
SERVER="user@YOUR_SERVER_IP"
PROJECT_DIR="/path/to/wechat-article-monitor"

# 步骤1：本地生成cookie
cd backend && python get_cookie.py && cd ..

# 步骤2：上传cookie
scp backend/wechat_auth_state.json $SERVER:$PROJECT_DIR/backend/

# 步骤3：重启容器
ssh $SERVER "cd $PROJECT_DIR && docker-compose restart"
```

## 三、数据存储位置

| 数据 | 本地路径 | Docker容器路径 | 说明 |
|------|----------|---------------|------|
| 数据库 | `backend/wechat_monitor.db` | `/app/wechat_monitor.db` | SQLite，存订阅/文章/设置 |
| Cookie | `backend/wechat_auth_state.json` | `/app/wechat_auth_state.json` | 微信登录状态 |
| 文章 | `backend/downloads/` | `/app/downloads` | Markdown文件+图片 |

## 四、API接口

### 公众号管理
```
GET    /api/subscriptions              获取所有订阅
POST   /api/subscriptions              添加订阅 {name, fakeid?}
DELETE /api/subscriptions/{id}         删除订阅
POST   /api/subscriptions/{id}/sync   同步该公众号文章
GET    /api/subscriptions/search?name= 搜索公众号
```

### 文章管理
```
GET    /api/articles?subscription_id=&is_read=&date=  获取文章列表
PUT    /api/articles/{id}/read         切换已读状态
POST   /api/articles/{id}/summary      生成AI摘要
```

### 系统设置
```
GET    /api/settings/ai               获取AI配置
POST   /api/settings/ai               保存AI配置 {api_key, url, model, proxy}
GET    /api/auth/status               检查微信登录状态
```

## 五、AI配置说明

### 有效的模型名称
- `gemini-3.5-flash`（推荐，速度快）
- `gemini-2.5-flash`
- `gemini-2.5-pro`
- `gemini-1.5-flash`

### Docker中使用代理
```
proxy=http://host.docker.internal:10808
```
> Docker容器内需要通过宿主机IP访问本地代理

## 六、常用命令

### 本地开发
```bash
cd backend
pip install -r requirements.txt
python main.py
# 访问 http://localhost:8000
```

### Docker部署
```bash
# 首次构建
docker-compose up -d --build

# 重启
docker-compose restart

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 代码同步
```bash
# 本地提交
git add .
git commit -m "update"
git push

# 服务器更新
ssh user@SERVER "cd /path && git pull && docker-compose restart"
```

## 七、关键逻辑流程

### 文章同步
```
定时触发（60分钟）
    ↓
遍历active状态的订阅
    ↓
获取微信token（从cookie）
    ↓
调用微信API获取文章列表
    ↓
下载文章HTML → 转Markdown → 存本地
    ↓
存入SQLite数据库
```

### AI摘要生成
```
用户点击"生成摘要"
    ↓
从数据库读取文章内容
    ↓
构建8段式生物医药行业提示词
    ↓
调用Gemini API（通过代理）
    ↓
解析返回文本
    ↓
保存到article.summary
```

## 八、数据库表结构

### subscriptions 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(100) | 公众号名称 |
| fakeid | VARCHAR(100) | 微信唯一标识 |
| status | VARCHAR(20) | active/inactive |
| added_at | DATETIME | 添加时间 |
| last_sync_at | DATETIME | 最后同步 |

### articles 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| title | VARCHAR(255) | 标题 |
| url | VARCHAR(500) | 原文链接 |
| publish_date | DATE | 发布日期 |
| digest | TEXT | 微信摘要 |
| content | TEXT | 正文内容 |
| summary | TEXT | AI摘要 |
| markdown_path | VARCHAR(500) | 本地文件路径 |
| subscription_id | INT | 关联公众号 |
| is_read | BOOL | 是否已读 |

### settings 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| key | VARCHAR(100) | 配置键 |
| value | TEXT | 配置值 |
| updated_at | DATETIME | 更新时间 |

**AI相关配置键**：
- `ai_api_key` - API密钥
- `ai_api_base_url` - API地址
- `ai_model` - 模型名称
- `ai_proxy` - 代理地址

## 九、故障排查

### Cookie失效
```bash
# 1. 本地重新登录
python get_cookie.py

# 2. 上传到服务器并重启
scp backend/wechat_auth_state.json user@SERVER:/path/backend/
ssh user@SERVER "cd /path && docker-compose restart"
```

### AI调用超时
- 检查代理是否可达：`curl -x http://host.docker.internal:10808 https://generativelanguage.googleapis.com`
- 更换代理地址

### 容器无法启动
```bash
# 查看错误日志
docker-compose logs

# 重建容器
docker-compose down
docker-compose up -d --build
```