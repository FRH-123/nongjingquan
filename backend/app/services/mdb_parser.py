"""
MDB解析服务
负责解析MDB文件中的业务表数据并写入数据库
"""
import os
import subprocess
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
import csv

from sqlalchemy.orm import Session
from app.models import (
    FBF, CBF, CBFJTCY, CBHT, CBDKXX, 
    DictItem, ImportError
)
from app.services.validator import DataValidator

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """解析结果"""
    table_name: str
    total_count: int
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]


class MDBParserService:
    """MDB解析服务"""

    # MDB表名到ORM模型的映射
    TABLE_MODEL_MAP = {
        'FBF': FBF,
        'CBF': CBF,
        'CBF_JTCY': CBFJTCY,
        'CBHT': CBHT,
        'CBDKXX': CBDKXX,
    }

    # MDB表字段名到ORM字段名的映射（处理大小写和命名差异）
    FIELD_MAPS = {
        'FBF': {
            'FBFBM': 'fbfbm',
            'FBFMC': 'fbfmc',
            'FBFFZRXM': 'fbffzrxm',
        },
        'CBF': {
            'CBFBM': 'cbfbm',
            'CBFMC': 'cbfmc',
            'CBFZJLX': 'cbfzjlx',
            'CBFZJHM': 'cbfzjhm',
            'CBFCYSL': 'cbfcysl',
        },
        'CBF_JTCY': {
            'CBFBM': 'cbfbm',
            'CYXM': 'cyxm',
            'YHZGX': 'yhzgx',
            'SFZHM': 'sfzhm',
        },
        'CBHT': {
            'CBHTBM': 'cbhtbm',
            'FBFBM': 'fbfbm',
            'CBFBM': 'cbfbm',
            'CBFS': 'cbfs',
            'CBQXQ': 'cbqxq',
            'CBQXZ': 'cbqxz',
            'HTMJM': 'htmjm',
            'CBDKZS': 'cbdkzs',
        },
        'CBDKXX': {
            'ID': 'id',
            'CBFBM': 'cbfbm',
            'CBHTBM': 'cbhtbm',
            'DKBM': 'dkbm',
            'CBJYQZBM': 'cbjyqzbm',
            'HTMJM': 'htmjm',
            'SCMJM': 'scmjm',
            'DKMC': 'dkmc',
            'SYQXZ': 'syqxz',
            'DKLB': 'dklb',
            'TDYT': 'tdyt',
            'DLDJ': 'dldj',
            'DKDZ': 'dkdz',
            'DKXZ': 'dkxz',
            'DKBZ': 'dkbz',
        },
    }

    def __init__(self, validator: Optional[DataValidator] = None):
        """
        初始化MDB解析服务
        
        Args:
            validator: 数据校验器
        """
        self.validator = validator or DataValidator()
        self._mdb_tools_available = self._check_mdb_tools()

    def _check_mdb_tools(self) -> bool:
        """检查mdb-tools是否可用"""
        try:
            result = subprocess.run(
                ['mdb-tables', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_table_list(self, mdb_path: str) -> List[str]:
        """
        获取MDB文件中的表列表
        
        Args:
            mdb_path: MDB文件路径
            
        Returns:
            表名列表
        """
        if not os.path.exists(mdb_path):
            raise ValueError(f"MDB文件不存在: {mdb_path}")
        
        if self._mdb_tools_available:
            try:
                result = subprocess.run(
                    ['mdb-tables', mdb_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    tables = result.stdout.strip().split()
                    return [t for t in tables if t in self.TABLE_MODEL_MAP]
            except Exception as e:
                logger.error(f"获取MDB表列表失败: {str(e)}")
        
        # 如果mdb-tools不可用，返回默认表列表
        logger.warning("mdb-tools不可用，使用默认表列表")
        return list(self.TABLE_MODEL_MAP.keys())

    def export_table_to_csv(self, mdb_path: str, table_name: str) -> str:
        """
        将MDB表导出为CSV文件
        
        Args:
            mdb_path: MDB文件路径
            table_name: 表名
            
        Returns:
            CSV文件路径
        """
        csv_path = os.path.join(
            tempfile.gettempdir(),
            f"mdb_export_{table_name}.csv"
        )
        
        if self._mdb_tools_available:
            try:
                result = subprocess.run(
                    ['mdb-export', mdb_path, table_name],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    logger.info(f"导出表 {table_name} 到 {csv_path}")
                    return csv_path
                else:
                    logger.error(f"mdb-export失败: {result.stderr}")
            except Exception as e:
                logger.error(f"导出MDB表失败: {str(e)}")
        
        raise ValueError(f"无法导出MDB表 {table_name}，请确保mdb-tools已安装")

    def parse_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        解析CSV文件
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            数据行列表
        """
        rows = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 清理空值
                    cleaned_row = {
                        k: (v if v and v.strip() else None)
                        for k, v in row.items()
                    }
                    rows.append(cleaned_row)
        except Exception as e:
            logger.error(f"解析CSV失败: {str(e)}")
        
        return rows

    def map_fields(self, table_name: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        将MDB字段映射到ORM字段
        
        Args:
            table_name: 表名
            row: 原始数据行
            
        Returns:
            映射后的数据行
        """
        field_map = self.FIELD_MAPS.get(table_name, {})
        mapped_row = {}
        
        for mdb_field, orm_field in field_map.items():
            # 尝试多种可能的字段名格式
            value = None
            for possible_name in [mdb_field, mdb_field.lower(), mdb_field.upper()]:
                if possible_name in row:
                    value = row[possible_name]
                    break
            
            if value is not None:
                mapped_row[orm_field] = value
        
        return mapped_row

    def parse_table(
        self,
        mdb_path: str,
        table_name: str,
        db: Session,
        task_id: int,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ParseResult:
        """
        解析MDB表并写入数据库
        
        Args:
            mdb_path: MDB文件路径
            table_name: 表名
            db: 数据库会话
            task_id: 导入任务ID
            progress_callback: 进度回调函数
            
        Returns:
            ParseResult: 解析结果
        """
        errors = []
        success_count = 0
        error_count = 0
        
        try:
            # 导出表到CSV
            csv_path = self.export_table_to_csv(mdb_path, table_name)
            
            # 解析CSV
            rows = self.parse_csv(csv_path)
            total_count = len(rows)
            
            logger.info(f"表 {table_name} 共 {total_count} 条记录")
            
            # 获取ORM模型
            model = self.TABLE_MODEL_MAP.get(table_name)
            if not model:
                logger.warning(f"未找到表 {table_name} 的ORM模型")
                return ParseResult(
                    table_name=table_name,
                    total_count=total_count,
                    success_count=0,
                    error_count=total_count,
                    errors=[{
                        'table_name': table_name,
                        'error_message': f"未找到表 {table_name} 的ORM模型"
                    }]
                )
            
            # 逐行处理
            for row_num, row in enumerate(rows, start=1):
                try:
                    # 字段映射
                    mapped_row = self.map_fields(table_name, row)
                    
                    # 数据校验
                    validation_errors = self.validator.validate_row(table_name, mapped_row)
                    if validation_errors:
                        error_count += 1
                        errors.append({
                            'table_name': table_name,
                            'row_number': row_num,
                            'code': mapped_row.get('fbfbm') or mapped_row.get('cbfbm') or mapped_row.get('cbhtbm') or mapped_row.get('dkbm'),
                            'error_message': '; '.join(validation_errors)
                        })
                        continue
                    
                    # 创建ORM对象
                    obj = model(**mapped_row)
                    
                    # 写入数据库
                    db.add(obj)
                    db.commit()
                    success_count += 1
                    
                    # 进度回调
                    if progress_callback:
                        progress_callback(row_num, total_count)
                        
                except Exception as e:
                    db.rollback()
                    error_count += 1
                    errors.append({
                        'table_name': table_name,
                        'row_number': row_num,
                        'code': mapped_row.get('fbfbm') or mapped_row.get('cbfbm') or mapped_row.get('cbhtbm') or mapped_row.get('dkbm'),
                        'error_message': str(e)
                    })
                    logger.error(f"处理行 {row_num} 失败: {str(e)}")
            
            # 清理临时CSV文件
            if os.path.exists(csv_path):
                os.remove(csv_path)
            
            return ParseResult(
                table_name=table_name,
                total_count=total_count,
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"解析表 {table_name} 失败: {str(e)}")
            return ParseResult(
                table_name=table_name,
                total_count=0,
                success_count=0,
                error_count=1,
                errors=[{
                    'table_name': table_name,
                    'error_message': str(e)
                }]
            )

    def parse_all_tables(
        self,
        mdb_path: str,
        db: Session,
        task_id: int,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Tuple[List[ParseResult], List[ImportError]]:
        """
        解析MDB文件中的所有业务表
        
        Args:
            mdb_path: MDB文件路径
            db: 数据库会话
            task_id: 导入任务ID
            progress_callback: 进度回调函数 (表名, 当前行, 总行数)
            
        Returns:
            Tuple[解析结果列表, 错误记录列表]
        """
        results = []
        all_errors = []
        
        # 获取表列表
        tables = self.get_table_list(mdb_path)
        logger.info(f"MDB文件包含以下业务表: {tables}")
        
        # 按顺序解析各表（考虑外键依赖）
        parse_order = ['FBF', 'CBF', 'CBF_JTCY', 'CBHT', 'CBDKXX']
        
        for table_name in parse_order:
            if table_name not in tables:
                logger.warning(f"MDB中未找到表 {table_name}")
                continue
            
            def table_progress(current, total):
                if progress_callback:
                    progress_callback(table_name, current, total)
            
            result = self.parse_table(
                mdb_path, table_name, db, task_id, table_progress
            )
            results.append(result)
            
            # 收集错误记录
            for error in result.errors:
                import_error = ImportError(
                    task_id=task_id,
                    table_name=error['table_name'],
                    code=error.get('code'),
                    row_number=error.get('row_number'),
                    error_message=error['error_message']
                )
                all_errors.append(import_error)
        
        return results, all_errors

    def get_table_stats(self, mdb_path: str) -> Dict[str, int]:
        """
        获取MDB各表的记录数统计
        
        Args:
            mdb_path: MDB文件路径
            
        Returns:
            表名到记录数的映射
        """
        stats = {}
        
        for table_name in self.TABLE_MODEL_MAP.keys():
            try:
                csv_path = self.export_table_to_csv(mdb_path, table_name)
                rows = self.parse_csv(csv_path)
                stats[table_name] = len(rows)
                if os.path.exists(csv_path):
                    os.remove(csv_path)
            except Exception:
                stats[table_name] = 0
        
        return stats