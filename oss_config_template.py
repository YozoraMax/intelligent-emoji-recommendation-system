#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
阿里云OSS配置模板文件

请复制此文件中的配置到 config.py 中的 OSSConfig 类，
并根据您的实际阿里云OSS信息进行修改。
"""

# ============== OSS配置模板 ==============
class OSSConfigTemplate:
    """
    阿里云OSS配置模板
    
    使用说明:
    1. 登录阿里云控制台获取以下信息
    2. 将这些配置复制到 config.py 中的 OSSConfig 类
    3. 根据实际情况修改配置值
    """
    
    # ============== 必填配置 ==============
    
    # 阿里云AccessKey信息 (在RAM控制台获取)
    ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'            # 替换为您的AccessKey ID
    ACCESS_KEY_SECRET = 'YOUR_ACCESS_KEY_SECRET'    # 替换为您的AccessKey Secret
    
    # OSS服务配置
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'        # 替换为您的OSS地域节点
    BUCKET_NAME = 'your-bucket-name'                # 替换为您的Bucket名称
    
    # ============== 可选配置 ==============
    
    # 自定义域名配置（CDN加速）
    CUSTOM_DOMAIN = ''                              # 可选：自定义域名，如 'cdn.example.com'
    USE_HTTPS = True                                # 是否使用HTTPS协议
    
    # 表情包存储配置
    EMOJI_ROOT_PATH = 'assets/'                     # 表情包在OSS中的根目录
    SUPPORTED_EXTENSIONS = ['.gif', '.jpg', '.jpeg', '.png', '.webp']  # 支持的文件格式
    
    # 缓存配置
    METADATA_CACHE_FILE = 'oss_emoji_metadata.json'  # 本地元数据缓存文件
    CACHE_EXPIRE_HOURS = 24                         # 缓存过期时间（小时）

# ============== API认证配置模板 ==============
class AuthConfigTemplate:
    """
    API认证配置模板
    """
    
    # Basic Auth配置
    ENABLE_AUTH = True                              # 是否启用认证
    USERNAME = 'your_api_username'                  # API用户名
    PASSWORD = 'your_secure_password'               # API密码
    
    # 公共路径（无需认证）
    PUBLIC_PATHS = [
        '/',                    # 根路径
        '/health',              # 健康检查
        '/docs',                # API文档
        '/openapi.json',        # OpenAPI规范
        '/redoc'                # ReDoc文档
    ]

def main():
    """主函数"""
    print("📋 阿里云OSS配置模板")
    print("=" * 50)
    print("此文件提供了OSS和API认证配置的模板和说明。")
    print("请根据您的实际情况修改 config.py 中的相关配置类。")
    
    print("\n💡 配置步骤:")
    print("1. 登录阿里云控制台")
    print("2. 进入RAM控制台创建用户并获取AccessKey")
    print("3. 进入OSS控制台创建Bucket")
    print("4. 将OSS信息填入config.py中的OSSConfig类")
    print("5. 修改API认证信息（用户名密码）")
    print("6. 运行 python test_oss_config.py 验证配置")

if __name__ == "__main__":
    main()