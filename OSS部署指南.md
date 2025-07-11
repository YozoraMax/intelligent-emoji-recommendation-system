# 基于阿里云OSS的智能表情包推荐系统 - 部署指南

## 📋 概述

本指南将帮助您将表情包文件上传到阿里云OSS，并配置基于OSS的智能表情包推荐系统。

## 🚀 系统特性

### ✨ OSS版本优势
- **☁️ 云存储**: 基于阿里云OSS，无需本地存储
- **🌍 CDN加速**: 支持全球CDN加速访问
- **📈 可扩展**: 支持海量表情包存储
- **🔄 自动同步**: 元数据自动构建和缓存
- **💰 成本优化**: 按需付费，成本可控

### 🔧 技术架构
```
用户输入 → API服务 → 关键词匹配 → JSON元数据查找 → OSS URL返回
    ↓          ↓          ↓           ↓            ↓
  文本分析    接口处理    算法计算     元数据缓存     云端文件
```

## 📦 第一步：OSS存储配置

### 1.1 创建OSS Bucket
1. 登录[阿里云控制台](https://oss.console.aliyun.com/)
2. 创建新的Bucket：
   - **Bucket名称**: 全局唯一（如：`my-emoji-bucket-2025`）
   - **地域**: 选择离用户最近的地域
   - **读写权限**: 公共读（便于直接访问图片）
   - **版本控制**: 关闭（可选）

### 1.2 上传表情包文件
按照以下目录结构上传您的表情包文件：

```
assets/
├── 好吃/
│   ├── 1716434598861.gif
│   ├── 1716434707976.gif
│   └── ...
├── 害羞/
│   ├── 2302878817.gif
│   └── ...
├── 开心 舒适/
│   ├── 1732357420441.gif
│   └── ...
├── 悲伤  丧丧的 焦虑 紧张/
│   └── ...
└── 其他分类/
    └── ...
```

**重要说明：**
- 📁 **目录名称**：即为表情包分类，系统会自动识别
- 🎯 **支持格式**：`.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`
- 📂 **根目录**：统一放在 `assets/` 目录下

### 1.3 配置访问权限
确保Bucket的读权限设置正确：
```bash
# 方式1: 控制台设置
OSS控制台 → Bucket管理 → 权限管理 → 读写权限 → 公共读

# 方式2: 自定义域名（推荐）
绑定自定义域名并配置CDN加速
```

## ⚙️ 第二步：系统配置

### 2.1 安装依赖
```bash
pip install -r requirements.txt
```

确保 `requirements.txt` 包含OSS依赖：
```txt
# OSS依赖
oss2>=2.18.0
```

### 2.2 配置OSS信息
在 `config.py` 文件中配置OSS信息：

```python
# ============== 阿里云OSS配置 ==============
class OSSConfig:
    """阿里云OSS相关配置"""
    
    # OSS基本配置
    ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'          # 您的AccessKey ID
    ACCESS_KEY_SECRET = 'YOUR_ACCESS_KEY_SECRET'  # 您的AccessKey Secret
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'      # 您的OSS Endpoint
    BUCKET_NAME = 'your-bucket-name'              # 您的Bucket名称
    
    # URL配置
    CUSTOM_DOMAIN = ''                            # 自定义域名（可选）
    USE_HTTPS = True                              # 是否使用HTTPS
    
    # 表情包配置
    EMOJI_ROOT_PATH = 'assets/'                   # 表情包根路径
    SUPPORTED_EXTENSIONS = ['.gif', '.jpg', '.jpeg', '.png', '.webp']
    
    # 缓存配置
    METADATA_CACHE_FILE = 'oss_emoji_metadata.json'
    CACHE_EXPIRE_HOURS = 24
```

### 2.3 获取AccessKey信息
1. 登录[阿里云控制台](https://ram.console.aliyun.com/)
2. 访问控制 RAM → 用户管理
3. 创建用户并分配OSS权限：
   - `AliyunOSSFullAccess` 或 `AliyunOSSReadOnlyAccess`
4. 创建AccessKey获取ID和Secret

## 🔨 第三步：构建元数据

### 3.1 运行元数据构建器
```bash
python oss_metadata_builder.py
```

该脚本会：
- 🔍 扫描OSS Bucket中的所有表情包文件
- 📊 按目录自动分类
- 💾 生成JSON元数据文件
- ⚡ 缓存结果以提高性能

### 3.2 元数据文件格式
生成的 `oss_emoji_metadata.json` 文件格式：
```json
{
  "metadata": {
    "generated_at": "2025-01-27T12:00:00",
    "total_categories": 9,
    "total_files": 102,
    "oss_bucket": "my-emoji-bucket",
    "oss_endpoint": "oss-cn-beijing.aliyuncs.com",
    "emoji_root_path": "assets/"
  },
  "categories": {
    "好吃": [
      "https://my-emoji-bucket.oss-cn-beijing.aliyuncs.com/assets/好吃/1716434598861.gif",
      "https://my-emoji-bucket.oss-cn-beijing.aliyuncs.com/assets/好吃/1716434707976.gif"
    ],
    "开心 舒适": [
      "https://my-emoji-bucket.oss-cn-beijing.aliyuncs.com/assets/开心 舒适/1732357420441.gif"
    ]
  }
}
```

## 🚀 第四步：启动API服务

### 4.1 启动OSS版API服务
```bash
# 方式1: 直接启动
python oss_api_server.py

# 方式2: 使用uvicorn
uvicorn oss_api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 4.2 验证服务状态
```bash
# 健康检查
curl http://localhost:8000/health

# 获取服务状态
curl http://localhost:8000/status

# 查看API文档
http://localhost:8000/docs
```

## 🔧 环境变量配置

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
```

## 🧪 测试验证

### 4.3 测试OSS配置
```bash
python test_oss_config.py
```

### 4.4 测试API接口
```bash
# 使用curl测试（需要认证）
curl -X POST -u "emoji_user:emoji_pass_2025" \
     "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"input": "今天心情很好", "top_k": 1}'
```

## 🚀 生产环境部署

### 5.1 性能优化
1. **CDN配置**: 绑定自定义域名启用CDN
2. **缓存策略**: 调整元数据缓存时间
3. **并发配置**: 使用gunicorn等WSGI服务器

### 5.2 安全配置
1. **权限控制**: 使用只读权限的AccessKey
2. **网络安全**: 配置安全组和防火墙
3. **认证强化**: 使用强密码或JWT认证

### 5.3 监控告警
1. **OSS监控**: 配置OSS访问监控和告警
2. **API监控**: 配置服务可用性监控
3. **成本控制**: 设置OSS费用告警

## ❓ 常见问题

### Q: 如何更换OSS Bucket？
A: 修改config.py中的BUCKET_NAME，重新运行元数据构建器

### Q: 表情包分类如何定义？
A: 直接通过OSS中的目录名称定义，系统会自动识别

### Q: 如何添加新的表情包？
A: 直接上传到OSS对应分类目录，然后调用/refresh接口刷新元数据

### Q: 支持哪些图片格式？
A: 支持GIF、JPG、PNG、WebP格式

### Q: 如何优化推荐算法？
A: 可以修改config.py中的情绪关键词配置或权重设置

## 📞 技术支持

如有问题，请：
1. 查看日志文件了解错误详情
2. 检查OSS配置和权限设置  
3. 参考API认证使用说明文档
4. 提交Issue到GitHub仓库