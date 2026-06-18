"""
数据质量检测服务 (QualityService)
提供空间重叠检测、面积异常检测、编码校验等功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models import CBDKXX, CBF, CBHT, ImportError
from pydantic import BaseModel, Field


class QualityErrorItem(BaseModel):
    """质量错误项"""
    id: int = Field(..., description="错误ID")
    error_type: str = Field(..., description="错误类型")
    severity: str = Field(..., description="严重程度（critical/warning/info）")
    table_name: str = Field(..., description="表名")
    record_code: str = Field(..., description="记录编码")
    error_message: str = Field(..., description="错误信息")
    created_at: datetime = Field(..., description="创建时间")


class QualityErrorListResponse(BaseModel):
    """质量错误列表响应"""
    items: List[QualityErrorItem] = Field(..., description="错误列表")
    total_count: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页大小")


class QualityStatsResponse(BaseModel):
    """质量统计响应"""
    # 空间重叠检测
    overlap_count: int = Field(default=0, description="空间重叠异常数")
    
    # 面积异常检测
    area_zero_count: int = Field(default=0, description="面积为0的地块数")
    area_exceed_count: int = Field(default=0, description="面积超阈值地块数")
    
    # 编码校验异常
    code_invalid_count: int = Field(default=0, description="编码格式异常数")
    
    # 其他统计
    total_errors: int = Field(default=0, description="总错误数")
    critical_count: int = Field(default=0, description="严重错误数")
    warning_count: int = Field(default=0, description="警告数")


class QualityService:
    """数据质量检测服务"""
    
    # 面积阈值（亩）
    AREA_THRESHOLD = 100.0
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_quality_stats(self) -> QualityStatsResponse:
        """
        获取数据质量统计
        
        Returns:
            质量统计数据
        """
        # 空间重叠检测（SQLite 不支持 PostGIS，使用简化逻辑）
        # 实际生产环境应使用 PostGIS ST_Overlaps
        overlap_count = 0  # 简化处理
        
        # 面积为0的地块数
        area_zero_count = self.db.query(func.count(CBDKXX.id)).filter(
            or_(
                CBDKXX.htmjm == 0,
                CBDKXX.scmjm == 0,
                CBDKXX.htmjm.is_(None),
                CBDKXX.scmjm.is_(None),
            )
        ).scalar() or 0
        
        # 面积超阈值地块数
        area_exceed_count = self.db.query(func.count(CBDKXX.id)).filter(
            or_(
                CBDKXX.htmjm > self.AREA_THRESHOLD,
                CBDKXX.scmjm > self.AREA_THRESHOLD,
            )
        ).scalar() or 0
        
        # 编码格式异常数
        # 承包方编码应为18位
        cbf_invalid = self.db.query(func.count(CBF.cbfbm)).filter(
            or_(
                func.length(CBF.cbfbm) != 18,
                CBF.cbfbm.is_(None),
            )
        ).scalar() or 0
        
        # 地块编码应为19位
        dk_invalid = self.db.query(func.count(CBDKXX.id)).filter(
            or_(
                func.length(CBDKXX.dkbm) != 19,
                CBDKXX.dkbm.is_(None),
            )
        ).scalar() or 0
        
        # 合同编码应为19位
        ht_invalid = self.db.query(func.count(CBHT.cbhtbm)).filter(
            or_(
                func.length(CBHT.cbhtbm) != 19,
                CBHT.cbhtbm.is_(None),
            )
        ).scalar() or 0
        
        code_invalid_count = cbf_invalid + dk_invalid + ht_invalid
        
        # 从导入错误表获取统计
        import_errors = self.db.query(ImportError).all()
        critical_count = len([e for e in import_errors if e.error_message and "严重" in e.error_message])
        warning_count = len([e for e in import_errors if e.error_message and "警告" in e.error_message])
        
        total_errors = overlap_count + area_zero_count + area_exceed_count + code_invalid_count
        
        return QualityStatsResponse(
            overlap_count=overlap_count,
            area_zero_count=area_zero_count,
            area_exceed_count=area_exceed_count,
            code_invalid_count=code_invalid_count,
            total_errors=total_errors,
            critical_count=critical_count,
            warning_count=warning_count,
        )
    
    def get_quality_errors(
        self,
        error_type: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> QualityErrorListResponse:
        """
        获取质量错误列表
        
        Args:
            error_type: 错误类型过滤
            page: 页码
            size: 每页大小
            
        Returns:
            错误列表
        """
        errors = []
        
        # 面积为0的地块
        area_zero_records = self.db.query(CBDKXX).filter(
            or_(
                CBDKXX.htmjm == 0,
                CBDKXX.scmjm == 0,
                CBDKXX.htmjm.is_(None),
                CBDKXX.scmjm.is_(None),
            )
        ).all()
        
        for record in area_zero_records:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="area_zero",
                severity="critical",
                table_name="cbdkxx",
                record_code=record.dkbm or str(record.id),
                error_message=f"地块面积为0或空值：合同面积={record.htmjm}, 实测面积={record.scmjm}",
                created_at=record.created_at or datetime.now(),
            ))
        
        # 面积超阈值地块
        area_exceed_records = self.db.query(CBDKXX).filter(
            or_(
                CBDKXX.htmjm > self.AREA_THRESHOLD,
                CBDKXX.scmjm > self.AREA_THRESHOLD,
            )
        ).all()
        
        for record in area_exceed_records:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="area_exceed",
                severity="warning",
                table_name="cbdkxx",
                record_code=record.dkbm or str(record.id),
                error_message=f"地块面积超过阈值({self.AREA_THRESHOLD}亩)：合同面积={record.htmjm}, 实测面积={record.scmjm}",
                created_at=record.created_at or datetime.now(),
            ))
        
        # 编码格式异常 - 承包方
        cbf_invalid_records = self.db.query(CBF).filter(
            or_(
                func.length(CBF.cbfbm) != 18,
                CBF.cbfbm.is_(None),
            )
        ).all()
        
        for record in cbf_invalid_records:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="code_invalid",
                severity="critical",
                table_name="cbf",
                record_code=record.cbfbm or "",
                error_message=f"承包方编码格式异常：应为18位，实际为{len(record.cbfbm) if record.cbfbm else 0}位",
                created_at=record.created_at or datetime.now(),
            ))
        
        # 编码格式异常 - 地块
        dk_invalid_records = self.db.query(CBDKXX).filter(
            or_(
                func.length(CBDKXX.dkbm) != 19,
                CBDKXX.dkbm.is_(None),
            )
        ).all()
        
        for record in dk_invalid_records:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="code_invalid",
                severity="critical",
                table_name="cbdkxx",
                record_code=record.dkbm or str(record.id),
                error_message=f"地块编码格式异常：应为19位，实际为{len(record.dkbm) if record.dkbm else 0}位",
                created_at=record.created_at or datetime.now(),
            ))
        
        # 编码格式异常 - 合同
        ht_invalid_records = self.db.query(CBHT).filter(
            or_(
                func.length(CBHT.cbhtbm) != 19,
                CBHT.cbhtbm.is_(None),
            )
        ).all()
        
        for record in ht_invalid_records:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="code_invalid",
                severity="critical",
                table_name="cbht",
                record_code=record.cbhtbm or "",
                error_message=f"合同编码格式异常：应为19位，实际为{len(record.cbhtbm) if record.cbhtbm else 0}位",
                created_at=record.created_at or datetime.now(),
            ))
        
        # 添加导入错误表中的错误
        import_errors = self.db.query(ImportError).all()
        for error in import_errors:
            errors.append(QualityErrorItem(
                id=len(errors) + 1,
                error_type="import",
                severity="critical",
                table_name=error.table_name or "",
                record_code=error.code or "",
                error_message=error.error_message or "",
                created_at=error.created_at or datetime.now(),
            ))
        
        # 按错误类型过滤
        if error_type:
            errors = [e for e in errors if e.error_type == error_type]
        
        # 分页
        total_count = len(errors)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_errors = errors[start_idx:end_idx]
        
        return QualityErrorListResponse(
            items=paginated_errors,
            total_count=total_count,
            page=page,
            size=size,
        )


def get_quality_service(db: Session) -> QualityService:
    """获取质量服务实例"""
    return QualityService(db)