"""
承包合同模型 (CBHT - 承包合同表)
对应 MDB 中的 CBHT 表
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CBHT(Base):
    """
    承包合同表
    对应内业软件输出的 CBHT 表
    """
    __tablename__ = "cbht"

    # 承包合同编码 (19位)
    cbhtbm = Column(String(19), primary_key=True, comment="承包合同编码")
    # 发包方编码（外键）
    fbfbm = Column(String(14), ForeignKey("fbf.fbfbm"), nullable=True, comment="发包方编码")
    # 承包方编码（外键）
    cbfbm = Column(String(18), ForeignKey("cbf.cbfbm"), nullable=True, comment="承包方编码")
    # 承包方式
    cbfs = Column(String(20), nullable=True, comment="承包方式")
    # 承包期限起
    cbqxq = Column(Date, nullable=True, comment="承包期限起")
    # 承包期限止
    cbqxz = Column(Date, nullable=True, comment="承包期限止")
    # 合同总面积（亩）
    htmjm = Column(Numeric(12, 2), nullable=True, comment="合同总面积（亩）")
    # 承包地块总数
    cbdkzs = Column(Integer, nullable=True, comment="承包地块总数")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    issuer = relationship("FBF", backref="contracts")
    contractor = relationship("CBF", backref="contracts")

    def __repr__(self):
        return f"<CBHT(cbhtbm='{self.cbhtbm}', cbfbm='{self.cbfbm}')>"