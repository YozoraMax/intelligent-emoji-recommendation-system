#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能表情包推荐系统 - 配置文件
包含算法权重、默认参数和系统设置
"""

import os

# ============== 算法权重配置 ==============
class AlgorithmConfig:
    """算法相关配置"""
    
    # 混合匹配算法权重 (总和应为1.0)
    KEYWORD_WEIGHT = 0.7        # 关键词匹配权重 70%
    SEMANTIC_WEIGHT = 0.3       # 语义匹配权重 30%
    
    # 验证权重总和
    @classmethod
    def validate_weights(cls):
        """验证权重配置是否合法"""
        total_weight = cls.KEYWORD_WEIGHT + cls.SEMANTIC_WEIGHT
        if abs(total_weight - 1.0) > 0.001:  # 允许小误差
            raise ValueError(f"权重总和必须为1.0，当前为{total_weight}")
        return True

# ============== 推荐参数配置 ==============
class RecommendConfig:
    """推荐相关配置"""
    
    # 默认推荐数量
    DEFAULT_TOP_K = 1           # 默认返回1个推荐结果
    MAX_TOP_K = 10              # 最大推荐数量限制
    MIN_TOP_K = 1               # 最小推荐数量限制
    
    # 搜索相关参数
    SEARCH_MULTIPLIER = 3       # 搜索倍数，用于扩大候选集
    
    @classmethod
    def validate_top_k(cls, top_k):
        """验证top_k参数是否合法"""
        if not isinstance(top_k, int):
            raise TypeError("top_k必须是整数")
        if top_k < cls.MIN_TOP_K:
            raise ValueError(f"top_k不能小于{cls.MIN_TOP_K}")
        if top_k > cls.MAX_TOP_K:
            raise ValueError(f"top_k不能大于{cls.MAX_TOP_K}")
        return True

# ============== 模型配置 ==============
class ModelConfig:
    """模型相关配置"""
    
    # 默认sentence-transformers模型
    DEFAULT_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
    
    # 备选模型列表
    ALTERNATIVE_MODELS = [
        'all-MiniLM-L6-v2',                       # 轻量级模型
        'all-mpnet-base-v2',                      # 高精度模型
        'paraphrase-multilingual-MiniLM-L12-v2'   # 多语言模型（推荐）
    ]
    
    # TF-IDF配置
    TFIDF_MAX_FEATURES = 1000   # TF-IDF最大特征数
    USE_TFIDF_DEFAULT = True    # 默认是否使用TF-IDF

# ============== 文件路径配置 ==============
class PathConfig:
    """路径相关配置"""
    
    # 默认目录
    DEFAULT_ASSETS_DIR = 'assets'       # 默认表情包目录
    DEFAULT_MODELS_DIR = 'models'       # 默认模型保存目录
    
    # 支持的文件格式
    SUPPORTED_IMAGE_FORMATS = ['*.gif', '*.jpg', '*.jpeg', '*.png', '*.webp']
    
    # 模型文件名
    FAISS_INDEX_FILE = 'emoji.faiss'
    METADATA_FILE = 'emoji_data.pkl'

# ============== 匹配阈值配置 ==============
class MatchingConfig:
    """匹配相关配置"""
    
    # 关键词匹配阈值
    DIRECT_MATCH_BONUS = 1.0        # 直接匹配加分
    EMOTION_MATCH_BONUS = 0.5       # 情绪匹配加分
    
    # 语义匹配相关
    MIN_SEMANTIC_SCORE = 0.0        # 最小语义分数
    MAX_SEMANTIC_SCORE = 1.0        # 最大语义分数

# ============== 情绪关键词配置 ==============
class EmotionConfig:
    """情绪关键词配置"""
    
    # 情绪关键词字典
    EMOTION_KEYWORDS = {
        '开心': ['开心', '高兴', '快乐', '兴奋', '愉快', '爽', '哈哈', '嘻嘻', '嘿嘿', '舒服', '舒适', '棒', '赞', '好'],
        '愤怒': ['愤怒', '生气', '恼火', '暴躁', '怒', '火大', '抓狂', '爆炸', '气死', '讨厌', '烦', '恶心'],
        '悲伤': ['悲伤', '难过', '伤心', '沮丧', '郁闷', '失落', '哭泣', '痛苦', '哭', '眼泪', '委屈', '可怜'],
        '撒娇': ['撒娇', '可爱', '萌', '求', '要', '关注', '抱抱', '亲亲', '么么', '宝贝', '乖', '求求'],
        '疲惫': ['累', '疲惫', '困', '倦怠', '厌世', '无语', '躺', '睡', '休息', '太累了'],
        '好吃': ['吃', '好吃', '美食', '蛋糕', '香', '饿了', '想吃', '美味', '香甜', '流口水', '馋'],
        '害羞': ['害羞', '脸红', '不好意思', '羞涩', '羞羞', '害羞了', '红脸'],
        '赞同': ['支持', '赞同', '同意', '对', '没错', '棒', '好的', '是的', '确实', '点赞'],
        '鼓励': ['安慰', '鼓励', '加油', '没事', '别哭', '抱抱', '不要紧', '会好的', '坚持'],
    }

# ============== 阿里云OSS配置 ==============
class OSSConfig:
    """阿里云OSS相关配置"""
    
    # OSS认证模式配置
    USE_ECS_RAM_ROLE = os.getenv('OSS_USE_ECS_RAM_ROLE', 'true').lower() == 'true'  # 是否使用ECS RAM Role
    
    # OSS基本配置 (请根据实际情况修改)
    ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID', '')              # 阿里云AccessKey ID (当不使用RAM Role时)
    ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET', '')      # 阿里云AccessKey Secret (当不使用RAM Role时)
    ENDPOINT = 'oss-cn-beijing.aliyuncs.com'                       # OSS Endpoint，如: oss-cn-beijing.aliyuncs.com
    BUCKET_NAME = 'coze-archive'                                    # OSS Bucket名称
    
    # OSS URL配置
    CUSTOM_DOMAIN = ''              # 自定义域名（可选）
    USE_HTTPS = True                # 是否使用HTTPS
    
    # 表情包相关配置
    EMOJI_ROOT_PATH = 'sably/'     # 表情包在OSS中的根路径
    SUPPORTED_EXTENSIONS = ['.gif', '.jpg', '.jpeg', '.png', '.webp']  # 支持的文件格式
    
    # 缓存配置
    METADATA_CACHE_FILE = 'oss_emoji_metadata.json'  # 元数据缓存文件
    CACHE_EXPIRE_HOURS = 24         # 缓存过期时间（小时）
    
    @classmethod
    def get_public_url(cls, object_key: str) -> str:
        """
        生成OSS对象的公共访问URL
        
        Args:
            object_key: OSS对象键名
            
        Returns:
            完整的公共访问URL
        """
        if cls.CUSTOM_DOMAIN:
            # 使用自定义域名
            protocol = 'https' if cls.USE_HTTPS else 'http'
            return f"{protocol}://{cls.CUSTOM_DOMAIN.rstrip('/')}/{object_key}"
        else:
            # 使用默认OSS域名
            protocol = 'https' if cls.USE_HTTPS else 'http'
            return f"{protocol}://{cls.BUCKET_NAME}.{cls.ENDPOINT}/{object_key}"
    
    @classmethod
    def validate_config(cls):
        """验证OSS配置是否完整"""
        # 基本必需字段
        required_fields = [
            ('ENDPOINT', cls.ENDPOINT),
            ('BUCKET_NAME', cls.BUCKET_NAME)
        ]
        
        # 如果不使用ECS RAM Role，需要验证AKSK
        if not cls.USE_ECS_RAM_ROLE:
            required_fields.extend([
                ('ACCESS_KEY_ID', cls.ACCESS_KEY_ID),
                ('ACCESS_KEY_SECRET', cls.ACCESS_KEY_SECRET)
            ])
        
        missing_fields = [name for name, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(f"OSS配置不完整，缺少字段: {', '.join(missing_fields)}")
        
        return True
    
    @classmethod
    def get_auth_info(cls) -> str:
        """获取认证方式信息"""
        if cls.USE_ECS_RAM_ROLE:
            return "🔐 认证方式: ECS RAM Role"
        else:
            return f"🔐 认证方式: AKSK (AccessKey: {cls.ACCESS_KEY_ID[:8]}...)"

# ============== API认证配置 ==============
class AuthConfig:
    """API认证相关配置"""
    
    # 是否启用Basic Auth
    ENABLE_AUTH = True
    
    # Basic Auth用户名和密码
    USERNAME = os.getenv('API_USERNAME', 'emoji_user')                      # API访问用户名
    PASSWORD = os.getenv('API_PASSWORD', 'emoji_pass_2025')                 # API访问密码
    
    # 认证失败提示信息
    AUTH_FAILED_MESSAGE = "需要提供有效的用户名和密码"
    
    # 免认证的路径（不需要认证即可访问）
    PUBLIC_PATHS = [
        '/',                    # 根路径
        '/health',              # 健康检查
        '/docs',                # API文档
        '/openapi.json',        # OpenAPI规范
        '/redoc'                # ReDoc文档
    ]
    
    @classmethod
    def validate_credentials(cls, username: str, password: str) -> bool:
        """
        验证用户名和密码
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            验证是否通过
        """
        return username == cls.USERNAME and password == cls.PASSWORD
    
    @classmethod
    def is_public_path(cls, path: str) -> bool:
        """
        检查路径是否无需认证
        
        Args:
            path: 请求路径
            
        Returns:
            是否为公共路径
        """
        return path in cls.PUBLIC_PATHS

# ============== 日志配置 ==============
class LogConfig:
    """日志相关配置"""
    
    # 是否启用详细日志
    VERBOSE_LOGGING = True
    
    # 日志级别
    LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# ============== 配置验证 ==============
def validate_all_configs():
    """验证所有配置的合法性"""
    try:
        AlgorithmConfig.validate_weights()
        print("✅ 算法权重配置验证通过")
        
        RecommendConfig.validate_top_k(RecommendConfig.DEFAULT_TOP_K)
        print("✅ 推荐参数配置验证通过")
        
        print("✅ 所有配置验证通过")
        return True
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

# ============== 配置信息显示 ==============
def show_config_summary():
    """显示配置摘要信息"""
    print("=" * 60)
    print("🔧 智能表情包推荐系统 - 配置信息")
    print("=" * 60)
    print(f"📊 算法权重:")
    print(f"   - 关键词匹配: {AlgorithmConfig.KEYWORD_WEIGHT:.1%}")
    print(f"   - 语义匹配: {AlgorithmConfig.SEMANTIC_WEIGHT:.1%}")
    print(f"🎯 推荐设置:")
    print(f"   - 默认推荐数量: {RecommendConfig.DEFAULT_TOP_K}")
    print(f"   - 最大推荐数量: {RecommendConfig.MAX_TOP_K}")
    print(f"🤖 模型设置:")
    print(f"   - 默认模型: {ModelConfig.DEFAULT_MODEL}")
    print(f"   - 使用TF-IDF: {ModelConfig.USE_TFIDF_DEFAULT}")
    print(f"📁 路径设置:")
    print(f"   - 表情包目录: {PathConfig.DEFAULT_ASSETS_DIR}")
    print(f"   - 模型目录: {PathConfig.DEFAULT_MODELS_DIR}")
    print(f"💭 情绪分类: {len(EmotionConfig.EMOTION_KEYWORDS)} 种")
    print(f"🔐 API认证:")
    print(f"   - 启用状态: {'✅ 已启用' if AuthConfig.ENABLE_AUTH else '❌ 已禁用'}")
    print(f"   - 用户名: {AuthConfig.USERNAME}")
    print(f"   - 密码: {'*' * len(AuthConfig.PASSWORD)}")
    print(f"   - 公共路径数量: {len(AuthConfig.PUBLIC_PATHS)} 个")
    print(f"☁️  OSS配置:")
    print(f"   - Bucket: {OSSConfig.BUCKET_NAME}")
    print(f"   - 地域: {OSSConfig.ENDPOINT}")
    print(f"   - 根路径: {OSSConfig.EMOJI_ROOT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    # 配置验证和信息显示
    if validate_all_configs():
        show_config_summary()