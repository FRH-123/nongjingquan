"""
地块空间几何模型 (LandParcelGeom)
存储从 Shapefile 导入的地块几何数据
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# Try to import Geometry from geoalchemy2, fallback for SQLite
try:
    from geoalchemy2 import Geometry
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False


class LandParcelGeom(Base):
    """
    地块空间几何表
    存储从 DK.shp 导入的地块多边形几何数据
    坐标系: EPSG:4326 (WGS84)
    """
    __tablename__ = "land_parcel_geom"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 地块编码（外键关联到 cbdkxx）
    dkbm = Column(String(19), ForeignKey("cbdkxx.dkbm"), nullable=True, unique=True, comment="地块编码")
    # 地块几何 (Polygon, SRID=4326)
    # 使用 WKT 格式存储几何数据
    geom_wkt = Column(String, nullable=True, comment="地块几何 WKT 格式")
    # 几何类型
    geom_type = Column(String(20), nullable=True, default="POLYGON", comment="几何类型")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    land_parcel = relationship("CBDKXX", backref="geometry", foreign_keys=[dkbm], primaryjoin="LandParcelGeom.dkbm == CBDKXX.dkbm")

    def __repr__(self):
        return f"<LandParcelGeom(id={self.id}, dkbm='{self.dkbm}')>"