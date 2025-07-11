#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试ECS RAM Role OSS连接
"""

import os
import logging
from config import OSSConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ecs_ram_role_connection():
    """测试ECS RAM Role连接OSS"""
    try:
        # 确保使用ECS RAM Role模式
        os.environ['OSS_USE_ECS_RAM_ROLE'] = 'true'
        
        print("🧪 测试ECS RAM Role OSS连接")
        print("=" * 50)
        
        # 显示配置信息
        print(f"认证模式: {'ECS RAM Role' if OSSConfig.USE_ECS_RAM_ROLE else 'AKSK'}")
        print(f"Bucket: {OSSConfig.BUCKET_NAME}")
        print(f"Endpoint: {OSSConfig.ENDPOINT}")
        print(f"根路径: {OSSConfig.EMOJI_ROOT_PATH}")
        
        # 尝试导入并初始化OSS客户端
        try:
            import oss2
            from oss2.credentials import EcsRamRoleCredentialsProvider
            from oss2 import ProviderAuth
            
            print("\n📦 OSS2库版本检查通过")
            
            # 创建凭证提供者
            print("🔑 创建ECS RAM Role凭证提供者...")
            credentials_provider = EcsRamRoleCredentialsProvider()
            
            # 创建认证对象
            print("🔐 创建认证对象...")
            auth = ProviderAuth(credentials_provider)
            
            # 创建Bucket对象
            print("📦 创建Bucket对象...")
            bucket = oss2.Bucket(auth, OSSConfig.ENDPOINT, OSSConfig.BUCKET_NAME)
            
            # 测试连接
            print("🏥 测试OSS连接...")
            bucket_info = bucket.get_bucket_info()
            
            print("✅ ECS RAM Role连接测试成功！")
            print(f"📊 Bucket信息:")
            print(f"   - 名称: {bucket_info.name}")
            print(f"   - 创建时间: {bucket_info.creation_date}")
            print(f"   - 地域: {bucket_info.location}")
            print(f"   - 存储类型: {bucket_info.storage_class}")
            
            # 测试列出对象
            print(f"\n📁 测试列出对象 (前5个)...")
            object_count = 0
            for obj in oss2.ObjectIterator(bucket, prefix=OSSConfig.EMOJI_ROOT_PATH, max_keys=5):
                if not obj.key.endswith('/'):  # 跳过目录
                    print(f"   - {obj.key}")
                    object_count += 1
            
            if object_count > 0:
                print(f"✅ 成功列出 {object_count} 个对象")
            else:
                print(f"⚠️  在路径 {OSSConfig.EMOJI_ROOT_PATH} 下未找到对象")
            
            return True
            
        except ImportError as e:
            print(f"❌ OSS2库导入失败: {e}")
            print("请安装或升级OSS2: pip install --upgrade oss2")
            return False
            
        except Exception as e:
            print(f"❌ OSS连接失败: {e}")
            print("\n🔧 排查建议:")
            print("1. 确保ECS实例已附加RAM角色")
            print("2. 检查RAM角色是否有OSS访问权限")
            print("3. 确保安全组允许访问OSS服务")
            print("4. 检查Bucket名称和地域是否正确")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_aksk_fallback():
    """测试AKSK模式作为备选方案"""
    try:
        # 设置为AKSK模式
        os.environ['OSS_USE_ECS_RAM_ROLE'] = 'false'
        
        print("\n🔄 测试AKSK认证模式 (备选方案)")
        print("-" * 50)
        
        # 检查是否有AKSK配置
        if not OSSConfig.ACCESS_KEY_ID or OSSConfig.ACCESS_KEY_ID == 'YOUR_ACCESS_KEY_ID':
            print("⚠️  未配置AKSK，跳过AKSK测试")
            return False
        
        import oss2
        
        # 创建传统认证
        auth = oss2.Auth(OSSConfig.ACCESS_KEY_ID, OSSConfig.ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, OSSConfig.ENDPOINT, OSSConfig.BUCKET_NAME)
        
        # 测试连接
        bucket_info = bucket.get_bucket_info()
        print("✅ AKSK连接测试成功！")
        
        return True
        
    except Exception as e:
        print(f"❌ AKSK连接失败: {e}")
        return False

def show_iam_role_setup_guide():
    """显示IAM角色设置指南"""
    print("\n📋 ECS RAM角色设置指南")
    print("=" * 50)
    print("1. 在RAM控制台创建角色:")
    print("   - 角色类型: 服务角色")
    print("   - 受信服务: 云服务器ECS")
    print("")
    print("2. 为角色添加OSS权限策略:")
    print("   - AliyunOSSFullAccess (完全访问)")
    print("   - 或自定义权限策略")
    print("")
    print("3. 将角色绑定到ECS实例:")
    print("   - 在ECS控制台选择实例")
    print("   - 更多 -> 实例设置 -> 绑定/解绑RAM角色")
    print("")
    print("4. 重启应用程序以应用新的角色权限")
    print("")
    print("📝 最小权限策略示例:")
    print("""
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "oss:ListObjects",
        "oss:GetObject",
        "oss:GetBucketInfo"
      ],
      "Resource": [
        "acs:oss:*:*:your-bucket-name",
        "acs:oss:*:*:your-bucket-name/*"
      ]
    }
  ]
}
""")

def main():
    """主函数"""
    print("🔐 ECS RAM Role OSS连接测试")
    print("=" * 60)
    
    # 显示环境信息
    print(f"当前模式: {'ECS RAM Role' if OSSConfig.USE_ECS_RAM_ROLE else 'AKSK'}")
    print(f"OSS Bucket: {OSSConfig.BUCKET_NAME}")
    print(f"OSS Endpoint: {OSSConfig.ENDPOINT}")
    
    # 测试ECS RAM Role
    success = test_ecs_ram_role_connection()
    
    if not success:
        # 如果RAM Role失败，尝试AKSK作为备选
        print("\n🔄 尝试AKSK模式作为备选方案...")
        aksk_success = test_aksk_fallback()
        
        if not aksk_success:
            # 显示设置指南
            show_iam_role_setup_guide()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ECS RAM Role测试成功！可以安全部署到生产环境")
    else:
        print("❌ 连接测试失败，请检查配置")

if __name__ == "__main__":
    main()