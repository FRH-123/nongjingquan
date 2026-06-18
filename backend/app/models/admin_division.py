"""
行政区划模型 (AdminDivision)
用于存储行政区划树结构（县→镇→村→组）
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AdminDivision(Base):
    """
    行政区划表
    存储行政区划树结构，支持按层级聚合统计
    """
    __tablename__ = "admin_division"

    # 行政区划编码 (主键)
    code = Column(String(14), primary_key=True, comment="行政区划编码")
    # 行政区划名称
    name = Column(String(100), nullable=False, comment="行政区划名称")
    # 上级行政区划编码
    parent_code = Column(String(14), nullable=True, index=True, comment="上级行政区划编码")
    # 层级 (1:省, 2:市, 3:县, 4:镇, 5:村, 6:组)
    level = Column(Integer, nullable=False, comment="层级")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<AdminDivision(code='{self.code}', name='{self.name}', level={self.level})>"