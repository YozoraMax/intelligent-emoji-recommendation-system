#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于OSS的智能表情包推荐API服务
提供REST API接口用于OSS表情包推荐
"""

import os
import base64
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

# 导入OSS推荐系统
from oss_emoji_recommender import OSSEmojiRecommender
from config import RecommendConfig, AlgorithmConfig, OSSConfig, AuthConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局推荐器实例
recommender = None

# Basic Auth中间件
async def basic_auth_middleware(request: Request, call_next):
    """
    Basic Auth认证中间件
    
    Args:
        request: FastAPI请求对象
        call_next: 下一个中间件或路由处理器
        
    Returns:
        响应对象
    """
    # 如果未启用认证，直接通过
    if not AuthConfig.ENABLE_AUTH:
        return await call_next(request)
    
    # 检查是否为公共路径
    if AuthConfig.is_public_path(request.url.path):
        return await call_next(request)
    
    # 获取Authorization头
    authorization = request.headers.get("authorization")
    
    if not authorization or not authorization.startswith("Basic "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "认证失败",
                "message": AuthConfig.AUTH_FAILED_MESSAGE,
                "detail": "请提供Basic Auth认证信息"
            },
            headers={"WWW-Authenticate": "Basic"}
        )
    
    try:
        # 解码Basic Auth
        encoded_credentials = authorization.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        
        # 验证用户名和密码
        if not AuthConfig.validate_credentials(username, password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "认证失败",
                    "message": "用户名或密码错误",
                    "detail": "请检查您的登录凭据"
                },
                headers={"WWW-Authenticate": "Basic"}
            )
        
        # 认证成功，继续处理请求
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Basic Auth认证过程中发生错误: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "认证失败",
                "message": "认证信息格式错误",
                "detail": str(e)
            },
            headers={"WWW-Authenticate": "Basic"}
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global recommender
    
    # 启动时初始化推荐器
    logger.info("🚀 正在初始化基于OSS的智能表情包推荐系统...")
    try:
        # 检查OSS配置
        try:
            OSSConfig.validate_config()
            logger.info("✅ OSS配置验证通过")
        except ValueError as e:
            logger.error(f"❌ OSS配置错误: {e}")
            raise
        
        # 创建OSS推荐器
        recommender = OSSEmojiRecommender(auto_load_metadata=True)
        
        if recommender.emoji_metadata:
            logger.info("✅ OSS表情包推荐系统初始化完成")
            stats = recommender.get_stats()
            logger.info(f"📁 加载分类数量: {stats['total_categories']}")
            logger.info(f"🎯 表情包数量: {stats['total_emoji_urls']}")
        else:
            logger.error("❌ 表情包元数据加载失败")
            raise RuntimeError("表情包元数据加载失败")
        
        # 显示认证状态
        if AuthConfig.ENABLE_AUTH:
            logger.info(f"🔐 Basic Auth已启用 - 用户名: {AuthConfig.USERNAME}")
            logger.info(f"🚫 公共路径: {', '.join(AuthConfig.PUBLIC_PATHS)}")
        else:
            logger.info("⚠️  Basic Auth已禁用")
        
        logger.info("🎉 API服务初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("🔄 正在关闭API服务...")

# 创建FastAPI应用
app = FastAPI(
    title="基于OSS的智能表情包推荐API",
    description="基于阿里云OSS的智能表情包推荐系统API服务",
    version="2.0.0",
    lifespan=lifespan
)

# 添加Basic Auth中间件（需要在CORS中间件之前）
app.middleware("http")(basic_auth_middleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型定义
class RecommendRequest(BaseModel):
    """推荐请求模型"""
    input: str = Field(..., description="用户输入的文本", example="今天天气不错，心情很好")
    top_k: Optional[int] = Field(None, description="返回推荐数量", example=1, ge=1, le=10)

class EmojiRecommendation(BaseModel):
    """单个表情包推荐结果"""
    url: str = Field(..., description="表情包URL", example="https://bucket.oss-region.aliyuncs.com/assets/开心/emoji.gif")
    category: str = Field(..., description="表情包分类", example="开心 舒适")
    score: float = Field(..., description="推荐分数", example=0.9, ge=0.0, le=1.0)
    keyword_score: Optional[float] = Field(None, description="关键词匹配分数")
    semantic_score: Optional[float] = Field(None, description="语义匹配分数")
    keyword_weight: Optional[float] = Field(None, description="关键词权重")
    semantic_weight: Optional[float] = Field(None, description="语义权重")
    rank: Optional[int] = Field(None, description="推荐排名")
    source: Optional[str] = Field(None, description="推荐来源")

class RecommendResponse(BaseModel):
    """推荐响应模型"""
    input: str = Field(..., description="用户输入的原始文本")
    output: List[EmojiRecommendation] = Field(..., description="推荐结果列表")
    total_count: int = Field(..., description="返回结果总数")
    algorithm_config: dict = Field(..., description="当前算法配置")
    oss_info: dict = Field(..., description="OSS相关信息")

class StatusResponse(BaseModel):
    """状态响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态描述")
    stats: Optional[dict] = Field(None, description="系统统计信息")

class ConfigResponse(BaseModel):
    """配置响应模型"""
    algorithm_config: dict = Field(..., description="算法配置")
    recommend_config: dict = Field(..., description="推荐配置")
    oss_config: dict = Field(..., description="OSS配置")

# API路由定义
@app.get("/", response_model=dict)
async def root():
    """根路径 - API信息"""
    return {
        "name": "基于OSS的智能表情包推荐API",
        "version": "2.0.0",
        "description": "基于阿里云OSS的智能表情包推荐系统",
        "features": [
            "OSS云存储支持",
            "JSON元数据匹配",
            "关键词智能分析",
            "多分类表情包推荐"
        ],
        "endpoints": {
            "recommend": "/recommend - 表情包推荐",
            "status": "/status - 服务状态",
            "config": "/config - 配置信息",
            "refresh": "/refresh - 刷新元数据",
            "docs": "/docs - API文档"
        }
    }

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_emoji(request: RecommendRequest):
    """
    表情包推荐接口
    
    Args:
        request: 包含用户输入文本和可选参数的请求
    
    Returns:
        推荐结果，包含表情包URL、分类、分数等信息
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")
    
    try:
        # 获取推荐参数
        top_k = request.top_k if request.top_k is not None else RecommendConfig.DEFAULT_TOP_K
        
        # 验证top_k参数
        RecommendConfig.validate_top_k(top_k)
        
        # 执行推荐
        recommendations = recommender.recommend(request.input, top_k=top_k)
        
        # 转换为API响应格式
        output = []
        for rec in recommendations:
            emoji_rec = EmojiRecommendation(
                url=rec['url'],
                category=rec['category'],
                score=round(rec['score'], 3),
                keyword_score=round(rec.get('keyword_score', 0), 3),
                semantic_score=round(rec.get('semantic_score', 0), 3),
                keyword_weight=rec.get('keyword_weight'),
                semantic_weight=rec.get('semantic_weight'),
                rank=rec.get('rank'),
                source=rec.get('source', 'oss')
            )
            output.append(emoji_rec)
        
        # 构建响应
        response = RecommendResponse(
            input=request.input,
            output=output,
            total_count=len(output),
            algorithm_config={
                "keyword_weight": AlgorithmConfig.KEYWORD_WEIGHT,
                "semantic_weight": AlgorithmConfig.SEMANTIC_WEIGHT
            },
            oss_info={
                "bucket": OSSConfig.BUCKET_NAME,
                "endpoint": OSSConfig.ENDPOINT,
                "using_oss": True
            }
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"推荐过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="推荐服务内部错误")

@app.get("/recommend", response_model=RecommendResponse)
async def recommend_emoji_get(
    input: str = Query(..., description="用户输入的文本", example="今天天气不错，心情很好"),
    top_k: Optional[int] = Query(None, description="返回推荐数量", example=1, ge=1, le=10)
):
    """
    表情包推荐接口 (GET方法)
    
    Args:
        input: 用户输入的文本
        top_k: 返回推荐数量 (可选)
    
    Returns:
        推荐结果
    """
    request = RecommendRequest(input=input, top_k=top_k)
    return await recommend_emoji(request)

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    获取服务状态
    
    Returns:
        服务状态和统计信息
    """
    if recommender is None:
        return StatusResponse(
            status="error",
            message="推荐系统未初始化"
        )
    
    try:
        stats = recommender.get_stats()
        return StatusResponse(
            status="healthy",
            message="OSS推荐服务运行正常",
            stats=stats
        )
    except Exception as e:
        logger.error(f"获取状态时发生错误: {e}")
        return StatusResponse(
            status="error",
            message=f"获取状态失败: {str(e)}"
        )

@app.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    获取当前配置信息
    
    Returns:
        算法、推荐和OSS配置信息
    """
    return ConfigResponse(
        algorithm_config={
            "keyword_weight": AlgorithmConfig.KEYWORD_WEIGHT,
            "semantic_weight": AlgorithmConfig.SEMANTIC_WEIGHT
        },
        recommend_config={
            "default_top_k": RecommendConfig.DEFAULT_TOP_K,
            "max_top_k": RecommendConfig.MAX_TOP_K,
            "min_top_k": RecommendConfig.MIN_TOP_K
        },
        oss_config={
            "bucket": OSSConfig.BUCKET_NAME,
            "endpoint": OSSConfig.ENDPOINT,
            "emoji_root_path": OSSConfig.EMOJI_ROOT_PATH,
            "cache_file": OSSConfig.METADATA_CACHE_FILE,
            "cache_expire_hours": OSSConfig.CACHE_EXPIRE_HOURS
        }
    )

@app.post("/refresh")
async def refresh_metadata():
    """
    刷新表情包元数据
    
    Returns:
        刷新结果
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")
    
    try:
        logger.info("🔄 接收到元数据刷新请求...")
        success = recommender.refresh_metadata()
        
        if success:
            stats = recommender.get_stats()
            return {
                "success": True,
                "message": "元数据刷新成功",
                "stats": {
                    "total_categories": stats['total_categories'],
                    "total_emoji_urls": stats['total_emoji_urls'],
                    "updated_at": stats['metadata_loaded_at']
                }
            }
        else:
            raise HTTPException(status_code=500, detail="元数据刷新失败")
            
    except Exception as e:
        logger.error(f"刷新元数据时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy", 
        "timestamp": "2025-01-27",
        "service": "oss-emoji-recommender",
        "version": "2.0.0"
    }

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return HTTPException(status_code=500, detail="服务器内部错误")

if __name__ == "__main__":
    # 开发环境启动配置
    uvicorn.run(
        "oss_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )