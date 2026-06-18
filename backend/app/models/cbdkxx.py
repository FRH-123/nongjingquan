"""
承包地块信息模型 (CBDKXX - 承包地块信息表)
对应 MDB 中的 CBDKXX 表
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CBDKXX(Base):
    """
    承包地块信息表
    对应内业软件输出的 CBDKXX 表
    """
    __tablename__ = "cbdkxx"

    # 主键ID
    id = Column(String(20), primary_key=True, comment="主键ID")
    # 承包方编码（外键）
    cbfbm = Column(String(18), ForeignKey("cbf.cbfbm"), nullable=True, comment="承包方编码")
    # 承包合同编码（外键）
    cbhtbm = Column(String(19), ForeignKey("cbht.cbhtbm"), nullable=True, comment="承包合同编码")
    # 地块编码 (19位)
    dkbm = Column(String(19), nullable=True, comment="地块编码")
    # 承包经营权证编码
    cbjyqzbm = Column(String(19), nullable=True, comment="承包经营权证编码")
    # 合同面积（亩）
    htmjm = Column(Numeric(12, 2), nullable=True, comment="合同面积（亩）")
    # 实测面积（亩）
    scmjm = Column(Numeric(12, 2), nullable=True, comment="实测面积（亩）")
    # 地块名称
    dkmc = Column(String(100), nullable=True, comment="地块名称")
    # 所有权性质
    syqxz = Column(String(10), nullable=True, comment="所有权性质")
    # 地块类别
    dklb = Column(String(10), nullable=True, comment="地块类别")
    # 土地用途
    tdyt = Column(String(10), nullable=True, comment="土地用途")
    # 地块等级
    dldj = Column(String(10), nullable=True, comment="地块等级")
    # 地块地址
    dkdz = Column(String(200), nullable=True, comment="地块地址")
    # 地块坐落
    dkxz = Column(String(200), nullable=True, comment="地块坐落")
    # 地块备注
    dkbz = Column(String(500), nullable=True, comment="地块备注")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    contractor = relationship("CBF", backref="land_parcels")
    contract = relationship("CBHT", backref="land_parcels")

    def __repr__(self):
        return f"<CBDKXX(id='{self.id}', dkbm='{self.dkbm}')>"