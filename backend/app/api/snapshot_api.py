"""
快照 API 路由
提供快照查询、趋势数据、对比功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.snapshot_service import get_snapshot_service, SnapshotService
from app.services.snapshot_service import (
    SnapshotListResponse,
    TrendDataResponse,
    ComparisonResponse,
)


router = APIRouter(prefix="/snapshot", tags=["snapshot"])


@router.get("/list", response_model=SnapshotListResponse)
async def get_snapshots(
    level: str = Query(default="global", description="层级"),
    code: str = Query(default="", description="行政区划编码"),
    db: Session = Depends(get_db),
):
    """
    获取快照列表
    
    返回所有导入快照的历史记录
    """
    service = get_snapshot_service(db)
    return service.get_snapshots_list(level, code)


@router.get("/trend", response_model=TrendDataResponse)
async def get_trend(
    period: str = Query(default="day", description="聚合周期（day/week）"),
    metric_type: str = Query(default="contractor_count", description="指标类型"),
    level: str = Query(default="global", description="层级"),
    code: str = Query(default="", description="行政区划编码"),
    days: int = Query(default=30, description="查询天数"),
    db: Session = Depends(get_db),
):
    """
    获取趋势数据
    
    返回指定指标的历史趋势数据，支持按日或按周聚合
    """
    service = get_snapshot_service(db)
    return service.get_trend_data(period, metric_type, level, code, days)


@router.get("/compare", response_model=ComparisonResponse)
async def compare_snapshots(
    base_id: int = Query(..., description="基准快照ID"),
    compare_id: int = Query(..., description="对比快照ID"),
    db: Session = Depends(get_db),
):
    """
    对比两个快照
    
    返回两个快照的指标差异对比
    """
    service = get_snapshot_service(db)
    
    try:
        return service.compare_snapshots(base_id, compare_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))