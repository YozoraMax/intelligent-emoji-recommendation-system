# 基于OSS的智能表情包推荐系统

一个基于阿里云OSS存储的智能表情包推荐系统，通过关键词匹配和情绪分析为用户推荐合适的表情包。

## 🌟 功能特性

- **🔤 智能匹配**: 基于关键词和情绪分析的表情包推荐
- **☁️ OSS集成**: 直接从阿里云OSS读取表情包资源
- **🔐 安全认证**: 支持Basic Auth和ECS RAM Role认证
- **⚡ 高性能**: 支持元数据缓存，减少OSS API调用
- **🌐 RESTful API**: 提供完整的HTTP API接口
- **📊 实时监控**: 提供状态监控和配置查看接口
- **🔄 动态刷新**: 支持运行时刷新表情包元数据

## 📁 项目结构

```
intelligent-emoji-recommendation-system/
├── config.py                  # 系统配置文件
├── oss_api_server.py          # FastAPI服务器主程序
├── oss_emoji_recommender.py   # 表情包推荐核心逻辑
├── oss_metadata_builder.py    # OSS元数据构建器
├── requirements.txt           # Python依赖包
└── README.md                  # 项目说明文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 阿里云OSS访问权限

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置OSS

在 `config.py` 中配置OSS相关参数：

```python
class OSSConfig:
    # OSS基本配置
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'    # 您的OSS地域
    BUCKET_NAME = 'your-bucket-name'            # 您的Bucket名称
    EMOJI_ROOT_PATH = 'emoji/'                  # 表情包根目录
    
    # 认证配置（二选一）
    # 方式1: ECS RAM Role认证（推荐）
    USE_ECS_RAM_ROLE = True
    
    # 方式2: AKSK认证
    # ACCESS_KEY_ID = 'your-access-key-id'
    # ACCESS_KEY_SECRET = 'your-access-key-secret'
```

### 5. 环境变量配置（可选）

创建 `.env` 文件：

```bash
# OSS认证（如果不使用ECS RAM Role）
OSS_ACCESS_KEY_ID=your-access-key
OSS_ACCESS_KEY_SECRET=your-secret-key
OSS_USE_ECS_RAM_ROLE=false

# API认证
API_USERNAME=your-username
API_PASSWORD=your-password
```

或者设置环境变量：

```bash
export OSS_ACCESS_KEY_ID="your-access-key"
export OSS_ACCESS_KEY_SECRET="your-secret-key"
export OSS_USE_ECS_RAM_ROLE="false"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
```

### 6. 运行服务

```bash
python oss_api_server.py
```

服务将在 `http://localhost:8000` 启动。

## 📖 API文档

### 基础信息

- **服务地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **认证方式**: Basic Auth（默认用户名: `emoji_user`，密码: `emoji_pass_2025`）

### 主要接口

#### 1. 表情包推荐

**POST** `/recommend`

```json
{
  "input": "今天心情很好，特别开心",
  "top_k": 1
}
```

**GET** `/recommend?input=今天心情很好&top_k=1`

**响应示例**:
```json
{
  "input": "今天心情很好，特别开心",
  "output": [
    {
      "url": "https://bucket.oss-region.aliyuncs.com/emoji/开心/happy.gif",
      "category": "开心",
      "score": 0.95,
      "keyword_score": 0.95,
      "semantic_score": 0.0,
      "rank": 1,
      "source": "oss"
    }
  ],
  "total_count": 1,
  "algorithm_config": {
    "keyword_weight": 0.7,
    "semantic_weight": 0.3
  },
  "oss_info": {
    "bucket": "your-bucket",
    "endpoint": "oss-cn-beijing.aliyuncs.com",
    "using_oss": true
  }
}
```

#### 2. 服务状态

**GET** `/status`

```json
{
  "status": "healthy",
  "message": "OSS推荐服务运行正常",
  "stats": {
    "total_categories": 15,
    "total_emoji_urls": 1250,
    "metadata_loaded_at": "2025-01-27T10:30:00",
    "using_oss": true
  }
}
```

#### 3. 配置信息

**GET** `/config`

```json
{
  "algorithm_config": {
    "keyword_weight": 0.7,
    "semantic_weight": 0.3
  },
  "recommend_config": {
    "default_top_k": 1,
    "max_top_k": 10,
    "min_top_k": 1
  },
  "oss_config": {
    "bucket": "your-bucket",
    "endpoint": "oss-cn-beijing.aliyuncs.com",
    "emoji_root_path": "emoji/",
    "cache_file": "oss_emoji_metadata.json",
    "cache_expire_hours": 24
  }
}
```

#### 4. 刷新元数据

**POST** `/refresh`

强制重新从OSS加载表情包元数据。

#### 5. 健康检查

**GET** `/health`

系统健康状态检查，无需认证。

### API使用示例

#### Python请求示例

```python
import requests
from base64 import b64encode

# API基础信息
base_url = "http://localhost:8000"
username = "emoji_user"
password = "emoji_pass_2025"

# 构建Basic Auth头
credentials = b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {credentials}"}

# 推荐表情包
response = requests.post(
    f"{base_url}/recommend",
    headers=headers,
    json={"input": "今天心情很好", "top_k": 2}
)

if response.status_code == 200:
    result = response.json()
    for emoji in result["output"]:
        print(f"分类: {emoji['category']}")
        print(f"URL: {emoji['url']}")
        print(f"分数: {emoji['score']}")
        print("---")
else:
    print(f"请求失败: {response.status_code}")
```

#### curl命令示例

```bash
# 推荐表情包 (POST)
curl -X POST "http://localhost:8000/recommend" \
  -H "Authorization: Basic ZW1vamlfdXNlcjplbW9qaV9wYXNzXzIwMjU=" \
  -H "Content-Type: application/json" \
  -d '{"input": "今天心情很好", "top_k": 1}'

# 推荐表情包 (GET)
curl "http://localhost:8000/recommend?input=开心&top_k=1" \
  -H "Authorization: Basic ZW1vamlfdXNlcjplbW9qaV9wYXNzXzIwMjU="

# 查看服务状态
curl "http://localhost:8000/status" \
  -H "Authorization: Basic ZW1vamlfdXNlcjplbW9qaV9wYXNzXzIwMjU="

# 健康检查（无需认证）
curl "http://localhost:8000/health"
```

#### JavaScript/前端示例

```javascript
// 推荐表情包函数
async function recommendEmoji(text, topK = 1) {
    const username = 'emoji_user';
    const password = 'emoji_pass_2025';
    const credentials = btoa(`${username}:${password}`);
    
    try {
        const response = await fetch('http://localhost:8000/recommend', {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${credentials}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input: text,
                top_k: topK
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.output;
        } else {
            console.error('推荐失败:', response.status);
            return [];
        }
    } catch (error) {
        console.error('请求错误:', error);
        return [];
    }
}

// 使用示例
recommendEmoji('今天心情很好').then(emojis => {
    emojis.forEach(emoji => {
        console.log(`分类: ${emoji.category}, URL: ${emoji.url}`);
    });
});
```

## 🔧 配置说明

### 算法配置

```python
class AlgorithmConfig:
    KEYWORD_WEIGHT = 0.7    # 关键词匹配权重 70%
    SEMANTIC_WEIGHT = 0.3   # 语义匹配权重 30%
```

### 情绪关键词

系统预定义了9种情绪分类：

- **开心**: 开心、高兴、快乐、兴奋等
- **愤怒**: 愤怒、生气、恼火、暴躁等  
- **悲伤**: 悲伤、难过、伤心、沮丧等
- **撒娇**: 撒娇、可爱、萌、求等
- **疲惫**: 累、疲惫、困、倦怠等
- **好吃**: 吃、好吃、美食、蛋糕等
- **害羞**: 害羞、脸红、不好意思等
- **赞同**: 支持、赞同、同意、对等
- **鼓励**: 安慰、鼓励、加油、没事等

### OSS目录结构

推荐的OSS目录结构：

```
your-bucket/
└── emoji/                 # EMOJI_ROOT_PATH
    ├── 开心/
    │   ├── happy1.gif
    │   └── happy2.png
    ├── 愤怒/
    │   ├── angry1.gif
    │   └── angry2.jpg
    └── 悲伤/
        ├── sad1.gif
        └── sad2.webp
```

## 🛠️ 独立组件使用

### 1. 元数据构建器

```bash
python oss_metadata_builder.py
```

手动构建OSS表情包元数据。

### 2. 推荐器测试

```bash
python oss_emoji_recommender.py
```

测试表情包推荐功能。

### 3. 配置验证

```bash
python config.py
```

验证和显示当前配置信息。

## 📦 部署指南

### 生产环境部署

#### 使用Gunicorn（推荐）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务（4个工作进程）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 oss_api_server:app

# 带日志配置的启动
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/emoji-api/access.log \
  --error-logfile /var/log/emoji-api/error.log \
  --log-level info \
  oss_api_server:app
```

#### 使用systemd服务（Linux）

创建服务配置文件 `/etc/systemd/system/emoji-recommender.service`：

```ini
[Unit]
Description=Emoji Recommender API Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/intelligent-emoji-recommendation-system
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 oss_api_server:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start emoji-recommender

# 设置开机自启
sudo systemctl enable emoji-recommender

# 查看服务状态
sudo systemctl status emoji-recommender
```

#### 使用Nginx反向代理

Nginx配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 🔍 故障排除

### 常见问题

1. **OSS认证失败**
   - 检查ACCESS_KEY_ID和ACCESS_KEY_SECRET
   - 确认ECS实例已配置RAM角色（如使用RAM Role）
   - 验证OSS访问权限

2. **表情包加载失败**
   - 检查BUCKET_NAME和ENDPOINT配置
   - 确认EMOJI_ROOT_PATH路径正确
   - 验证OSS中是否存在表情包文件

3. **API认证失败**
   - 检查API_USERNAME和API_PASSWORD
   - 确认请求头包含正确的Basic Auth信息

4. **性能问题**
   - 增加缓存时间（CACHE_EXPIRE_HOURS）
   - 使用CDN加速OSS访问
   - 考虑本地缓存表情包URL
   - 使用Gunicorn多进程部署
   - 配置Nginx反向代理和负载均衡

### 日志查看

服务运行时会输出详细日志，包括：

- OSS连接状态
- 元数据加载进度
- 推荐请求处理
- 错误信息和堆栈

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🆕 版本更新

### v2.0.0
- ✨ 全面重构为基于OSS的架构
- 🔐 新增Basic Auth认证支持
- ⚡ 优化元数据缓存机制
- 📊 增强API响应格式
- 🛠️ 改进错误处理和日志记录

### v1.x.x
- 🎯 基础表情包推荐功能
- 🔤 关键词匹配算法
- 📁 本地文件系统支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues页面]
- 📖 文档: [项目Wiki页面]

---

<div align="center">
  <strong>基于OSS的智能表情包推荐系统</strong><br>
  让表情包推荐更智能、更便捷！ 🎉
</div> 