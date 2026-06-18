"""
审核列表查询 API 路由 (AuditAPI)
提供审核列表查询相关的 REST API 接口
"""
from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models import CBF, CBHT, CBDKXX, CBFJTCY, AdminDivision
from app.schemas.audit_schema import AuditListItem, AuditListResponse, AuditDetail


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/list", response_model=AuditListResponse)
async def get_audit_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    village_code: Optional[str] = Query(None, description="村级行政区划编码"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词（承包方名称）"),
    db: Session = Depends(get_db),
):
    """
    获取审核列表（分页）
    
    返回承包方名称/村组/上报类型/当前状态的分页表格数据
    
    Args:
        page: 页码（默认 1）
        size: 每页大小（默认 10，最大 100）
        village_code: 村级行政区划编码（可选筛选）
        status: 状态筛选（可选）
        search: 搜索关键词（可选）
        db: 数据库会话
        
    Returns:
        AuditListResponse: 审核列表分页数据
    """
    # 构建基础查询
    query = db.query(CBF).outerjoin(
        CBHT, CBF.cbfbm == CBHT.cbfbm
    ).outerjoin(
        CBDKXX, CBF.cbfbm == CBDKXX.cbfbm
    )
    
    # 应用筛选条件
    if village_code:
        prefix = village_code[:12] if len(village_code) >= 12 else village_code
        query = query.filter(CBF.cbfbm.like(f"{prefix}%"))
    
    if search:
        query = query.filter(CBF.cbfmc.like(f"%{search}%"))
    
    # 计算总数
    total = query.count()
    
    # 计算总页数
    pages = ceil(total / size) if total > 0 else 1
    
    # 分页查询
    offset = (page - 1) * size
    results = query.order_by(CBF.cbfbm).offset(offset).limit(size).all()
    
    # 构建响应列表
    items = []
    
    for cbf in results:
        # 获取村组编码（从 cbfbm 前 12 位提取）
        village_code_from_cbfbm = cbf.cbfbm[:12] if len(cbf.cbfbm) >= 12 else cbf.cbfbm
        
        # 获取村组名称
        village_name = None
        admin_div = db.query(AdminDivision).filter(
            AdminDivision.code == village_code_from_cbfbm
        ).first()
        if admin_div:
            village_name = admin_div.name
        
        # 获取合同信息
        contract = db.query(CBHT).filter(CBHT.cbfbm == cbf.cbfbm).first()
        
        # 获取地块数量和面积
        land_count = db.query(func.count(CBDKXX.id)).filter(
            CBDKXX.cbfbm == cbf.cbfbm
        ).scalar() or 0
        
        contract_area = db.query(func.sum(CBDKXX.htmjm)).filter(
            CBDKXX.cbfbm == cbf.cbfbm
        ).scalar()
        contract_area = float(contract_area or 0)
        
        # 获取家庭成员数量
        family_count = db.query(func.count(CBFJTCY.id)).filter(
            CBFJTCY.cbfbm == cbf.cbfbm
        ).scalar() or 0
        
        # 确定状态
        # 根据业务逻辑推断状态：
        # - 有合同且有地块 = 已完成
        # - 有合同但无地块 = 待审核
        # - 无合同但有地块 = 村干部审核
        # - 无合同无地块 = 未调查
        
        if contract and land_count > 0:
            status_code = "5"
            status_name = "已完成"
        elif contract and land_count == 0:
            status_code = "4"
            status_name = "待审核"
        elif not contract and land_count > 0:
            status_code = "2"
            status_name = "村干部审核"
        else:
            status_code = "3"
            status_name = "未调查"
        
        # 状态筛选
        if status and status_code != status:
            continue
        
        # 确定上报类型（简化处理）
        # 实际业务中可能需要从其他字段获取
        report_type = "无变化"  # 默认值
        
        items.append(AuditListItem(
            cbfbm=cbf.cbfbm,
            cbfmc=cbf.cbfmc,
            village_code=village_code_from_cbfbm,
            village_name=village_name,
            report_type=report_type,
            status=status_name,
            status_code=status_code,
            family_count=family_count,
            land_count=land_count,
            contract_area=contract_area,
            contract_date=contract.cbqxq if contract else None,
        ))
    
    return AuditListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/detail/{cbfbm}", response_model=AuditDetail)
async def get_audit_detail(
    cbfbm: str,
    db: Session = Depends(get_db),
):
    """
    获取审核详情
    
    返回指定承包方的详细信息，包括家庭成员和地块列表
    
    Args:
        cbfbm: 承包方编码
        db: 数据库会话
        
    Returns:
        AuditDetail: 审核详情
    """
    # 查询承包方
    cbf = db.query(CBF).filter(CBF.cbfbm == cbfbm).first()
    
    if not cbf:
        raise HTTPException(status_code=404, detail="承包方不存在")
    
    # 获取村组信息
    village_code = cbf.cbfbm[:12] if len(cbf.cbfbm) >= 12 else cbf.cbfbm
    village_name = None
    admin_div = db.query(AdminDivision).filter(
        AdminDivision.code == village_code
    ).first()
    if admin_div:
        village_name = admin_div.name
    
    # 获取合同信息
    contract = db.query(CBHT).filter(CBHT.cbfbm == cbf.cbfbm).first()
    
    # 获取地块数量和面积
    land_count = db.query(func.count(CBDKXX.id)).filter(
        CBDKXX.cbfbm == cbf.cbfbm
    ).scalar() or 0
    
    contract_area = db.query(func.sum(CBDKXX.htmjm)).filter(
        CBDKXX.cbfbm == cbf.cbfbm
    ).scalar()
    contract_area = float(contract_area or 0)
    
    # 获取家庭成员数量
    family_count = db.query(func.count(CBFJTCY.id)).filter(
        CBFJTCY.cbfbm == cbf.cbfbm
    ).scalar() or 0
    
    # 确定状态
    if contract and land_count > 0:
        status_code = "5"
        status_name = "已完成"
    elif contract and land_count == 0:
        status_code = "4"
        status_name = "待审核"
    elif not contract and land_count > 0:
        status_code = "2"
        status_name = "村干部审核"
    else:
        status_code = "3"
        status_name = "未调查"
    
    # 获取家庭成员列表
    family_members_query = db.query(CBFJTCY).filter(
        CBFJTCY.cbfbm == cbf.cbfbm
    ).all()
    family_members = [
        {
            "name": fm.cyxm,
            "relation": fm.yhzgx,
        }
        for fm in family_members_query
    ]
    
    # 获取地块列表
    land_parcels_query = db.query(CBDKXX).filter(
        CBDKXX.cbfbm == cbf.cbfbm
    ).all()
    land_parcels = [
        {
            "dkbm": lp.dkbm,
            "dkmc": lp.dkmc,
            "area": float(lp.htmjm or 0),
            "tdyt": lp.tdyt,
        }
        for lp in land_parcels_query
    ]
    
    return AuditDetail(
        cbfbm=cbf.cbfbm,
        cbfmc=cbf.cbfmc,
        village_code=village_code,
        village_name=village_name,
        report_type="无变化",
        status=status_name,
        status_code=status_code,
        family_count=family_count,
        land_count=land_count,
        contract_area=contract_area,
        contract_date=contract.cbqxq if contract else None,
        family_members=family_members,
        land_parcels=land_parcels,
    )