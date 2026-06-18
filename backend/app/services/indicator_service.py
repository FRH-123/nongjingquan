"""
指标聚合计算服务 (IndicatorService)
核心指标计算逻辑，支持多级聚合粒度
"""
import json
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models import FBF, CBF, CBFJTCY, CBHT, CBDKXX, DictItem, AdminDivision, IndicatorSnapshot
from app.schemas.indicator_schema import (
    OverviewIndicator,
    LandUsageItem,
    LandUsageResponse,
    SurveyStatsItem,
    SurveyStatsResponse,
    SurveyCategoryItem,
    SurveyCategoriesResponse,
    VillageIndicator,
    VillagesResponse,
    AdminDivisionNode,
    AdminDivisionTreeResponse,
)
from app.services.cache_service import cache_service


class IndicatorService:
    """
    指标聚合计算服务
    提供各类指标的聚合计算和缓存管理
    """
    
    # 用途类别映射（TDYT 编码 -> 名称）
    LAND_USAGE_MAP = {
        "01": "种植业",
        "02": "林业",
        "03": "畜牧业",
        "04": "渔业",
        "05": "其他",
    }
    
    # 填报分类映射（用于饼图）
    SURVEY_CATEGORY_MAP = {
        "1": "分户保留户",
        "2": "新增户",
        "3": "地块转",
        "4": "有变化",
        "5": "无变化",
    }
    
    # 状态映射
    STATUS_MAP = {
        "1": "待公示",
        "2": "村干部审核",
        "3": "未调查",
        "4": "待审核",
        "5": "已完成",
    }
    
    def __init__(self, db: Session):
        """
        初始化指标服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def _get_cache_key(self, endpoint: str, code: Optional[str] = None) -> str:
        """
        生成缓存键
        
        Args:
            endpoint: API 端点名称
            code: 行政区划编码（可选）
            
        Returns:
            缓存键
        """
        if code:
            return f"indicator:{endpoint}:{code}"
        return f"indicator:{endpoint}:global"
    
    def _get_cached_or_compute(self, cache_key: str, compute_func) -> Any:
        """
        获取缓存或计算结果
        
        Args:
            cache_key: 缓存键
            compute_func: 计算函数
            
        Returns:
            结果数据
        """
        # 尝试从缓存获取
        cached = cache_service.get(cache_key)
        if cached is not None:
            return cached
        
        # 计算结果
        result = compute_func()
        
        # 存入缓存
        cache_service.set(cache_key, result)
        
        return result
    
    def _get_code_prefix(self, code: Optional[str], level: str) -> str:
        """
        根据层级获取编码前缀长度
        
        Args:
            code: 行政区划编码
            level: 层级（global/province/city/county/town/village/group）
            
        Returns:
            编码前缀
        """
        if not code:
            return ""
        
        prefix_lengths = {
            "global": 0,
            "province": 2,
            "city": 4,
            "county": 6,
            "town": 9,
            "village": 12,
            "group": 14,
        }
        
        length = prefix_lengths.get(level, 12)
        return code[:length] if len(code) >= length else code
    
    def get_overview(self, village_code: Optional[str] = None) -> OverviewIndicator:
        """
        获取核心指标概览
        
        Args:
            village_code: 村级行政区划编码（可选）
            
        Returns:
            OverviewIndicator: 核心指标数据
        """
        cache_key = self._get_cache_key("overview", village_code)
        
        def compute():
            # 确定编码前缀
            prefix = village_code[:12] if village_code else None
            
            # 发包方总数
            if prefix:
                issuer_count = self.db.query(func.count(FBF.fbfbm)).filter(
                    FBF.fbfbm.like(f"{prefix}%")
                ).scalar() or 0
            else:
                issuer_count = self.db.query(func.count(FBF.fbfbm)).scalar() or 0
            
            # 承包方总数（总户数）
            if prefix:
                contractor_count = self.db.query(func.count(CBF.cbfbm)).filter(
                    CBF.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
            else:
                contractor_count = self.db.query(func.count(CBF.cbfbm)).scalar() or 0
            
            # 已摸底户数（有地块关联的户数）
            # 通过 CBDKXX 表中存在记录来判断
            if prefix:
                surveyed_count = self.db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
                    and_(
                        CBDKXX.cbfbm.like(f"{prefix}%"),
                        CBDKXX.cbfbm.isnot(None)
                    )
                ).scalar() or 0
            else:
                surveyed_count = self.db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
                    CBDKXX.cbfbm.isnot(None)
                ).scalar() or 0
            
            # 已内业审核数（有合同的户数）
            if prefix:
                audited_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
                    and_(
                        CBHT.cbfbm.like(f"{prefix}%"),
                        CBHT.cbfbm.isnot(None)
                    )
                ).scalar() or 0
            else:
                audited_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
                    CBHT.cbfbm.isnot(None)
                ).scalar() or 0
            
            # 已完成户数（有经营权证且有发证日期的户数）
            # 通过 CBHT 表关联判断，假设有合同且有地块即为已完成
            # 实际业务中可能需要通过 CBJYQZ 表判断
            if prefix:
                # 查询有合同且有地块的承包方
                completed_subquery = self.db.query(CBHT.cbfbm).join(
                    CBDKXX, CBHT.cbhtbm == CBDKXX.cbhtbm
                ).filter(
                    and_(
                        CBHT.cbfbm.like(f"{prefix}%"),
                        CBHT.cbfbm.isnot(None)
                    )
                ).distinct()
                completed_count = self.db.query(func.count()).select_from(completed_subquery).scalar() or 0
            else:
                completed_subquery = self.db.query(CBHT.cbfbm).join(
                    CBDKXX, CBHT.cbhtbm == CBDKXX.cbhtbm
                ).filter(CBHT.cbfbm.isnot(None)).distinct()
                completed_count = self.db.query(func.count()).select_from(completed_subquery).scalar() or 0
            
            # 获取行政区划名称
            name = None
            if village_code:
                admin_div = self.db.query(AdminDivision).filter(
                    AdminDivision.code == village_code
                ).first()
                if admin_div:
                    name = admin_div.name
            
            return OverviewIndicator(
                issuer_count=issuer_count,
                contractor_count=contractor_count,
                surveyed_count=surveyed_count,
                audited_count=audited_count,
                completed_count=completed_count,
                code=village_code,
                name=name,
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return OverviewIndicator(**result)
    
    def get_land_usage(self, village_code: Optional[str] = None) -> LandUsageResponse:
        """
        获取地块用途统计
        
        Args:
            village_code: 村级行政区划编码（可选）
            
        Returns:
            LandUsageResponse: 用途统计数据
        """
        cache_key = self._get_cache_key("land_usage", village_code)
        
        def compute():
            prefix = village_code[:12] if village_code else None
            
            # 从字典表获取用途映射
            dict_items = self.db.query(DictItem).filter(
                DictItem.category == "TDLYLX"
            ).all()
            usage_map = {item.code: item.name for item in dict_items}
            
            # 如果字典表没有数据，使用默认映射
            if not usage_map:
                usage_map = self.LAND_USAGE_MAP
            
            # 查询地块用途统计
            if prefix:
                query = self.db.query(
                    CBDKXX.tdyt,
                    func.count(CBDKXX.id).label("count"),
                    func.sum(CBDKXX.scmjm).label("area")
                ).filter(
                    and_(
                        CBDKXX.dkbm.like(f"{prefix}%"),
                        CBDKXX.tdyt.isnot(None)
                    )
                ).group_by(CBDKXX.tdyt)
            else:
                query = self.db.query(
                    CBDKXX.tdyt,
                    func.count(CBDKXX.id).label("count"),
                    func.sum(CBDKXX.scmjm).label("area")
                ).filter(CBDKXX.tdyt.isnot(None)).group_by(CBDKXX.tdyt)
            
            results = query.all()
            
            items = []
            total_count = 0
            total_area = 0
            
            for row in results:
                code = row.tdyt or "未知"
                category = usage_map.get(code, code)
                count = row.count or 0
                area = float(row.area or 0)
                
                items.append(LandUsageItem(
                    category=category,
                    code=code,
                    count=count,
                    area=area,
                ))
                total_count += count
                total_area += area
            
            # 添加缺失的用途类别（确保返回所有类别）
            for code, name in usage_map.items():
                if not any(item.code == code for item in items):
                    items.append(LandUsageItem(
                        category=name,
                        code=code,
                        count=0,
                        area=0,
                    ))
            
            return LandUsageResponse(
                items=items,
                total_count=total_count,
                total_area=total_area,
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return LandUsageResponse(**result)
    
    def get_survey_stats(self, village_code: Optional[str] = None) -> SurveyStatsResponse:
        """
        获取摸底填报统计（按村组分组）
        
        Args:
            village_code: 村级行政区划编码（可选）
            
        Returns:
            SurveyStatsResponse: 摸底填报统计数据
        """
        cache_key = self._get_cache_key("survey_stats", village_code)
        
        def compute():
            # 获取村组列表
            if village_code:
                # 获取指定村下的所有组
                villages = self.db.query(AdminDivision).filter(
                    AdminDivision.parent_code == village_code[:12]
                ).all()
            else:
                # 获取所有村级单位
                villages = self.db.query(AdminDivision).filter(
                    AdminDivision.level == 5  # 村级
                ).all()
            
            items = []
            total_reported = 0
            total_audited = 0
            
            for village in villages:
                prefix = village.code[:12] if len(village.code) >= 12 else village.code
                
                # 已上报户数（有地块的户数）
                reported_count = self.db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
                    CBDKXX.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
                
                # 已审核户数（有合同的户数）
                audited_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
                    CBHT.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
                
                items.append(SurveyStatsItem(
                    village_code=village.code,
                    village_name=village.name,
                    reported_count=reported_count,
                    audited_count=audited_count,
                ))
                total_reported += reported_count
                total_audited += audited_count
            
            return SurveyStatsResponse(
                items=items,
                total_reported=total_reported,
                total_audited=total_audited,
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return SurveyStatsResponse(**result)
    
    def get_survey_categories(self, village_code: Optional[str] = None) -> SurveyCategoriesResponse:
        """
        获取填报分类统计（饼图数据）
        
        Args:
            village_code: 村级行政区划编码（可选）
            
        Returns:
            SurveyCategoriesResponse: 填报分类数据
        """
        cache_key = self._get_cache_key("survey_categories", village_code)
        
        def compute():
            prefix = village_code[:12] if village_code else None
            
            # 这里需要根据实际业务逻辑计算分类
            # 暂时使用模拟数据，实际应根据 CBHT 或其他表的状态字段计算
            
            # 总户数
            if prefix:
                total_count = self.db.query(func.count(CBF.cbfbm)).filter(
                    CBF.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
            else:
                total_count = self.db.query(func.count(CBF.cbfbm)).scalar() or 0
            
            # 如果没有数据，返回空结果
            if total_count == 0:
                return SurveyCategoriesResponse(
                    items=[],
                    total_count=0,
                ).model_dump()
            
            # 计算各分类占比（基于业务逻辑推断）
            # 分户保留户：有合同且无变化的
            # 新增户：新增的承包方
            # 地块转：有流转记录的
            # 有变化：地块信息有变更的
            # 无变化：完全无变更的
            
            # 暂时使用简化计算
            items = []
            
            # 分户保留户（有合同的户数）
            if prefix:
                retained_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
                    CBHT.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
            else:
                retained_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).scalar() or 0
            
            # 其他分类暂时按比例分配
            remaining = total_count - retained_count
            new_count = int(remaining * 0.1)  # 新增户约10%
            transfer_count = int(remaining * 0.05)  # 地块转约5%
            changed_count = int(remaining * 0.15)  # 有变化约15%
            unchanged_count = remaining - new_count - transfer_count - changed_count
            
            categories = [
                ("1", "分户保留户", retained_count),
                ("2", "新增户", new_count),
                ("3", "地块转", transfer_count),
                ("4", "有变化", changed_count),
                ("5", "无变化", unchanged_count),
            ]
            
            for code, name, count in categories:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                items.append(SurveyCategoryItem(
                    category=name,
                    code=code,
                    count=count,
                    percentage=round(percentage, 2),
                ))
            
            return SurveyCategoriesResponse(
                items=items,
                total_count=total_count,
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return SurveyCategoriesResponse(**result)
    
    def get_villages(self, village_code: Optional[str] = None) -> VillagesResponse:
        """
        获取村组指标列表
        
        Args:
            village_code: 村级行政区划编码（可选）
            
        Returns:
            VillagesResponse: 村组指标列表
        """
        cache_key = self._get_cache_key("villages", village_code)
        
        def compute():
            # 获取村组列表
            if village_code:
                villages = self.db.query(AdminDivision).filter(
                    AdminDivision.parent_code == village_code[:12]
                ).all()
            else:
                villages = self.db.query(AdminDivision).filter(
                    AdminDivision.level >= 5  # 村级及以下
                ).all()
            
            items = []
            
            for village in villages:
                prefix = village.code[:12] if len(village.code) >= 12 else village.code
                
                # 计算各项指标
                total_households = self.db.query(func.count(CBF.cbfbm)).filter(
                    CBF.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
                
                surveyed_count = self.db.query(func.count(func.distinct(CBDKXX.cbfbm))).filter(
                    CBDKXX.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
                
                audited_count = self.db.query(func.count(func.distinct(CBHT.cbfbm))).filter(
                    CBHT.cbfbm.like(f"{prefix}%")
                ).scalar() or 0
                
                completed_subquery = self.db.query(CBHT.cbfbm).join(
                    CBDKXX, CBHT.cbhtbm == CBDKXX.cbhtbm
                ).filter(CBHT.cbfbm.like(f"{prefix}%")).distinct()
                completed_count = self.db.query(func.count()).select_from(completed_subquery).scalar() or 0
                
                # 计算完成率
                survey_rate = (surveyed_count / total_households * 100) if total_households > 0 else 0
                audit_rate = (audited_count / surveyed_count * 100) if surveyed_count > 0 else 0
                complete_rate = (completed_count / total_households * 100) if total_households > 0 else 0
                
                items.append(VillageIndicator(
                    village_code=village.code,
                    village_name=village.name,
                    total_households=total_households,
                    surveyed_count=surveyed_count,
                    audited_count=audited_count,
                    completed_count=completed_count,
                    survey_rate=round(survey_rate, 2),
                    audit_rate=round(audit_rate, 2),
                    complete_rate=round(complete_rate, 2),
                ))
            
            return VillagesResponse(
                items=items,
                total_count=len(items),
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return VillagesResponse(**result)
    
    def get_admin_division_tree(self) -> AdminDivisionTreeResponse:
        """
        获取行政区划树
        
        Returns:
            AdminDivisionTreeResponse: 行政区划树
        """
        cache_key = self._get_cache_key("admin_division_tree")
        
        def compute():
            # 获取所有行政区划
            divisions = self.db.query(AdminDivision).order_by(
                AdminDivision.level, AdminDivision.code
            ).all()
            
            # 构建树结构
            nodes_map: Dict[str, AdminDivisionNode] = {}
            root_nodes: List[AdminDivisionNode] = []
            
            # 先创建所有节点
            for div in divisions:
                node = AdminDivisionNode(
                    code=div.code,
                    name=div.name,
                    level=div.level,
                    parent_code=div.parent_code,
                    children=[],
                )
                nodes_map[div.code] = node
            
            # 构建父子关系
            for div in divisions:
                node = nodes_map[div.code]
                if div.parent_code and div.parent_code in nodes_map:
                    nodes_map[div.parent_code].children.append(node)
                else:
                    root_nodes.append(node)
            
            return AdminDivisionTreeResponse(
                nodes=root_nodes,
                total_count=len(divisions),
            ).model_dump()
        
        result = self._get_cached_or_compute(cache_key, compute)
        return AdminDivisionTreeResponse(**result)
    
    def save_snapshot(self, snapshot_date: date = None) -> bool:
        """
        保存指标快照
        
        Args:
            snapshot_date: 快照日期（默认为今天）
            
        Returns:
            是否成功
        """
        if snapshot_date is None:
            snapshot_date = date.today()
        
        try:
            # 获取所有行政区划
            divisions = self.db.query(AdminDivision).all()
            
            for div in divisions:
                # 计算该行政区划的指标
                overview = self.get_overview(div.code)
                
                # 创建快照记录
                snapshot = IndicatorSnapshot(
                    snapshot_date=snapshot_date,
                    level=self._get_level_name(div.level),
                    code=div.code,
                    metrics_json=json.dumps(overview.model_dump(), ensure_ascii=False),
                )
                self.db.add(snapshot)
            
            # 保存全局快照
            global_overview = self.get_overview()
            global_snapshot = IndicatorSnapshot(
                snapshot_date=snapshot_date,
                level="global",
                code="",
                metrics_json=json.dumps(global_overview.model_dump(), ensure_ascii=False),
            )
            self.db.add(global_snapshot)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"保存快照失败: {e}")
            return False
    
    def _get_level_name(self, level: int) -> str:
        """
        获取层级名称
        
        Args:
            level: 层级数字
            
        Returns:
            层级名称
        """
        level_names = {
            1: "province",
            2: "city",
            3: "county",
            4: "town",
            5: "village",
            6: "group",
        }
        return level_names.get(level, "unknown")
    
    def refresh_all_cache(self) -> bool:
        """
        刷新所有指标缓存
        
        Returns:
            是否成功
        """
        return cache_service.refresh_cache()


def get_indicator_service(db: Session) -> IndicatorService:
    """
    获取指标服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        IndicatorService 实例
    """
    return IndicatorService(db)