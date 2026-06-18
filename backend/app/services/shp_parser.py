"""
Shapefile解析服务
负责解析Shapefile文件，进行坐标转换，并写入数据库
"""
import os
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session
from app.models import LandParcelGeom, ImportError

logger = logging.getLogger(__name__)

# 尝试导入geopandas和pyproj
try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.wkt import dumps
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    logger.warning("geopandas未安装，Shapefile解析功能受限")


@dataclass
class ShapefileParseResult:
    """Shapefile解析结果"""
    file_name: str
    total_count: int
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]


class ShapefileParserService:
    """Shapefile解析服务"""

    # 源坐标系（CGCS2000 / 3-degree Gauss-Kruger zone 27）
    SOURCE_CRS = "EPSG:4527"
    
    # 目标坐标系（WGS84）
    TARGET_CRS = "EPSG:4326"
    
    # Shapefile字段名到ORM字段名的映射
    FIELD_MAP = {
        'DKBM': 'dkbm',     # 地块编码
        'DKMC': 'dkmc',     # 地块名称
        'DKMJ': 'dkmj',     # 地块面积
    }

    def __init__(self):
        """
        初始化Shapefile解析服务
        """
        if not HAS_GEOPANDAS:
            logger.warning("geopandas未安装，将无法解析Shapefile")

    def read_shapefile(self, shp_path: str) -> Optional[gpd.GeoDataFrame]:
        """
        读取Shapefile文件
        
        Args:
            shp_path: Shapefile主文件(.shp)路径
            
        Returns:
            GeoDataFrame对象或None
        """
        if not HAS_GEOPANDAS:
            raise RuntimeError("geopandas未安装，无法读取Shapefile")
        
        if not os.path.exists(shp_path):
            raise ValueError(f"Shapefile不存在: {shp_path}")
        
        # 检查必需文件
        shp_base = os.path.splitext(shp_path)[0]
        required_files = [shp_base + ext for ext in ['.shx', '.dbf']]
        for req_file in required_files:
            if not os.path.exists(req_file):
                raise ValueError(f"Shapefile不完整，缺少文件: {req_file}")
        
        try:
            gdf = gpd.read_file(shp_path)
            logger.info(f"读取Shapefile成功: {len(gdf)} 条记录")
            return gdf
        except Exception as e:
            logger.error(f"读取Shapefile失败: {str(e)}")
            raise ValueError(f"读取Shapefile失败: {str(e)}")

    def transform_coordinates(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        将坐标系从EPSG:4527转换为EPSG:4326
        
        Args:
            gdf: 原始GeoDataFrame
            
        Returns:
            转换后的GeoDataFrame
        """
        if not HAS_GEOPANDAS:
            raise RuntimeError("geopandas未安装")
        
        try:
            # 检查当前坐标系
            if gdf.crs is None:
                # 如果没有坐标系信息，假设是EPSG:4527
                gdf = gdf.set_crs(self.SOURCE_CRS)
                logger.info(f"Shapefile未指定坐标系，假设为 {self.SOURCE_CRS}")
            
            # 转换坐标系
            if gdf.crs != self.TARGET_CRS:
                gdf = gdf.to_crs(self.TARGET_CRS)
                logger.info(f"坐标系转换: {self.SOURCE_CRS} -> {self.TARGET_CRS}")
            
            return gdf
        except Exception as e:
            logger.error(f"坐标转换失败: {str(e)}")
            raise ValueError(f"坐标转换失败: {str(e)}")

    def geometry_to_wkt(self, geom: Any) -> str:
        """
        将几何对象转换为WKT格式
        
        Args:
            geom: Shapely几何对象
            
        Returns:
            WKT字符串
        """
        if geom is None:
            return None
        
        try:
            return dumps(geom)
        except Exception as e:
            logger.error(f"几何对象转换WKT失败: {str(e)}")
            return None

    def get_geometry_type(self, geom: Any) -> str:
        """
        获取几何类型
        
        Args:
            geom: Shapely几何对象
            
        Returns:
            几何类型字符串
        """
        if geom is None:
            return None
        
        geom_type = geom.geom_type.upper()
        
        # 标准化几何类型名称
        if geom_type in ['POLYGON', 'MULTIPOLYGON']:
            return geom_type
        else:
            return 'POLYGON'

    def parse_shapefile(
        self,
        shp_path: str,
        db: Session,
        task_id: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ShapefileParseResult:
        """
        解析Shapefile并写入数据库
        
        Args:
            shp_path: Shapefile主文件路径
            db: 数据库会话
            task_id: 导入任务ID
            progress_callback: 进度回调函数
            
        Returns:
            ShapefileParseResult: 解析结果
        """
        errors = []
        success_count = 0
        error_count = 0
        
        if not HAS_GEOPANDAS:
            return ShapefileParseResult(
                file_name=os.path.basename(shp_path),
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'land_parcel_geom',
                    'error_message': 'geopandas未安装，无法解析Shapefile'
                }]
            )
        
        try:
            # 读取Shapefile
            gdf = self.read_shapefile(shp_path)
            
            # 坐标转换
            gdf = self.transform_coordinates(gdf)
            
            total_count = len(gdf)
            logger.info(f"Shapefile共 {total_count} 条记录")
            
            # 逐行处理
            for row_num, row in enumerate(gdf.itertuples(), start=1):
                try:
                    # 获取地块编码
                    dkbm = None
                    for field_name in ['DKBM', 'dkbm', 'Dkbm']:
                        if hasattr(row, field_name):
                            dkbm = getattr(row, field_name)
                            break
                    
                    if not dkbm:
                        error_count += 1
                        errors.append({
                            'table_name': 'land_parcel_geom',
                            'row_number': row_num,
                            'error_message': '地块编码(DKBM)缺失'
                        })
                        continue
                    
                    # 获取几何对象
                    geom = row.geometry
                    
                    if geom is None or geom.is_empty:
                        error_count += 1
                        errors.append({
                            'table_name': 'land_parcel_geom',
                            'row_number': row_num,
                            'code': dkbm,
                            'error_message': '几何对象为空'
                        })
                        continue
                    
                    # 转换为WKT
                    geom_wkt = self.geometry_to_wkt(geom)
                    geom_type = self.get_geometry_type(geom)
                    
                    if not geom_wkt:
                        error_count += 1
                        errors.append({
                            'table_name': 'land_parcel_geom',
                            'row_number': row_num,
                            'code': dkbm,
                            'error_message': '几何对象转换WKT失败'
                        })
                        continue
                    
                    # 创建数据库记录
                    land_geom = LandParcelGeom(
                        dkbm=str(dkbm),
                        geom_wkt=geom_wkt,
                        geom_type=geom_type
                    )
                    
                    db.add(land_geom)
                    db.commit()
                    success_count += 1
                    
                    # 进度回调
                    if progress_callback:
                        progress_callback(row_num, total_count)
                        
                except Exception as e:
                    db.rollback()
                    error_count += 1
                    errors.append({
                        'table_name': 'land_parcel_geom',
                        'row_number': row_num,
                        'code': dkbm if hasattr(row, 'DKBM') else None,
                        'error_message': str(e)
                    })
                    logger.error(f"处理行 {row_num} 失败: {str(e)}")
            
            return ShapefileParseResult(
                file_name=os.path.basename(shp_path),
                total_count=total_count,
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"解析Shapefile失败: {str(e)}")
            return ShapefileParseResult(
                file_name=os.path.basename(shp_path),
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'land_parcel_geom',
                    'error_message': str(e)
                }]
            )

    def get_shapefile_stats(self, shp_path: str) -> Dict[str, Any]:
        """
        获取Shapefile统计信息
        
        Args:
            shp_path: Shapefile路径
            
        Returns:
            统计信息字典
        """
        if not HAS_GEOPANDAS:
            return {'total_count': 0, 'error': 'geopandas未安装'}
        
        try:
            gdf = self.read_shapefile(shp_path)
            return {
                'total_count': len(gdf),
                'crs': str(gdf.crs),
                'geometry_types': gdf.geometry.type.value_counts().to_dict(),
                'columns': list(gdf.columns)
            }
        except Exception as e:
            return {'total_count': 0, 'error': str(e)}

    def validate_shapefile(self, shp_path: str) -> Tuple[bool, List[str]]:
        """
        验证Shapefile是否有效
        
        Args:
            shp_path: Shapefile路径
            
        Returns:
            Tuple[是否有效, 错误消息列表]
        """
        errors = []
        
        if not os.path.exists(shp_path):
            errors.append(f"Shapefile不存在: {shp_path}")
            return False, errors
        
        # 检查必需文件
        shp_base = os.path.splitext(shp_path)[0]
        for ext in ['.shx', '.dbf']:
            if not os.path.exists(shp_base + ext):
                errors.append(f"缺少必需文件: {ext}")
        
        if not HAS_GEOPANDAS:
            errors.append("geopandas未安装")
        
        if errors:
            return False, errors
        
        try:
            gdf = self.read_shapefile(shp_path)
            if len(gdf) == 0:
                errors.append("Shapefile没有数据")
        except Exception as e:
            errors.append(f"读取失败: {str(e)}")
        
        return len(errors) == 0, errors

    def create_import_errors(
        self,
        result: ShapefileParseResult,
        task_id: int
    ) -> List[ImportError]:
        """
        将解析错误转换为ImportError对象
        
        Args:
            result: 解析结果
            task_id: 导入任务ID
            
        Returns:
            ImportError对象列表
        """
        errors = []
        for error in result.errors:
            import_error = ImportError(
                task_id=task_id,
                table_name=error['table_name'],
                code=error.get('code'),
                row_number=error.get('row_number'),
                error_message=error['error_message']
            )
            errors.append(import_error)
        return errors