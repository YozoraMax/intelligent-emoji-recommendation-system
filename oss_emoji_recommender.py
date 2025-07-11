#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于OSS的智能表情包推荐系统
使用JSON元数据进行表情包匹配和推荐
"""

import os
import json
import random
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# 导入配置
from config import (
    AlgorithmConfig, RecommendConfig, EmotionConfig, 
    OSSConfig, MatchingConfig
)

# 导入OSS元数据构建器
from oss_metadata_builder import OSSMetadataBuilder

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSSEmojiRecommender:
    """基于OSS的表情包推荐器"""
    
    def __init__(self, auto_load_metadata: bool = True):
        """
        初始化推荐器
        
        Args:
            auto_load_metadata: 是否自动加载元数据
        """
        self.emoji_metadata: Dict[str, List[str]] = {}
        self.emotion_keywords = EmotionConfig.EMOTION_KEYWORDS
        
        # 统计信息
        self.stats = {
            'total_categories': 0,
            'total_emoji_urls': 0,
            'metadata_loaded_at': None,
            'using_oss': True
        }
        
        if auto_load_metadata:
            self.load_metadata()
    
    def load_metadata(self, force_rebuild: bool = False) -> bool:
        """
        加载表情包元数据
        
        Args:
            force_rebuild: 是否强制重新构建元数据
            
        Returns:
            是否成功加载
        """
        try:
            logger.info("📥 开始加载表情包元数据...")
            
            # 创建OSS元数据构建器
            builder = OSSMetadataBuilder()
            
            # 构建或加载元数据
            self.emoji_metadata = builder.build_and_save_metadata(force_rebuild=force_rebuild)
            
            if self.emoji_metadata:
                # 更新统计信息
                self.stats.update({
                    'total_categories': len(self.emoji_metadata),
                    'total_emoji_urls': sum(len(urls) for urls in self.emoji_metadata.values()),
                    'metadata_loaded_at': datetime.now().isoformat()
                })
                
                logger.info(f"✅ 元数据加载成功")
                logger.info(f"📁 分类数量: {self.stats['total_categories']}")
                logger.info(f"🎯 表情包数量: {self.stats['total_emoji_urls']}")
                
                return True
            else:
                logger.warning("⚠️  加载的元数据为空")
                return False
                
        except Exception as e:
            logger.error(f"❌ 加载元数据失败: {e}")
            return False
    
    def calculate_keyword_score(self, user_text: str, category: str) -> float:
        """
        计算关键词匹配分数
        
        Args:
            user_text: 用户输入文本
            category: 表情包分类
            
        Returns:
            关键词匹配分数 (0-1)
        """
        user_text_lower = user_text.lower()
        category_lower = category.lower()
        
        # 1. 直接匹配分类名
        if category_lower in user_text_lower:
            return MatchingConfig.DIRECT_MATCH_BONUS
        
        # 2. 情绪关键词匹配
        max_emotion_score = 0.0
        
        for emotion, keywords in self.emotion_keywords.items():
            # 检查情绪是否在分类名中
            if emotion in category_lower:
                # 计算该情绪关键词的匹配度
                emotion_score = 0.0
                for keyword in keywords:
                    if keyword in user_text_lower:
                        emotion_score += 1.0
                
                # 归一化分数
                if keywords:
                    emotion_score = min(emotion_score / len(keywords), 1.0)
                    emotion_score *= MatchingConfig.EMOTION_MATCH_BONUS
                    max_emotion_score = max(max_emotion_score, emotion_score)
        
        return max_emotion_score
    
    def calculate_category_scores(self, user_text: str) -> List[Tuple[str, float]]:
        """
        计算所有分类的匹配分数
        
        Args:
            user_text: 用户输入文本
            
        Returns:
            [(category, score), ...] 按分数降序排列
        """
        category_scores = []
        
        for category in self.emoji_metadata.keys():
            # 计算关键词分数
            keyword_score = self.calculate_keyword_score(user_text, category)
            
            # 当前版本主要使用关键词匹配
            # 后续可以集成语义匹配功能
            final_score = keyword_score
            
            category_scores.append((category, final_score))
        
        # 按分数降序排列
        category_scores.sort(key=lambda x: x[1], reverse=True)
        
        return category_scores
    
    def select_random_emoji(self, category: str) -> str:
        """
        从指定分类中随机选择一个表情包URL
        
        Args:
            category: 表情包分类
            
        Returns:
            表情包URL
        """
        if category not in self.emoji_metadata:
            raise ValueError(f"分类不存在: {category}")
        
        urls = self.emoji_metadata[category]
        if not urls:
            raise ValueError(f"分类 {category} 中没有表情包")
        
        return random.choice(urls)
    
    def recommend(self, user_text: str, top_k: int = None) -> List[Dict]:
        """
        推荐表情包
        
        Args:
            user_text: 用户输入文本
            top_k: 返回推荐数量
            
        Returns:
            推荐结果列表
        """
        if not self.emoji_metadata:
            raise RuntimeError("表情包元数据未加载，请先调用 load_metadata()")
        
        # 验证和设置推荐数量
        if top_k is None:
            top_k = RecommendConfig.DEFAULT_TOP_K
        
        RecommendConfig.validate_top_k(top_k)
        
        # 计算分类分数
        category_scores = self.calculate_category_scores(user_text)
        
        # 选择推荐结果
        recommendations = []
        used_categories = set()
        
        for i, (category, score) in enumerate(category_scores):
            if len(recommendations) >= top_k:
                break
            
            # 跳过分数为0的分类
            if score <= 0:
                continue
            
            # 避免重复分类
            if category in used_categories:
                continue
            
            try:
                # 随机选择表情包URL
                emoji_url = self.select_random_emoji(category)
                
                # 构建推荐结果
                recommendation = {
                    'url': emoji_url,
                    'category': category,
                    'score': round(score, 3),
                    'keyword_score': round(score, 3),  # 当前版本主要使用关键词分数
                    'semantic_score': 0.0,             # 占位符，后续可扩展
                    'keyword_weight': AlgorithmConfig.KEYWORD_WEIGHT,
                    'semantic_weight': AlgorithmConfig.SEMANTIC_WEIGHT,
                    'rank': len(recommendations) + 1,
                    'source': 'oss'
                }
                
                recommendations.append(recommendation)
                used_categories.add(category)
                
            except ValueError as e:
                logger.warning(f"⚠️  跳过分类 {category}: {e}")
                continue
        
        # 如果推荐数量不足，随机补充
        if len(recommendations) < top_k:
            remaining_count = top_k - len(recommendations)
            remaining_categories = [cat for cat in self.emoji_metadata.keys() 
                                  if cat not in used_categories and self.emoji_metadata[cat]]
            
            if remaining_categories:
                random.shuffle(remaining_categories)
                
                for category in remaining_categories[:remaining_count]:
                    try:
                        emoji_url = self.select_random_emoji(category)
                        
                        recommendation = {
                            'url': emoji_url,
                            'category': category,
                            'score': 0.1,  # 随机补充的低分
                            'keyword_score': 0.1,
                            'semantic_score': 0.0,
                            'keyword_weight': AlgorithmConfig.KEYWORD_WEIGHT,
                            'semantic_weight': AlgorithmConfig.SEMANTIC_WEIGHT,
                            'rank': len(recommendations) + 1,
                            'source': 'oss_random'
                        }
                        
                        recommendations.append(recommendation)
                        
                    except ValueError:
                        continue
        
        logger.info(f"🎯 为文本 '{user_text}' 推荐了 {len(recommendations)} 个表情包")
        
        return recommendations
    
    def get_stats(self) -> Dict:
        """获取系统统计信息"""
        return {
            **self.stats,
            'categories': list(self.emoji_metadata.keys()),
            'oss_bucket': OSSConfig.BUCKET_NAME,
            'oss_endpoint': OSSConfig.ENDPOINT,
            'cache_file': OSSConfig.METADATA_CACHE_FILE
        }
    
    def refresh_metadata(self) -> bool:
        """刷新元数据（强制重新构建）"""
        logger.info("🔄 强制刷新表情包元数据...")
        return self.load_metadata(force_rebuild=True)

def main():
    """主函数 - 测试推荐功能"""
    print("🎉 基于OSS的智能表情包推荐系统")
    print("=" * 50)
    
    try:
        # 创建推荐器
        recommender = OSSEmojiRecommender()
        
        # 检查是否成功加载元数据
        if not recommender.emoji_metadata:
            print("❌ 元数据加载失败，请检查OSS配置")
            return
        
        # 显示系统信息
        stats = recommender.get_stats()
        print(f"📊 系统信息:")
        print(f"   📁 表情包分类: {stats['total_categories']}")
        print(f"   🎯 表情包数量: {stats['total_emoji_urls']}")
        print(f"   🌐 OSS Bucket: {stats['oss_bucket']}")
        
        # 测试用例
        test_cases = [
            "今天心情很好，特别开心",
            "工作太累了，想要休息",
            "这个蛋糕看起来很好吃",
            "哈哈哈，太有趣了",
            "气死我了，很讨厌",
            "谢谢你的帮助"
        ]
        
        print("\n🧪 推荐测试:")
        print("-" * 40)
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n{i}. 输入: {text}")
            
            try:
                recommendations = recommender.recommend(text, top_k=2)
                
                if recommendations:
                    for rec in recommendations:
                        print(f"   🎯 分类: {rec['category']}")
                        print(f"   🔗 URL: {rec['url'][:60]}...")
                        print(f"   📊 分数: {rec['score']}")
                        print(f"   🏆 排名: {rec['rank']}")
                        print()
                else:
                    print("   ⚠️  未找到匹配的表情包")
                    
            except Exception as e:
                print(f"   ❌ 推荐失败: {e}")
        
        print("🎊 测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    main()