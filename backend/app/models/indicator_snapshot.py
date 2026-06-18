"""
指标快照模型 (IndicatorSnapshot)
用于存储历史指标数据，支持趋势对比
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class IndicatorSnapshot(Base):
    """
    指标快照表
    每次导入后保存一份快照，供后续趋势对比使用
    """
    __tablename__ = "indicator_snapshot"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 快照日期
    snapshot_date = Column(Date, nullable=False, index=True, comment="快照日期")
    # 层级 (province:省, city:市, county:县, town:镇, village:村, group:组)
    level = Column(String(20), nullable=False, comment="层级")
    # 行政区划编码
    code = Column(String(14), nullable=False, index=True, comment="行政区划编码")
    # 指标数据 (JSON 格式)
    metrics_json = Column(Text, nullable=False, comment="指标数据 JSON")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<IndicatorSnapshot(id={self.id}, date='{self.snapshot_date}', code='{self.code}')>"