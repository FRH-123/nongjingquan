"""
家庭成员模型 (CBF_JTCY - 承包方家庭成员表)
对应 MDB 中的 CBF_JTCY 表
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CBFJTCY(Base):
    """
    承包方家庭成员表
    对应内业软件输出的 CBF_JTCY 表
    """
    __tablename__ = "cbf_jtcy"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 承包方编码（外键）
    cbfbm = Column(String(18), ForeignKey("cbf.cbfbm"), nullable=False, comment="承包方编码")
    # 成员姓名
    cyxm = Column(String(50), nullable=True, comment="成员姓名")
    # 与户主关系
    yhzgx = Column(String(20), nullable=True, comment="与户主关系")
    # 身份证号码
    sfzhm = Column(String(30), nullable=True, comment="身份证号码")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    contractor = relationship("CBF", backref="family_members")

    def __repr__(self):
        return f"<CBFJTCY(id={self.id}, cbfbm='{self.cbfbm}', cyxm='{self.cyxm}')>"