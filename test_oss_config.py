#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSS配置测试脚本
用于验证OSS配置是否正确
"""

def test_oss_config():
    """测试OSS配置"""
    print("🧪 OSS配置测试脚本")
    print("=" * 50)
    
    try:
        # 1. 检查配置模块导入
        print("📥 1. 检查配置模块...")
        from config import OSSConfig
        print("   ✅ 配置模块导入成功")
        
        # 2. 验证OSS配置
        print("\n🔧 2. 验证OSS配置...")
        try:
            OSSConfig.validate_config()
            print("   ✅ OSS配置验证通过")
            
            # 显示配置信息
            print(f"   📦 Bucket: {OSSConfig.BUCKET_NAME}")
            print(f"   🌐 Endpoint: {OSSConfig.ENDPOINT}")
            print(f"   📁 表情包路径: {OSSConfig.EMOJI_ROOT_PATH}")
            
        except ValueError as e:
            print(f"   ❌ OSS配置验证失败: {e}")
            print("   💡 请在config.py中正确配置OSS信息")
            return False
        
        # 3. 测试OSS连接
        print("\n🌐 3. 测试OSS连接...")
        try:
            from oss_metadata_builder import OSSMetadataBuilder
            builder = OSSMetadataBuilder()
            
            if builder.test_connection():
                print("   ✅ OSS连接测试成功")
            else:
                print("   ❌ OSS连接测试失败")
                return False
                
        except ImportError:
            print("   ⚠️  oss2依赖未安装，跳过连接测试")
            print("   💡 请运行: pip install oss2")
        except Exception as e:
            print(f"   ❌ OSS连接测试失败: {e}")
            return False
        
        # 4. 检查相关文件
        print("\n📄 4. 检查相关文件...")
        files_to_check = [
            'oss_metadata_builder.py',
            'oss_emoji_recommender.py', 
            'oss_api_server.py',
            'oss_config_template.py',
            'OSS部署指南.md'
        ]
        
        import os
        for filename in files_to_check:
            if os.path.exists(filename):
                print(f"   ✅ {filename}")
            else:
                print(f"   ❌ {filename} (缺失)")
        
        print("\n🎉 OSS配置测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        return False

def show_oss_setup_guide():
    """显示OSS设置指南"""
    print("\n📋 OSS快速设置指南:")
    print("-" * 30)
    print("1. 在config.py中添加OSS配置类:")
    print("   class OSSConfig:")
    print("       ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'")
    print("       ACCESS_KEY_SECRET = 'YOUR_ACCESS_KEY_SECRET'")
    print("       ENDPOINT = 'oss-cn-beijing.aliyuncs.com'")
    print("       BUCKET_NAME = 'your-bucket-name'")
    print("       # ... 其他配置")
    print("")
    print("2. 安装OSS依赖:")
    print("   pip install oss2")
    print("")
    print("3. 上传表情包到OSS (assets/目录结构)")
    print("")
    print("4. 构建元数据:")
    print("   python oss_metadata_builder.py")
    print("")
    print("5. 启动OSS版API:")
    print("   python oss_api_server.py")
    print("")
    print("📚 详细说明请查看: OSS部署指南.md")

if __name__ == "__main__":
    success = test_oss_config()
    
    if not success:
        show_oss_setup_guide()