# 基于阿里云OSS的智能表情包推荐系统

基于阿里云OSS云存储的智能表情包推荐系统，通过JSON元数据实现高效的表情包匹配和推荐。

## 🌟 项目特性

### ✨ 核心优势
- **☁️ 云端存储**: 基于阿里云OSS，支持海量表情包存储
- **🚀 高性能**: JSON元数据查找，毫秒级响应
- **🌍 全球加速**: 支持CDN加速，全球快速访问
- **💰 成本优化**: 按需付费，存储成本低
- **🔄 智能缓存**: 24小时自动缓存，减少OSS访问
- **⚙️ 配置化**: 灵活的配置管理系统
- **📈 易扩展**: 支持无限表情包扩展

### 🎯 应用场景
- 聊天机器人智能表情包推荐
- 社交应用自动表情回复
- 情绪分析和表达辅助
- 基于云存储的表情包管理

## 🏗️ 系统架构

```
用户输入 → API服务 → 关键词匹配 → JSON元数据查找 → OSS URL返回
    ↓          ↓          ↓           ↓            ↓
  文本分析    接口处理    算法计算     元数据缓存     云端文件
```

### 技术栈
- **云存储**: 阿里云OSS对象存储
- **API框架**: FastAPI (高性能异步框架)
- **数据格式**: JSON元数据映射
- **中文分词**: jieba分词
- **缓存机制**: 本地文件缓存
- **支持格式**: GIF/JPG/PNG/WebP

## 📦 项目结构

```
情绪聊天/
├── config.py                     # 配置文件（包含OSS配置）
├── oss_metadata_builder.py       # OSS元数据构建器
├── oss_emoji_recommender.py      # OSS版推荐算法
├── oss_api_server.py             # OSS版API服务端
├── oss_config_template.py        # OSS配置模板
├── test_oss_config.py            # OSS配置测试脚本
├── requirements.txt              # 依赖列表
├── OSS部署指南.md                # 详细部署说明
├── OSS集成总结.md                # 集成工作总结
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 第一步：准备OSS环境

1. **创建阿里云OSS Bucket**
   - 登录阿里云控制台创建Bucket
   - 设置读权限为"公共读"
   - 记录Bucket名称和地域信息

2. **上传表情包文件**
   ```
   assets/
   ├── 好吃/
   │   ├── emoji1.gif
   │   └── emoji2.gif
   ├── 开心 舒适/
   │   └── emoji.gif
   └── 其他分类/
       └── ...
   ```

3. **获取AccessKey**
   - 在阿里云RAM控制台创建用户
   - 分配OSS权限
   - 创建AccessKey

### 第二步：配置系统

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置OSS信息**
   ```python
   # 在config.py中配置
   class OSSConfig:
       ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
       ACCESS_KEY_SECRET = 'YOUR_ACCESS_KEY_SECRET'
       ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
       BUCKET_NAME = 'your-bucket-name'
   ```

3. **验证配置**
   ```bash
   python test_oss_config.py
   ```

### 第三步：构建元数据

```bash
python oss_metadata_builder.py
```

该脚本会：
- 🔍 扫描OSS Bucket中的表情包文件
- 📊 按目录自动分类
- 💾 生成JSON元数据文件 (`oss_emoji_metadata.json`)
- ⚡ 创建24小时缓存

### 第四步：启动API服务

```bash
python oss_api_server.py
```

服务启动后可访问：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **服务状态**: http://localhost:8000/status

## 📡 API接口

### 1. 表情包推荐

⚠️ **认证要求**: 本API已启用Basic Auth认证，需要提供用户名和密码。

```bash
# POST请求（需要认证）
curl -X POST -u "emoji_user:emoji_pass_2025" \
     "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{
       "input": "今天心情特别好，很开心",
       "top_k": 1
     }'

# GET请求（需要认证）
curl -u "emoji_user:emoji_pass_2025" \
     "http://localhost:8000/recommend?input=今天好开心&top_k=1"
```

### 2. 响应格式
```json
{
  "input": "今天心情特别好，很开心",
  "output": [
    {
      "url": "https://bucket.oss-cn-beijing.aliyuncs.com/assets/开心 舒适/emoji.gif",
      "category": "开心 舒适",
      "score": 1.0,
      "keyword_score": 1.0,
      "semantic_score": 0.0,
      "keyword_weight": 0.7,
      "semantic_weight": 0.3,
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
    "bucket": "your-bucket-name",
    "endpoint": "oss-cn-beijing.aliyuncs.com",
    "using_oss": true
  }
}
```

### 3. 其他接口
- **GET /status**: 服务状态和统计信息
- **GET /config**: 获取当前配置
- **POST /refresh**: 刷新元数据缓存
- **GET /health**: 健康检查

## 🔧 配置说明

### OSS配置项
```python
class OSSConfig:
    # 必填配置
    ACCESS_KEY_ID = ''              # 阿里云AccessKey ID
    ACCESS_KEY_SECRET = ''          # 阿里云AccessKey Secret
    ENDPOINT = ''                   # OSS Endpoint
    BUCKET_NAME = ''                # OSS Bucket名称
    
    # 可选配置
    CUSTOM_DOMAIN = ''              # 自定义域名（CDN）
    USE_HTTPS = True                # 是否使用HTTPS
    EMOJI_ROOT_PATH = 'assets/'     # 表情包根路径
    METADATA_CACHE_FILE = 'oss_emoji_metadata.json'
    CACHE_EXPIRE_HOURS = 24         # 缓存过期时间
```

### 算法配置
```python
class AlgorithmConfig:
    KEYWORD_WEIGHT = 0.7    # 关键词匹配权重70%
    SEMANTIC_WEIGHT = 0.3   # 语义匹配权重30%

class RecommendConfig:
    DEFAULT_TOP_K = 1       # 默认推荐数量
    MAX_TOP_K = 10          # 最大推荐数量
```

## 🔧 环境配置

### OSS认证配置

#### 方式1: ECS RAM Role (推荐，更安全)

在ECS实例上部署时，推荐使用RAM角色进行认证，无需在代码中存储敏感信息：

```bash
# 环境变量配置
OSS_USE_ECS_RAM_ROLE=true
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name

# API认证配置
API_USERNAME=your_username
API_PASSWORD=your_password
```

**ECS RAM角色设置步骤：**
1. 在RAM控制台创建服务角色（受信服务：ECS）
2. 为角色添加OSS权限策略（AliyunOSSFullAccess或自定义）
3. 在ECS控制台将角色绑定到实例
4. 重启应用程序应用新权限

#### 方式2: AccessKey (传统方式)

```bash
# 环境变量配置
OSS_USE_ECS_RAM_ROLE=false
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name

# API认证配置  
API_USERNAME=your_username
API_PASSWORD=your_password
```

## 📚 详细文档

- [OSS部署指南](./OSS部署指南.md) - 完整的部署说明
- [API认证使用说明](./API认证使用说明.md) - API认证详细说明
- [OSS集成总结](./OSS集成总结.md) - 技术实现总结

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

---

🌟 如果这个项目对您有帮助，请给它一个star！