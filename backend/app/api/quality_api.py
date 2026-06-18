"""
数据质量检测 API 路由
提供数据质量统计和错误列表查询
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.quality_service import get_quality_service, QualityService
from app.services.quality_service import (
    QualityStatsResponse,
    QualityErrorListResponse,
)


router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/check", response_model=QualityStatsResponse)
async def get_quality_check(
    db: Session = Depends(get_db),
):
    """
    获取数据质量统计
    
    返回空间重叠、面积异常、编码异常等统计数据
    """
    service = get_quality_service(db)
    return service.get_quality_stats()


@router.get("/errors", response_model=QualityErrorListResponse)
async def get_quality_errors(
    error_type: Optional[str] = Query(None, description="错误类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
):
    """
    获取质量错误列表
    
    返回详细的质量错误记录，支持按类型过滤和分页
    """
    service = get_quality_service(db)
    return service.get_quality_errors(error_type, page, size)