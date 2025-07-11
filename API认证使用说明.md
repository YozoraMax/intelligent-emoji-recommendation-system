# API Basic Auth认证使用说明

## 🔐 认证概述

本API系统已启用Basic Auth认证，保护表情包推荐接口的安全访问。

### 认证配置

- **认证方式**: HTTP Basic Authentication
- **用户名**: `emoji_user`
- **密码**: `emoji_pass_2025`
- **认证状态**: ✅ 已启用

## 📋 接口权限说明

### 🌍 公共接口（无需认证）
以下接口可以直接访问，无需提供认证信息：

- `GET /` - API基本信息
- `GET /health` - 健康检查
- `GET /docs` - Swagger API文档  
- `GET /openapi.json` - OpenAPI规范
- `GET /redoc` - ReDoc文档

### 🔒 保护接口（需要认证）
以下接口需要提供有效的Basic Auth认证信息：

- `POST /recommend` - 表情包推荐（主要功能）
- `GET /recommend` - 表情包推荐（GET方式）
- `GET /status` - 服务状态查询
- `GET /config` - 配置信息获取
- `POST /refresh` - 刷新元数据缓存

## 🛠️ 使用方法

### 1. Python Requests示例

```python
import requests
import base64

# 认证信息
username = "emoji_user"
password = "emoji_pass_2025"

# 生成Basic Auth头
auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {auth_string}"}

# 调用推荐API
response = requests.post(
    "http://localhost:8000/recommend",
    json={
        "input": "今天心情很好，特别开心",
        "top_k": 1
    },
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print("推荐成功:", result)
else:
    print("请求失败:", response.status_code, response.text)
```

### 2. curl命令示例

```bash
# 方法1: 直接在URL中指定用户名密码
curl -X POST "http://emoji_user:emoji_pass_2025@localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"input": "今天好开心", "top_k": 1}'

# 方法2: 使用-u参数
curl -X POST -u "emoji_user:emoji_pass_2025" \
     "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"input": "今天好开心", "top_k": 1}'

# 方法3: 手动设置Authorization头
curl -X POST "http://localhost:8000/recommend" \
     -H "Authorization: Basic ZW1vamNfdXNlcjplbW9qaV9wYXNzXzIwMjU=" \
     -H "Content-Type: application/json" \
     -d '{"input": "今天好开心", "top_k": 1}'
```

### 3. JavaScript/Node.js示例

```javascript
// 使用fetch API
const username = 'emoji_user';
const password = 'emoji_pass_2025';
const authString = btoa(`${username}:${password}`);

fetch('http://localhost:8000/recommend', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${authString}`
    },
    body: JSON.stringify({
        input: '今天心情很好',
        top_k: 1
    })
})
.then(response => response.json())
.then(data => console.log('推荐结果:', data))
.catch(error => console.error('错误:', error));
```

### 4. Java示例

```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.util.Base64;

// 创建认证头
String credentials = "emoji_user:emoji_pass_2025";
String encodedCredentials = Base64.getEncoder()
    .encodeToString(credentials.getBytes());

// 构建请求
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:8000/recommend"))
    .header("Authorization", "Basic " + encodedCredentials)
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(
        "{\"input\": \"今天好开心\", \"top_k\": 1}"))
    .build();

// 发送请求
HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());
System.out.println("响应: " + response.body());
```

## ⚠️ 错误处理

### 401 未授权错误

当认证失败时，API会返回以下格式的错误响应：

```json
{
    "error": "认证失败",
    "message": "需要提供有效的用户名和密码",
    "detail": "请提供Basic Auth认证信息"
}
```

常见错误情况：

1. **未提供认证信息**
   ```bash
   curl http://localhost:8000/recommend
   # 返回: 401 Unauthorized
   ```

2. **用户名或密码错误**
   ```bash
   curl -u "wrong_user:wrong_pass" http://localhost:8000/recommend
   # 返回: 401 Unauthorized
   ```

3. **认证格式错误**
   ```bash
   curl -H "Authorization: Bearer invalid_token" http://localhost:8000/recommend
   # 返回: 401 Unauthorized
   ```

## 🔧 配置管理

### 认证开关

可以在 `config.py` 中的 `AuthConfig` 类中控制认证功能：

```python
class AuthConfig:
    # 设置为 False 可禁用认证
    ENABLE_AUTH = True
    
    # 修改用户名密码
    USERNAME = 'your_username'
    PASSWORD = 'your_password'
```

### 公共路径配置

可以配置哪些路径无需认证：

```python
class AuthConfig:
    PUBLIC_PATHS = [
        '/',                    # 根路径
        '/health',              # 健康检查
        '/docs',                # API文档
        '/openapi.json',        # OpenAPI规范
        '/redoc'                # ReDoc文档
    ]
```

## 🌐 环境变量配置

可以通过环境变量动态配置认证信息：

```bash
# 设置环境变量
export API_USERNAME="your_custom_username"
export API_PASSWORD="your_secure_password"

# 或在.env文件中配置
API_USERNAME=your_custom_username
API_PASSWORD=your_secure_password
```

## 📝 生产环境建议

1. **强密码**: 使用强密码或生成随机密码
2. **HTTPS**: 生产环境务必使用HTTPS
3. **定期更换**: 定期更换认证凭据
4. **日志监控**: 监控认证失败的访问
5. **速率限制**: 考虑添加API速率限制

## ❓ 常见问题

### Q: 如何禁用认证？
A: 在 `config.py` 中设置 `AuthConfig.ENABLE_AUTH = False`

### Q: 如何修改用户名密码？
A: 修改 `config.py` 中的 `AuthConfig.USERNAME` 和 `AuthConfig.PASSWORD`，或设置对应的环境变量

### Q: 为什么我的请求返回401？
A: 检查用户名密码是否正确，确保使用正确的Basic Auth格式

### Q: 如何在生产环境中安全配置？
A: 使用环境变量或加密配置文件，避免在代码中硬编码密码