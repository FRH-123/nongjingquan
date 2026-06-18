"""
ZIP解压与文件识别服务
负责解压上传的ZIP文件并识别其中的MDB、Shapefile、XLS文件
"""
import os
import zipfile
import tempfile
import shutil
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

from app.schemas.import_schema import ParsedFileInfo

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    file_path: str
    file_name: str
    file_size: int
    file_type: str  # 'mdb', 'shp', 'xls', 'other'


class UnzipService:
    """ZIP解压与文件识别服务"""

    # 需要识别的文件扩展名
    MDB_EXTENSIONS = {'.mdb', '.accdb'}
    SHP_EXTENSIONS = {'.shp'}  # Shapefile主文件
    SHP_REQUIRED_FILES = {'.shp', '.shx', '.dbf'}  # Shapefile必需文件
    XLS_EXTENSIONS = {'.xls', '.xlsx'}
    
    # MDB中的业务表名
    MDB_TABLES = [
        'FBF',        # 发包方
        'CBF',        # 承包方
        'CBF_JTCY',   # 家庭成员
        'CBHT',       # 合同
        'CBDKXX',     # 承包地块
        'CBJYQZ',     # 承包经营权证
        'FBF_JTCY',   # 发包方家庭成员
        'DK',         # 地块
        'DKXX',       # 地块信息
        'QSDW',       # 权属单位
        'XZQH',       # 行政区划
        'ZD',         # 字典
    ]

    def __init__(self, temp_dir: Optional[str] = None):
        """
        初始化服务
        
        Args:
            temp_dir: 临时目录路径，默认使用系统临时目录
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.extract_base_dir = os.path.join(self.temp_dir, "land_rights_import")
        os.makedirs(self.extract_base_dir, exist_ok=True)

    def extract_zip(self, zip_path: str, task_id: int) -> Tuple[str, List[str]]:
        """
        解压ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            task_id: 任务ID，用于创建唯一解压目录
            
        Returns:
            Tuple[解压目录路径, 解压后的文件列表]
            
        Raises:
            ValueError: 如果ZIP文件无效
        """
        if not os.path.exists(zip_path):
            raise ValueError(f"ZIP文件不存在: {zip_path}")
        
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"不是有效的ZIP文件: {zip_path}")
        
        # 创建任务专属解压目录
        extract_dir = os.path.join(self.extract_base_dir, f"task_{task_id}")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
        
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取ZIP中的所有文件
                file_list = zip_ref.namelist()
                
                # 过滤掉目录和隐藏文件
                files_to_extract = [
                    f for f in file_list 
                    if not f.endswith('/') and not os.path.basename(f).startswith('.')
                ]
                
                # 解压文件
                for file_in_zip in files_to_extract:
                    # 获取文件名（去除路径）
                    file_name = os.path.basename(file_in_zip)
                    if not file_name:
                        continue
                    
                    # 解压到目标目录
                    target_path = os.path.join(extract_dir, file_name)
                    
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # 解压文件
                    with zip_ref.open(file_in_zip) as source:
                        with open(target_path, 'wb') as target:
                            target.write(source.read())
                    
                    extracted_files.append(target_path)
                    logger.info(f"解压文件: {file_name} -> {target_path}")
                
                logger.info(f"ZIP解压完成: {len(extracted_files)} 个文件")
                
        except zipfile.BadZipFile as e:
            raise ValueError(f"ZIP文件损坏: {str(e)}")
        except Exception as e:
            logger.error(f"解压失败: {str(e)}")
            raise ValueError(f"解压失败: {str(e)}")
        
        return extract_dir, extracted_files

    def identify_files(self, extract_dir: str) -> ParsedFileInfo:
        """
        识别解压目录中的文件类型
        
        Args:
            extract_dir: 解压目录路径
            
        Returns:
            ParsedFileInfo: 包含各类文件列表的信息对象
        """
        mdb_files = []
        shp_files = []
        xls_files = []
        
        if not os.path.exists(extract_dir):
            logger.warning(f"解压目录不存在: {extract_dir}")
            return ParsedFileInfo(
                mdb_files=[],
                shp_files=[],
                xls_files=[],
                extract_path=extract_dir
            )
        
        # 遍历目录中的文件
        for root, dirs, files in os.walk(extract_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                _, ext = os.path.splitext(file_name)
                ext_lower = ext.lower()
                
                if ext_lower in self.MDB_EXTENSIONS:
                    mdb_files.append(file_path)
                    logger.info(f"发现MDB文件: {file_name}")
                    
                elif ext_lower in self.SHP_EXTENSIONS:
                    # 检查Shapefile是否完整
                    shp_base = os.path.splitext(file_path)[0]
                    required_files = [
                        shp_base + ext for ext in self.SHP_REQUIRED_FILES
                    ]
                    if all(os.path.exists(f) for f in required_files):
                        shp_files.append(file_path)
                        logger.info(f"发现完整Shapefile: {file_name}")
                    else:
                        logger.warning(f"Shapefile不完整，缺少必需文件: {file_name}")
                        
                elif ext_lower in self.XLS_EXTENSIONS:
                    xls_files.append(file_path)
                    logger.info(f"发现XLS文件: {file_name}")
        
        return ParsedFileInfo(
            mdb_files=mdb_files,
            shp_files=shp_files,
            xls_files=xls_files,
            extract_path=extract_dir
        )

    def cleanup(self, task_id: int) -> None:
        """
        清理任务相关的临时文件
        
        Args:
            task_id: 任务ID
        """
        extract_dir = os.path.join(self.extract_base_dir, f"task_{task_id}")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            logger.info(f"清理临时目录: {extract_dir}")

    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        获取文件详细信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            FileInfo对象或None
        """
        if not os.path.exists(file_path):
            return None
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        _, ext = os.path.splitext(file_name)
        ext_lower = ext.lower()
        
        if ext_lower in self.MDB_EXTENSIONS:
            file_type = 'mdb'
        elif ext_lower in self.SHP_EXTENSIONS:
            file_type = 'shp'
        elif ext_lower in self.XLS_EXTENSIONS:
            file_type = 'xls'
        else:
            file_type = 'other'
        
        return FileInfo(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type
        )

    def validate_zip_structure(self, zip_path: str) -> Tuple[bool, List[str]]:
        """
        验证ZIP文件结构是否符合要求
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            Tuple[是否有效, 错误消息列表]
        """
        errors = []
        
        if not os.path.exists(zip_path):
            errors.append(f"ZIP文件不存在: {zip_path}")
            return False, errors
        
        if not zipfile.is_zipfile(zip_path):
            errors.append("不是有效的ZIP文件")
            return False, errors
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # 检查是否有MDB文件
                has_mdb = any(
                    os.path.splitext(f)[1].lower() in self.MDB_EXTENSIONS
                    for f in file_list
                )
                if not has_mdb:
                    errors.append("ZIP中未找到MDB文件")
                
                # 检查是否有Shapefile
                has_shp = any(
                    os.path.splitext(f)[1].lower() == '.shp'
                    for f in file_list
                )
                if not has_shp:
                    errors.append("ZIP中未找到Shapefile文件")
                
                # 检查是否有XLS文件（可选）
                has_xls = any(
                    os.path.splitext(f)[1].lower() in self.XLS_EXTENSIONS
                    for f in file_list
                )
                if not has_xls:
                    logger.warning("ZIP中未找到XLS文件（行政区划代码表）")
                
        except Exception as e:
            errors.append(f"读取ZIP文件失败: {str(e)}")
            return False, errors
        
        # MDB和Shapefile是必需的
        is_valid = len(errors) == 0 or (has_mdb and has_shp)
        
        return is_valid, errors