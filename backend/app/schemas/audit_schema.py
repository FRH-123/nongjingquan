"""
审核列表响应 Pydantic 模型 (AuditSchema)
用于定义审核列表查询接口的响应数据结构
"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class AuditListItem(BaseModel):
    """
    审核列表项
    """
    # 承包方编码
    cbfbm: str = Field(..., description="承包方编码")
    # 承包方名称（户主姓名）
    cbfmc: Optional[str] = Field(None, description="承包方名称")
    # 村组编码
    village_code: str = Field(..., description="村组编码")
    # 村组名称
    village_name: Optional[str] = Field(None, description="村组名称")
    # 上报类型（分户保留户/新增户/地块转/有变化/无变化）
    report_type: Optional[str] = Field(None, description="上报类型")
    # 当前状态（待公示/村干部审核/未调查/待审核等）
    status: Optional[str] = Field(None, description="当前状态")
    # 状态编码
    status_code: Optional[str] = Field(None, description="状态编码")
    # 家庭成员数量
    family_count: Optional[int] = Field(None, description="家庭成员数量")
    # 承包地块数量
    land_count: Optional[int] = Field(None, description="承包地块数量")
    # 承包面积（亩）
    contract_area: Optional[float] = Field(None, description="承包面积（亩）")
    # 合同签订日期
    contract_date: Optional[date] = Field(None, description="合同签订日期")


class AuditListResponse(BaseModel):
    """
    审核列表分页响应模型
    """
    items: List[AuditListItem] = Field(..., description="审核列表项")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


class AuditDetail(BaseModel):
    """
    审核详情响应模型
    """
    cbfbm: str = Field(..., description="承包方编码")
    cbfmc: Optional[str] = Field(None, description="承包方名称")
    village_code: str = Field(..., description="村组编码")
    village_name: Optional[str] = Field(None, description="村组名称")
    report_type: Optional[str] = Field(None, description="上报类型")
    status: Optional[str] = Field(None, description="当前状态")
    status_code: Optional[str] = Field(None, description="状态编码")
    family_count: Optional[int] = Field(None, description="家庭成员数量")
    land_count: Optional[int] = Field(None, description="承包地块数量")
    contract_area: Optional[float] = Field(None, description="承包面积（亩）")
    contract_date: Optional[date] = Field(None, description="合同签订日期")
    # 家庭成员列表
    family_members: List[dict] = Field(default_factory=list, description="家庭成员列表")
    # 地块列表
    land_parcels: List[dict] = Field(default_factory=list, description="地块列表")