"""
承包方模型 (CBF - 承包方表)
对应 MDB 中的 CBF 表
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class CBF(Base):
    """
    承包方表（农户）
    对应内业软件输出的 CBF 表
    """
    __tablename__ = "cbf"

    # 承包方编码 (18位: 省2+市2+县2+镇3+村3+组2+顺序号4)
    cbfbm = Column(String(18), primary_key=True, comment="承包方编码")
    # 承包方名称（户主姓名）
    cbfmc = Column(String(100), nullable=True, comment="承包方名称")
    # 承包方证件类型
    cbfzjlx = Column(String(10), nullable=True, comment="承包方证件类型")
    # 承包方证件号码
    cbfzjhm = Column(String(30), nullable=True, comment="承包方证件号码")
    # 承包方成员数量
    cbfcysl = Column(Integer, nullable=True, comment="承包方成员数量")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<CBF(cbfbm='{self.cbfbm}', cbfmc='{self.cbfmc}')>"