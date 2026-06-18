"""
指标响应 Pydantic 模型 (IndicatorSchema)
用于定义指标查询接口的响应数据结构
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class OverviewIndicator(BaseModel):
    """
    核心指标概览响应模型
    """
    # 发包方总数
    issuer_count: int = Field(..., description="发包方总数")
    # 承包方总数（总户数）
    contractor_count: int = Field(..., description="承包方总数（总户数）")
    # 已摸底户数（有地块关联的户数）
    surveyed_count: int = Field(..., description="已摸底户数")
    # 已内业审核数（有合同的户数）
    audited_count: int = Field(..., description="已内业审核数")
    # 已完成户数（有经营权证的户数）
    completed_count: int = Field(..., description="已完成户数")
    
    # 行政区划信息
    code: Optional[str] = Field(None, description="行政区划编码")
    name: Optional[str] = Field(None, description="行政区划名称")


class LandUsageItem(BaseModel):
    """
    地块用途统计项
    """
    category: str = Field(..., description="用途类别名称")
    code: str = Field(..., description="用途编码")
    count: int = Field(..., description="地块数量")
    area: float = Field(default=0, description="总面积（亩）")


class LandUsageResponse(BaseModel):
    """
    地块用途统计响应模型
    """
    items: List[LandUsageItem] = Field(..., description="用途统计列表")
    total_count: int = Field(..., description="总地块数")
    total_area: float = Field(default=0, description="总面积（亩）")


class SurveyStatsItem(BaseModel):
    """
    摸底填报统计项（按村组）
    """
    village_code: str = Field(..., description="村组编码")
    village_name: str = Field(..., description="村组名称")
    reported_count: int = Field(..., description="已上报户数")
    audited_count: int = Field(..., description="已审核户数")


class SurveyStatsResponse(BaseModel):
    """
    摸底填报统计响应模型（分组柱状图数据）
    """
    items: List[SurveyStatsItem] = Field(..., description="按村组统计列表")
    total_reported: int = Field(..., description="总已上报户数")
    total_audited: int = Field(..., description="总已审核户数")


class SurveyCategoryItem(BaseModel):
    """
    填报分类统计项（饼图数据）
    """
    category: str = Field(..., description="分类名称")
    code: str = Field(..., description="分类编码")
    count: int = Field(..., description="户数")
    percentage: float = Field(..., description="占比百分比")


class SurveyCategoriesResponse(BaseModel):
    """
    填报分类统计响应模型（饼图数据）
    """
    items: List[SurveyCategoryItem] = Field(..., description="分类统计列表")
    total_count: int = Field(..., description="总户数")


class VillageIndicator(BaseModel):
    """
    村组指标详情
    """
    village_code: str = Field(..., description="村组编码")
    village_name: str = Field(..., description="村组名称")
    total_households: int = Field(..., description="总户数")
    surveyed_count: int = Field(..., description="已摸底户数")
    audited_count: int = Field(..., description="已审核户数")
    completed_count: int = Field(..., description="已完成户数")
    survey_rate: float = Field(default=0, description="摸底完成率")
    audit_rate: float = Field(default=0, description="审核完成率")
    complete_rate: float = Field(default=0, description="总体完成率")


class VillagesResponse(BaseModel):
    """
    村组列表响应模型
    """
    items: List[VillageIndicator] = Field(..., description="村组指标列表")
    total_count: int = Field(..., description="村组总数")


class AdminDivisionNode(BaseModel):
    """
    行政区划树节点
    """
    code: str = Field(..., description="行政区划编码")
    name: str = Field(..., description="行政区划名称")
    level: int = Field(..., description="层级（1-6）")
    parent_code: Optional[str] = Field(default=None, description="父级编码")
    children: List["AdminDivisionNode"] = Field(default_factory=list, description="子节点列表")


# Pydantic v2 使用 model_rebuild() 解决递引用
AdminDivisionNode.model_rebuild()


class AdminDivisionTreeResponse(BaseModel):
    """
    行政区划树响应模型
    """
    nodes: List[AdminDivisionNode] = Field(..., description="行政区划树节点列表")
    total_count: int = Field(..., description="节点总数")