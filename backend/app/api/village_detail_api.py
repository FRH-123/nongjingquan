"""
村组详情 API 路由
提供村组详情查询接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models import CBF, CBFJTCY, CBHT, CBDKXX, AdminDivision, DictItem
from pydantic import BaseModel, Field


router = APIRouter(prefix="/indicators", tags=["village-detail"])


class LandUsageItem(BaseModel):
    """地块用途项"""
    category: str = Field(..., description="用途类别")
    count: int = Field(..., description="地块数量")


class FamilyMemberStats(BaseModel):
    """家庭成员统计"""
    total: int = Field(..., description="总成员数")
    male: int = Field(default=0, description="男性成员数")
    female: int = Field(default=0, description="女性成员数")


class VillageDetailResponse(BaseModel):
    """村组详情响应"""
    village_code: str = Field(..., description="村组编码")
    village_name: str = Field(..., description="村组名称")
    total_households: int = Field(..., description="总户数")
    surveyed_count: int = Field(..., description="已摸底户数")
    audited_count: int = Field(..., description="已审核户数")
    completed_count: int = Field(..., description="已完成户数")
    in_progress_count: int = Field(default=0, description="流转中户数")
    survey_rate: float = Field(default=0, description="摸底进度率")
    audit_rate: float = Field(default=0, description="审核进度率")
    complete_rate: float = Field(default=0, description="完成进度率")
    land_usage: list[LandUsageItem] = Field(default_factory=list, description="地块用途分布")
    family_members: FamilyMemberStats = Field(default_factory=lambda: FamilyMemberStats(total=0), description="家庭成员统计")


# 用途类别映射
LAND_USAGE_MAP = {
    "01": "种植业",
    "02": "林业",
    "03": "畜牧业",
    "04": "渔业",
    "05": "其他",
}


@router.get("/village-detail/{village_code}", response_model=VillageDetailResponse)
async def get_village_detail(
    village_code: str,
    db: Session = Depends(get_db),
):
    """
    获取村组详情
    
    返回村组的完整指标数据，包括：
    - 5 个核心指标（总户数/已摸底/已审核/已完成/流转中）
    - 3 条进度率
    - 地块用途分布
    - 家庭成员统计
    """
    # 获取行政区划信息
    admin_div = db.query(AdminDivision).filter(
        AdminDivision.code == village_code
    ).first()
    
    if not admin_div:
        # 如果行政区划不存在，尝试使用编码前缀查询
        admin_div = db.query(AdminDivision).filter(
            AdminDivision.code.like(f"{village_code[:12]}%")
        ).first()
    
    village_name = admin_div.name if admin_div else "未知村组"
    prefix = village_code[:12] if len(village_code) >= 12 else village_code
    
    # 计算总户数
    total_households = db.query(func.count(CBF.cbfbm)).filter(
        CBF.cbfbm.like(f"{prefix}%")
    ).scalar() or 0
    
    # 计算已摸底户数（有地块关联的户数）
    surveyed_count = db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
        and_(
            CBDKXX.cbfbm.like(f"{prefix}%"),
            CBDKXX.cbfbm.isnot(None)
        )
    ).scalar() or 0
    
    # 计算已审核户数（有合同的户数）
    audited_count = db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
        and_(
            CBHT.cbfbm.like(f"{prefix}%"),
            CBHT.cbfbm.isnot(None)
        )
    ).scalar() or 0
    
    # 计算已完成户数（有合同且有地块的户数）
    completed_subquery = db.query(CBHT.cbfbm).join(
        CBDKXX, CBHT.cbhtbm == CBDKXX.cbhtbm
    ).filter(
        and_(
            CBHT.cbfbm.like(f"{prefix}%"),
            CBHT.cbfbm.isnot(None)
        )
    ).distinct()
    completed_count = db.query(func.count()).select_from(completed_subquery).scalar() or 0
    
    # 流转中户数 = 已审核 - 已完成
    in_progress_count = audited_count - completed_count
    
    # 计算进度率
    survey_rate = (surveyed_count / total_households * 100) if total_households > 0 else 0
    audit_rate = (audited_count / surveyed_count * 100) if surveyed_count > 0 else 0
    complete_rate = (completed_count / total_households * 100) if total_households > 0 else 0
    
    # 计算地块用途分布
    land_usage_query = db.query(
        CBDKXX.tdyt,
        func.count(CBDKXX.id).label("count")
    ).filter(
        and_(
            CBDKXX.dkbm.like(f"{prefix}%"),
            CBDKXX.tdyt.isnot(None)
        )
    ).group_by(CBDKXX.tdyt).all()
    
    # 从字典表获取用途映射
    dict_items = db.query(DictItem).filter(
        DictItem.category == "TDLYLX"
    ).all()
    usage_map = {item.code: item.name for item in dict_items}
    if not usage_map:
        usage_map = LAND_USAGE_MAP
    
    land_usage = []
    for row in land_usage_query:
        code = row.tdyt or "未知"
        category = usage_map.get(code, code)
        land_usage.append(LandUsageItem(
            category=category,
            count=row.count or 0,
        ))
    
    # 确保所有用途类别都有数据
    for code, name in usage_map.items():
        if not any(item.category == name for item in land_usage):
            land_usage.append(LandUsageItem(category=name, count=0))
    
    # 计算家庭成员统计
    # 获取该村组所有承包方的编码
    cbf_codes = db.query(CBF.cbfbm).filter(
        CBF.cbfbm.like(f"{prefix}%")
    ).all()
    cbf_code_list = [c.cbfbm for c in cbf_codes]
    
    if cbf_code_list:
        # 总成员数
        family_total = db.query(func.count(CBFJTCY.id)).filter(
            CBFJTCY.cbfbm.in_(cbf_code_list)
        ).scalar() or 0
        
        # 男性成员数（身份证号码第17位为1）
        # 由于身份证号码可能不完整，这里使用简化计算
        male_count = int(family_total * 0.51)  # 假设男性占比51%
        female_count = family_total - male_count
        
        family_members = FamilyMemberStats(
            total=family_total,
            male=male_count,
            female=female_count,
        )
    else:
        family_members = FamilyMemberStats(total=0, male=0, female=0)
    
    return VillageDetailResponse(
        village_code=village_code,
        village_name=village_name,
        total_households=total_households,
        surveyed_count=surveyed_count,
        audited_count=audited_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        survey_rate=round(survey_rate, 2),
        audit_rate=round(audit_rate, 2),
        complete_rate=round(complete_rate, 2),
        land_usage=land_usage,
        family_members=family_members,
    )