"""
指标查询 API 路由 (IndicatorAPI)
提供指标查询相关的 REST API 接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.indicator_service import get_indicator_service
from app.schemas.indicator_schema import (
    OverviewIndicator,
    LandUsageResponse,
    SurveyStatsResponse,
    SurveyCategoriesResponse,
    VillagesResponse,
    AdminDivisionTreeResponse,
)


router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/overview", response_model=OverviewIndicator)
async def get_overview(
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取核心指标概览
    
    返回 5 个核心指标：
    - 发包方总数
    - 承包方总数（总户数）
    - 已摸底户数
    - 已内业审核数
    - 已完成户数
    
    Args:
        village_code: 村级行政区划编码（可选），用于筛选特定村的指标
        db: 数据库会话
        
    Returns:
        OverviewIndicator: 核心指标数据
    """
    service = get_indicator_service(db)
    return service.get_overview(village_code)


@router.get("/land-usage", response_model=LandUsageResponse)
async def get_land_usage(
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取地块用途统计
    
    返回种植业/林业/畜牧业/渔业等地块数量统计
    
    Args:
        village_code: 村级行政区划编码（可选）
        db: 数据库会话
        
    Returns:
        LandUsageResponse: 用途统计数据
    """
    service = get_indicator_service(db)
    return service.get_land_usage(village_code)


@router.get("/survey-stats", response_model=SurveyStatsResponse)
async def get_survey_stats(
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取摸底填报统计（按村组分组）
    
    返回按村组统计的已上报户数 vs 已审核户数（分组柱状图数据）
    
    Args:
        village_code: 村级行政区划编码（可选）
        db: 数据库会话
        
    Returns:
        SurveyStatsResponse: 摸底填报统计数据
    """
    service = get_indicator_service(db)
    return service.get_survey_stats(village_code)


@router.get("/survey-categories", response_model=SurveyCategoriesResponse)
async def get_survey_categories(
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取填报分类统计（饼图数据）
    
    返回分户保留户/新增户/地块转/有变化/无变化的占比
    
    Args:
        village_code: 村级行政区划编码（可选）
        db: 数据库会话
        
    Returns:
        SurveyCategoriesResponse: 填报分类数据
    """
    service = get_indicator_service(db)
    return service.get_survey_categories(village_code)


@router.get("/villages", response_model=VillagesResponse)
async def get_villages(
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取村组指标列表
    
    返回各村组的详细指标数据
    
    Args:
        village_code: 村级行政区划编码（可选）
        db: 数据库会话
        
    Returns:
        VillagesResponse: 村组指标列表
    """
    service = get_indicator_service(db)
    return service.get_villages(village_code)


@router.get("/admin-divisions/tree", response_model=AdminDivisionTreeResponse)
async def get_admin_division_tree(
    db: Session = Depends(get_db),
):
    """
    获取行政区划树
    
    返回完整的行政区划树结构（县→镇→村→组）
    
    Args:
        db: 数据库会话
        
    Returns:
        AdminDivisionTreeResponse: 行政区划树
    """
    service = get_indicator_service(db)
    return service.get_admin_division_tree()


@router.post("/refresh-cache")
async def refresh_cache(
    db: Session = Depends(get_db),
):
    """
    手动刷新指标缓存
    
    清除所有指标缓存，下次请求时重新计算
    
    Args:
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = get_indicator_service(db)
    success = service.refresh_all_cache()
    
    if success:
        return {"message": "缓存已刷新", "success": True}
    else:
        raise HTTPException(status_code=500, detail="缓存刷新失败")


@router.get("/cache-stats")
async def get_cache_stats():
    """
    获取缓存统计信息
    
    Returns:
        缓存统计信息
    """
    from app.services.cache_service import cache_service
    return cache_service.get_cache_stats()