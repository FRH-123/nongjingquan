"""
XLS代码表解析服务
负责解析XLS文件中的权属单位代码表，构建行政区划树并写入数据库
"""
import os
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session
from app.models import AdminDivision, DictItem, ImportError

logger = logging.getLogger(__name__)

# 尝试导入pandas和openpyxl
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("pandas未安装，XLS解析功能受限")


@dataclass
class XLSParseResult:
    """XLS解析结果"""
    file_name: str
    table_name: str
    total_count: int
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]


@dataclass
class AdminDivisionNode:
    """行政区划节点"""
    code: str
    name: str
    parent_code: Optional[str]
    level: int
    children: List['AdminDivisionNode'] = None


class XLSParserService:
    """XLS代码表解析服务"""

    # 行政区划编码长度对应的层级
    LEVEL_LENGTH_MAP = {
        2: 1,   # 省 (2位)
        4: 2,   # 市 (4位)
        6: 3,   # 县 (6位)
        9: 4,   # 镇 (9位)
        12: 5,  # 村 (12位)
        14: 6,  # 组 (14位)
    }

    # 层级名称
    LEVEL_NAMES = {
        1: '省',
        2: '市',
        3: '县',
        4: '镇',
        5: '村',
        6: '组',
    }

    # 权属单位代码表字段映射
    QSDW_FIELD_MAP = {
        'QSDWDM': 'code',     # 权属单位代码
        'QSDWMC': 'name',     # 权属单位名称
        'SJQSDWDM': 'parent_code',  # 上级权属单位代码
    }

    def __init__(self):
        """
        初始化XLS解析服务
        """
        if not HAS_PANDAS:
            logger.warning("pandas未安装，将无法解析XLS文件")

    def read_xls(self, xls_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        读取XLS/XLSX文件
        
        Args:
            xls_path: XLS文件路径
            sheet_name: 工作表名称（可选）
            
        Returns:
            DataFrame对象或None
        """
        if not HAS_PANDAS:
            raise RuntimeError("pandas未安装，无法读取XLS文件")
        
        if not os.path.exists(xls_path):
            raise ValueError(f"XLS文件不存在: {xls_path}")
        
        try:
            # 根据文件扩展名选择引擎
            ext = os.path.splitext(xls_path)[1].lower()
            if ext == '.xlsx':
                df = pd.read_excel(xls_path, sheet_name=sheet_name, engine='openpyxl')
            else:
                df = pd.read_excel(xls_path, sheet_name=sheet_name, engine='xlrd')
            
            logger.info(f"读取XLS成功: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"读取XLS失败: {str(e)}")
            raise ValueError(f"读取XLS失败: {str(e)}")

    def get_level_by_code_length(self, code: str) -> int:
        """
        根据编码长度确定层级
        
        Args:
            code: 行政区划编码
            
        Returns:
            层级值
        """
        if not code:
            return 0
        
        code_len = len(str(code).strip())
        return self.LEVEL_LENGTH_MAP.get(code_len, 0)

    def get_parent_code(self, code: str) -> Optional[str]:
        """
        根据编码推导上级编码
        
        Args:
            code: 行政区划编码
            
        Returns:
            上级编码
        """
        if not code:
            return None
        
        code_str = str(code).strip()
        code_len = len(code_str)
        
        # 根据编码长度截取上级编码
        parent_len_map = {
            4: 2,    # 市的上级是省(2位)
            6: 4,    # 县的上级是市(4位)
            9: 6,    # 镇的上级是县(6位)
            12: 9,   # 村的上级是镇(9位)
            14: 12,  # 组的上级是村(12位)
        }
        
        parent_len = parent_len_map.get(code_len)
        if parent_len:
            return code_str[:parent_len]
        
        return None

    def build_admin_division_tree(
        self,
        df: pd.DataFrame,
        code_column: str = 'QSDWDM',
        name_column: str = 'QSDWMC'
    ) -> List[AdminDivisionNode]:
        """
        构建行政区划树
        
        Args:
            df: 数据DataFrame
            code_column: 编码列名
            name_column: 名称列名
            
        Returns:
            行政区划节点列表
        """
        nodes = []
        node_map = {}  # 编码到节点的映射
        
        # 尝试多种可能的列名
        possible_code_cols = [code_column, 'QSDWDM', 'qsdwdm', '代码', '编码', 'CODE', 'code']
        possible_name_cols = [name_column, 'QSDWMC', 'qsdwmc', '名称', 'NAME', 'name']
        
        # 找到实际的列名
        actual_code_col = None
        actual_name_col = None
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            for possible in possible_code_cols:
                if col_lower == possible.lower():
                    actual_code_col = col
                    break
            if actual_code_col:
                break
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            for possible in possible_name_cols:
                if col_lower == possible.lower():
                    actual_name_col = col
                    break
            if actual_name_col:
                break
        
        if not actual_code_col or not actual_name_col:
            logger.error(f"未找到编码或名称列，现有列: {list(df.columns)}")
            return []
        
        logger.info(f"使用列: 编码={actual_code_col}, 名称={actual_name_col}")
        
        # 创建节点
        for _, row in df.iterrows():
            code = str(row[actual_code_col]).strip() if pd.notna(row[actual_code_col]) else None
            name = str(row[actual_name_col]).strip() if pd.notna(row[actual_name_col]) else None
            
            if not code or not name:
                continue
            
            level = self.get_level_by_code_length(code)
            parent_code = self.get_parent_code(code)
            
            node = AdminDivisionNode(
                code=code,
                name=name,
                parent_code=parent_code,
                level=level,
                children=[]
            )
            
            nodes.append(node)
            node_map[code] = node
        
        # 构建父子关系
        for node in nodes:
            if node.parent_code and node.parent_code in node_map:
                parent = node_map[node.parent_code]
                if parent.children is None:
                    parent.children = []
                parent.children.append(node)
        
        logger.info(f"构建行政区划树完成: {len(nodes)} 个节点")
        return nodes

    def parse_admin_division(
        self,
        xls_path: str,
        db: Session,
        task_id: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> XLSParseResult:
        """
        解析权属单位代码表并写入数据库
        
        Args:
            xls_path: XLS文件路径
            db: 数据库会话
            task_id: 导入任务ID
            progress_callback: 进度回调函数
            
        Returns:
            XLSParseResult: 解析结果
        """
        errors = []
        success_count = 0
        error_count = 0
        
        if not HAS_PANDAS:
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='admin_division',
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'admin_division',
                    'error_message': 'pandas未安装，无法解析XLS文件'
                }]
            )
        
        try:
            # 读取XLS文件
            df = self.read_xls(xls_path)
            
            # 构建行政区划树
            nodes = self.build_admin_division_tree(df)
            
            total_count = len(nodes)
            logger.info(f"权属单位代码表共 {total_count} 条记录")
            
            # 清空现有行政区划数据（可选，根据需求）
            # db.query(AdminDivision).delete()
            # db.commit()
            
            # 逐条写入数据库
            for node_num, node in enumerate(nodes, start=1):
                try:
                    # 检查是否已存在
                    existing = db.query(AdminDivision).filter(
                        AdminDivision.code == node.code
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.name = node.name
                        existing.parent_code = node.parent_code
                        existing.level = node.level
                    else:
                        # 创建新记录
                        admin_div = AdminDivision(
                            code=node.code,
                            name=node.name,
                            parent_code=node.parent_code,
                            level=node.level
                        )
                        db.add(admin_div)
                    
                    db.commit()
                    success_count += 1
                    
                    # 进度回调
                    if progress_callback:
                        progress_callback(node_num, total_count)
                        
                except Exception as e:
                    db.rollback()
                    error_count += 1
                    errors.append({
                        'table_name': 'admin_division',
                        'row_number': node_num,
                        'code': node.code,
                        'error_message': str(e)
                    })
                    logger.error(f"处理节点 {node_num} 失败: {str(e)}")
            
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='admin_division',
                total_count=total_count,
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"解析权属单位代码表失败: {str(e)}")
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='admin_division',
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'admin_division',
                    'error_message': str(e)
                }]
            )

    def parse_dict_items(
        self,
        xls_path: str,
        db: Session,
        task_id: int,
        category: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> XLSParseResult:
        """
        解析字典表并写入数据库
        
        Args:
            xls_path: XLS文件路径
            db: 数据库会话
            task_id: 导入任务ID
            category: 字典类别
            progress_callback: 进度回调函数
            
        Returns:
            XLSParseResult: 解析结果
        """
        errors = []
        success_count = 0
        error_count = 0
        
        if not HAS_PANDAS:
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='dict_item',
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'dict_item',
                    'error_message': 'pandas未安装，无法解析XLS文件'
                }]
            )
        
        try:
            # 读取XLS文件
            df = self.read_xls(xls_path)
            
            # 尝试多种可能的列名
            possible_code_cols = ['代码', '编码', 'CODE', 'code', 'DM']
            possible_name_cols = ['名称', 'NAME', 'name', 'MC']
            
            actual_code_col = None
            actual_name_col = None
            
            for col in df.columns:
                col_str = str(col).strip()
                if col_str in possible_code_cols or col_str.lower() in [c.lower() for c in possible_code_cols]:
                    actual_code_col = col
                    break
            
            for col in df.columns:
                col_str = str(col).strip()
                if col_str in possible_name_cols or col_str.lower() in [c.lower() for c in possible_name_cols]:
                    actual_name_col = col
                    break
            
            if not actual_code_col or not actual_name_col:
                logger.warning(f"未找到编码或名称列，现有列: {list(df.columns)}")
                return XLSParseResult(
                    file_name=os.path.basename(xls_path),
                    table_name='dict_item',
                    total_count=0,
                    success_count=0,
                    error_count=1,
                    errors=[{
                        'table_name': 'dict_item',
                        'error_message': '未找到编码或名称列'
                    }]
                )
            
            total_count = len(df)
            logger.info(f"字典表 {category} 共 {total_count} 条记录")
            
            # 逐条写入数据库
            for row_num, row in enumerate(df.itertuples(), start=1):
                try:
                    code = getattr(row, actual_code_col, None)
                    name = getattr(row, actual_name_col, None)
                    
                    if pd.isna(code) or pd.isna(name):
                        continue
                    
                    code = str(code).strip()
                    name = str(name).strip()
                    
                    if not code or not name:
                        continue
                    
                    # 检查是否已存在
                    existing = db.query(DictItem).filter(
                        DictItem.category == category,
                        DictItem.code == code
                    ).first()
                    
                    if existing:
                        existing.name = name
                    else:
                        dict_item = DictItem(
                            category=category,
                            code=code,
                            name=name,
                            sort_order=row_num
                        )
                        db.add(dict_item)
                    
                    db.commit()
                    success_count += 1
                    
                    if progress_callback:
                        progress_callback(row_num, total_count)
                        
                except Exception as e:
                    db.rollback()
                    error_count += 1
                    errors.append({
                        'table_name': 'dict_item',
                        'row_number': row_num,
                        'code': str(code) if code else None,
                        'error_message': str(e)
                    })
            
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='dict_item',
                total_count=total_count,
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"解析字典表失败: {str(e)}")
            return XLSParseResult(
                file_name=os.path.basename(xls_path),
                table_name='dict_item',
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': 'dict_item',
                    'error_message': str(e)
                }]
            )

    def create_import_errors(
        self,
        result: XLSParseResult,
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

    def get_xls_stats(self, xls_path: str) -> Dict[str, Any]:
        """
        获取XLS文件统计信息
        
        Args:
            xls_path: XLS文件路径
            
        Returns:
            统计信息字典
        """
        if not HAS_PANDAS:
            return {'total_count': 0, 'error': 'pandas未安装'}
        
        try:
            df = self.read_xls(xls_path)
            return {
                'total_count': len(df),
                'columns': list(df.columns),
                'sheets': pd.ExcelFile(xls_path).sheet_names
            }
        except Exception as e:
            return {'total_count': 0, 'error': str(e)}