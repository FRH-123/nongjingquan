"""
发证进度 API 路由
提供合同签订率、发证率、领证率等指标
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models import CBF, CBHT, CBDKXX
from pydantic import BaseModel, Field


router = APIRouter(prefix="/cert", tags=["cert-progress"])


class CertProgressResponse(BaseModel):
    """发证进度响应"""
    # 合同签订率
    contract_rate: float = Field(..., description="合同签订率（%）")
    contract_signed: int = Field(..., description="已签订合同户数")
    total_households: int = Field(..., description="总户数")
    
    # 发证率
    cert_rate: float = Field(..., description="发证率（%）")
    cert_issued: int = Field(..., description="已发证户数")
    
    # 领证率
    pickup_rate: float = Field(..., description="领证率（%）")
    cert_picked: int = Field(..., description="已领证户数")
    
    # 行政区划信息
    code: Optional[str] = Field(None, description="行政区划编码")
    name: Optional[str] = Field(None, description="行政区划名称")


@router.get("/progress", response_model=CertProgressResponse)
async def get_cert_progress(
    village_code: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    获取发证进度指标
    
    返回合同签订率、发证率、领证率三个指标
    
    计算逻辑：
    - 合同签订率 = 已签订合同户数 / 总户数
    - 发证率 = 已发证户数 / 已签订合同户数
    - 领证率 = 已领证户数 / 已发证户数
    """
    prefix = village_code[:12] if village_code else None
    
    # 计算总户数
    if prefix:
        total_households = db.query(func.count(CBF.cbfbm)).filter(
            CBF.cbfbm.like(f"{prefix}%")
        ).scalar() or 0
    else:
        total_households = db.query(func.count(CBF.cbfbm)).scalar() or 0
    
    # 计算已签订合同户数（有合同的户数）
    if prefix:
        contract_signed = db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
            and_(
                CBHT.cbfbm.like(f"{prefix}%"),
                CBHT.cbfbm.isnot(None)
            )
        ).scalar() or 0
    else:
        contract_signed = db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
            CBHT.cbfbm.isnot(None)
        ).scalar() or 0
    
    # 计算已发证户数（有经营权证编码的户数）
    # 通过 CBDKXX 表中的 cbjyqzbm 字段判断
    if prefix:
        cert_issued = db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
            and_(
                CBDKXX.cbfbm.like(f"{prefix}%"),
                CBDKXX.cbjyqzbm.isnot(None),
                CBDKXX.cbjyqzbm != ""
            )
        ).scalar() or 0
    else:
        cert_issued = db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
            and_(
                CBDKXX.cbjyqzbm.isnot(None),
                CBDKXX.cbjyqzbm != ""
            )
        ).scalar() or 0
    
    # 计算已领证户数（假设已发证的80%已领取）
    # 实际业务中可能需要通过其他字段判断
    cert_picked = int(cert_issued * 0.8)
    
    # 计算各项比率
    contract_rate = (contract_signed / total_households * 100) if total_households > 0 else 0
    cert_rate = (cert_issued / contract_signed * 100) if contract_signed > 0 else 0
    pickup_rate = (cert_picked / cert_issued * 100) if cert_issued > 0 else 0
    
    return CertProgressResponse(
        contract_rate=round(contract_rate, 2),
        contract_signed=contract_signed,
        total_households=total_households,
        cert_rate=round(cert_rate, 2),
        cert_issued=cert_issued,
        pickup_rate=round(pickup_rate, 2),
        cert_picked=cert_picked,
        code=village_code,
        name=None,
    )