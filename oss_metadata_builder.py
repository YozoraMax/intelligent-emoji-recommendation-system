#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSS表情包元数据构建器
遍历阿里云OSS Bucket，构建表情包元数据JSON
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

try:
    import oss2
except ImportError:
    print("❌ 请安装OSS依赖: pip install oss2")
    exit(1)

from config import OSSConfig, EmotionConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSSMetadataBuilder:
    """OSS表情包元数据构建器"""
    
    def __init__(self):
        """初始化OSS客户端"""
        try:
            # 验证OSS配置
            OSSConfig.validate_config()
            
            # 根据配置选择认证方式
            if OSSConfig.USE_ECS_RAM_ROLE:
                # 使用ECS RAM Role认证
                try:
                    from oss2.credentials import EcsRamRoleCredentialsProvider
                    from oss2 import ProviderAuth
                    
                    logger.info("🔐 使用ECS RAM Role认证")
                    
                    # 创建ECS RAM Role凭证提供者（自动获取角色）
                    credentials_provider = EcsRamRoleCredentialsProvider()
                    
                    # 创建Provider认证对象
                    auth = ProviderAuth(credentials_provider)
                    
                except ImportError:
                    logger.error("❌ ECS RAM Role认证需要oss2 >= 2.14.0")
                    logger.error("请升级OSS SDK: pip install --upgrade oss2")
                    raise
                except Exception as e:
                    logger.error(f"❌ ECS RAM Role认证失败: {e}")
                    logger.error("请确保ECS实例已正确配置RAM角色")
                    raise
                
            else:
                # 使用传统的AKSK认证
                logger.info("🔐 使用AKSK认证")
                auth = oss2.Auth(OSSConfig.ACCESS_KEY_ID, OSSConfig.ACCESS_KEY_SECRET)
            
            # 创建Bucket对象
            self.bucket = oss2.Bucket(auth, OSSConfig.ENDPOINT, OSSConfig.BUCKET_NAME)
            
            logger.info(f"✅ OSS客户端初始化成功")
            logger.info(f"📦 Bucket: {OSSConfig.BUCKET_NAME}")
            logger.info(f"🌐 Endpoint: {OSSConfig.ENDPOINT}")
            logger.info(OSSConfig.get_auth_info())
            
        except Exception as e:
            logger.error(f"❌ OSS客户端初始化失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试OSS连接"""
        try:
            # 尝试列出bucket信息
            bucket_info = self.bucket.get_bucket_info()
            logger.info(f"✅ OSS连接测试成功")
            logger.info(f"📊 Bucket创建时间: {bucket_info.creation_date}")
            return True
        except Exception as e:
            logger.error(f"❌ OSS连接测试失败: {e}")
            return False
    
    def list_emoji_files(self) -> List[Dict]:
        """
        遍历OSS bucket，获取所有表情包文件信息
        
        Returns:
            表情包文件信息列表
        """
        emoji_files = []
        
        try:
            logger.info(f"🔍 开始遍历OSS Bucket中的表情包文件...")
            logger.info(f"📁 搜索路径: {OSSConfig.EMOJI_ROOT_PATH}")
            
            # 遍历指定路径下的所有对象
            for obj in oss2.ObjectIterator(self.bucket, prefix=OSSConfig.EMOJI_ROOT_PATH):
                object_key = obj.key
                
                # 跳过目录（以/结尾的对象）
                if object_key.endswith('/'):
                    continue
                
                # 检查文件扩展名
                file_ext = Path(object_key).suffix.lower()
                if file_ext not in OSSConfig.SUPPORTED_EXTENSIONS:
                    continue
                
                # 解析目录结构，提取分类信息
                relative_path = object_key[len(OSSConfig.EMOJI_ROOT_PATH):] if object_key.startswith(OSSConfig.EMOJI_ROOT_PATH) else object_key
                path_parts = relative_path.split('/')
                
                if len(path_parts) >= 2:
                    category = path_parts[0]  # 第一级目录作为分类
                    filename = path_parts[-1]  # 文件名
                    
                    # 生成公共访问URL
                    public_url = OSSConfig.get_public_url(object_key)
                    
                    # 处理时间戳 - OSS返回的时间戳可能是int或datetime对象
                    last_modified_str = ''
                    if obj.last_modified:
                        if isinstance(obj.last_modified, datetime):
                            last_modified_str = obj.last_modified.isoformat()
                        elif isinstance(obj.last_modified, (int, float)):
                            last_modified_str = datetime.fromtimestamp(obj.last_modified).isoformat()
                        else:
                            last_modified_str = str(obj.last_modified)
                    
                    file_info = {
                        'object_key': object_key,
                        'category': category,
                        'filename': filename,
                        'url': public_url,
                        'size': obj.size,
                        'last_modified': last_modified_str,
                        'file_extension': file_ext
                    }
                    
                    emoji_files.append(file_info)
                    
                    if len(emoji_files) % 50 == 0:
                        logger.info(f"📄 已发现 {len(emoji_files)} 个表情包文件...")
            
            logger.info(f"✅ 遍历完成，共发现 {len(emoji_files)} 个表情包文件")
            return emoji_files
            
        except Exception as e:
            logger.error(f"❌ 遍历OSS失败: {e}")
            raise
    
    def build_metadata_json(self, emoji_files: List[Dict]) -> Dict[str, List[str]]:
        """
        构建表情包元数据JSON
        
        Args:
            emoji_files: 表情包文件信息列表
            
        Returns:
            {category: [url1, url2, ...]} 格式的元数据字典
        """
        metadata = {}
        category_stats = {}
        
        logger.info("🔨 开始构建元数据JSON...")
        
        for file_info in emoji_files:
            category = file_info['category']
            url = file_info['url']
            
            # 初始化分类
            if category not in metadata:
                metadata[category] = []
                category_stats[category] = 0
            
            # 添加URL到对应分类
            metadata[category].append(url)
            category_stats[category] += 1
        
        # 对每个分类的URL进行排序
        for category in metadata:
            metadata[category].sort()
        
        # 输出统计信息
        logger.info("📊 表情包分类统计:")
        total_files = 0
        for category, count in sorted(category_stats.items()):
            logger.info(f"   📁 {category}: {count} 个文件")
            total_files += count
        
        logger.info(f"📈 总计: {len(metadata)} 个分类, {total_files} 个表情包")
        
        return metadata
    
    def save_metadata(self, metadata: Dict[str, List[str]], filepath: str = None) -> str:
        """
        保存元数据到JSON文件
        
        Args:
            metadata: 元数据字典
            filepath: 保存路径（可选）
            
        Returns:
            保存的文件路径
        """
        if filepath is None:
            filepath = OSSConfig.METADATA_CACHE_FILE
        
        try:
            # 添加元信息
            full_metadata = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_categories': len(metadata),
                    'total_files': sum(len(urls) for urls in metadata.values()),
                    'oss_bucket': OSSConfig.BUCKET_NAME,
                    'oss_endpoint': OSSConfig.ENDPOINT,
                    'emoji_root_path': OSSConfig.EMOJI_ROOT_PATH
                },
                'categories': metadata
            }
            
            # 保存JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 元数据已保存到: {filepath}")
            logger.info(f"📁 文件大小: {os.path.getsize(filepath)} 字节")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 保存元数据失败: {e}")
            raise
    
    def load_cached_metadata(self, filepath: str = None) -> Optional[Dict]:
        """
        加载缓存的元数据
        
        Args:
            filepath: 元数据文件路径
            
        Returns:
            元数据字典或None
        """
        if filepath is None:
            filepath = OSSConfig.METADATA_CACHE_FILE
        
        if not os.path.exists(filepath):
            logger.info(f"📄 缓存文件不存在: {filepath}")
            return None
        
        try:
            # 检查文件是否过期
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            expire_time = datetime.now() - timedelta(hours=OSSConfig.CACHE_EXPIRE_HOURS)
            
            if file_mtime < expire_time:
                logger.info(f"⏰ 缓存文件已过期: {filepath}")
                return None
            
            # 加载JSON文件
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ 成功加载缓存元数据: {filepath}")
            
            if 'metadata' in data:
                logger.info(f"📊 缓存信息:")
                metadata_info = data['metadata']
                logger.info(f"   生成时间: {metadata_info.get('generated_at', 'Unknown')}")
                logger.info(f"   分类数量: {metadata_info.get('total_categories', 'Unknown')}")
                logger.info(f"   文件数量: {metadata_info.get('total_files', 'Unknown')}")
            
            return data.get('categories', data)
            
        except Exception as e:
            logger.error(f"❌ 加载缓存元数据失败: {e}")
            return None
    
    def build_and_save_metadata(self, force_rebuild: bool = False) -> Dict[str, List[str]]:
        """
        构建并保存元数据（支持缓存）
        
        Args:
            force_rebuild: 是否强制重新构建
            
        Returns:
            元数据字典
        """
        # 尝试加载缓存
        if not force_rebuild:
            cached_metadata = self.load_cached_metadata()
            if cached_metadata:
                logger.info("🎯 使用缓存的元数据")
                return cached_metadata
        
        logger.info("🔄 开始重新构建元数据...")
        
        # 测试OSS连接
        if not self.test_connection():
            raise ConnectionError("无法连接到OSS服务")
        
        # 遍历OSS获取文件列表
        emoji_files = self.list_emoji_files()
        
        if not emoji_files:
            logger.warning("⚠️  未发现任何表情包文件")
            return {}
        
        # 构建元数据
        metadata = self.build_metadata_json(emoji_files)
        
        # 保存元数据
        self.save_metadata(metadata)
        
        return metadata

def main():
    """主函数 - 元数据构建入口"""
    print("🎉 OSS表情包元数据构建器")
    print("=" * 50)
    
    try:
        # 检查OSS配置
        if not all([OSSConfig.ACCESS_KEY_ID, OSSConfig.ACCESS_KEY_SECRET, 
                   OSSConfig.ENDPOINT, OSSConfig.BUCKET_NAME]):
            print("❌ OSS配置不完整，请在config.py中配置:")
            print("   - ACCESS_KEY_ID")
            print("   - ACCESS_KEY_SECRET") 
            print("   - ENDPOINT")
            print("   - BUCKET_NAME")
            return
        
        # 创建构建器
        builder = OSSMetadataBuilder()
        
        # 构建元数据
        metadata = builder.build_and_save_metadata(force_rebuild=True)
        
        if metadata:
            print("\n🎊 元数据构建完成！")
            print(f"📁 分类数量: {len(metadata)}")
            print(f"📄 文件数量: {sum(len(urls) for urls in metadata.values())}")
            print(f"💾 保存位置: {OSSConfig.METADATA_CACHE_FILE}")
            
            # 显示前几个分类作为示例
            print("\n📋 分类预览:")
            for i, (category, urls) in enumerate(list(metadata.items())[:3]):
                print(f"   {i+1}. {category}: {len(urls)} 个表情包")
                if urls:
                    print(f"      示例: {urls[0][:80]}...")
        else:
            print("⚠️  未构建到任何元数据")
            
    except Exception as e:
        logger.error(f"❌ 构建失败: {e}")
        print(f"\n❌ 构建失败: {e}")

if __name__ == "__main__":
    main()