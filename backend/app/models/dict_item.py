"""
字典项模型 (DictItem)
用于存储系统字典数据，如 SYQXZ/DKLB/TDLYLX/DLDJ 等编码映射
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class DictItem(Base):
    """
    字典项表
    存储各类编码的名称映射
    """
    __tablename__ = "dict_item"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 字典类别 (如: SYQXZ-所有权性质, DKLB-地块类别, TDLYLX-土地利用类型, DLDJ-地类等级)
    category = Column(String(50), nullable=False, index=True, comment="字典类别")
    # 编码
    code = Column(String(20), nullable=False, comment="编码")
    # 名称
    name = Column(String(100), nullable=False, comment="名称")
    # 排序号
    sort_order = Column(Integer, nullable=True, default=0, comment="排序号")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<DictItem(category='{self.category}', code='{self.code}', name='{self.name}')>"