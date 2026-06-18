"""
发包方模型 (FBF - 发包方表)
对应 MDB 中的 FBF 表
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FBF(Base):
    """
    发包方表
    对应内业软件输出的 FBF 表
    """
    __tablename__ = "fbf"

    # 发包方编码 (14位: 省2+市2+县2+镇3+村3+组1)
    fbfbm = Column(String(14), primary_key=True, comment="发包方编码")
    # 发包方名称
    fbfmc = Column(String(100), nullable=True, comment="发包方名称")
    # 发包方负责人姓名
    fbffzrxm = Column(String(50), nullable=True, comment="发包方负责人姓名")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<FBF(fbfbm='{self.fbfbm}', fbfmc='{self.fbfmc}')>"