"""
数据校验服务
负责对导入数据进行编码格式校验、必填字段校验、外键引用完整性校验
"""
import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """校验规则"""
    field_name: str
    rule_type: str  # 'required', 'length', 'pattern', 'range', 'foreign_key'
    rule_value: Any
    error_message: str


class DataValidator:
    """数据校验服务"""

    # 编码长度规则
    CODE_LENGTH_RULES = {
        'FBF': {
            'fbfbm': 14,  # 发包方编码：14位（省2+市2+县2+镇3+村3+组1）
        },
        'CBF': {
            'cbfbm': 18,  # 承包方编码：18位（省2+市2+县2+镇3+村3+组2+顺序号4）
        },
        'CBHT': {
            'cbhtbm': 19,  # 承包合同编码：19位
        },
        'CBDKXX': {
            'dkbm': 19,    # 地块编码：19位
            'cbjyqzbm': 19,  # 承包经营权证编码：19位
        },
        'CBF_JTCY': {
            'cbfbm': 18,  # 承包方编码：18位
        },
    }

    # 必填字段规则
    REQUIRED_FIELDS = {
        'FBF': ['fbfbm'],
        'CBF': ['cbfbm'],
        'CBHT': ['cbhtbm'],
        'CBDKXX': ['id', 'dkbm'],
        'CBF_JTCY': ['cbfbm'],
    }

    # 编码格式正则表达式
    CODE_PATTERNS = {
        'fbfbm': r'^\d{14}$',      # 14位数字
        'cbfbm': r'^\d{18}$',      # 18位数字
        'cbhtbm': r'^\d{19}$',     # 19位数字
        'dkbm': r'^\d{19}$',       # 19位数字
        'cbjyqzbm': r'^\d{19}$',   # 19位数字
    }

    # 外键引用规则
    FOREIGN_KEY_RULES = {
        'CBF': {
            # 承包方编码的前14位应引用发包方编码
            'cbfbm_fbf': ('cbfbm', 'FBF', 'fbfbm', '前14位')
        },
        'CBHT': {
            'fbfbm': ('fbfbm', 'FBF', 'fbfbm', '完整'),
            'cbfbm': ('cbfbm', 'CBF', 'cbfbm', '完整'),
        },
        'CBDKXX': {
            'cbfbm': ('cbfbm', 'CBF', 'cbfbm', '完整'),
            'cbhtbm': ('cbhtbm', 'CBHT', 'cbhtbm', '完整'),
        },
        'CBF_JTCY': {
            'cbfbm': ('cbfbm', 'CBF', 'cbfbm', '完整'),
        },
    }

    def __init__(self):
        """
        初始化数据校验服务
        """
        # 缓存已导入的编码集合，用于外键校验
        self._fbfbm_cache: Set[str] = set()
        self._cbfbm_cache: Set[str] = set()
        self._cbhtbm_cache: Set[str] = set()
        self._dkbm_cache: Set[str] = set()

    def update_cache(self, table_name: str, codes: List[str]) -> None:
        """
        更新编码缓存
        
        Args:
            table_name: 表名
            codes: 编码列表
        """
        if table_name == 'FBF':
            self._fbfbm_cache.update(codes)
        elif table_name == 'CBF':
            self._cbfbm_cache.update(codes)
        elif table_name == 'CBHT':
            self._cbhtbm_cache.update(codes)
        elif table_name == 'CBDKXX':
            self._dkbm_cache.update(codes)

    def clear_cache(self) -> None:
        """
        清空编码缓存
        """
        self._fbfbm_cache.clear()
        self._cbfbm_cache.clear()
        self._cbhtbm_cache.clear()
        self._dkbm_cache.clear()

    def validate_code_length(self, table_name: str, field_name: str, value: str) -> Optional[str]:
        """
        校验编码长度
        
        Args:
            table_name: 表名
            field_name: 字段名
            value: 编码值
            
        Returns:
            错误消息或None
        """
        if not value:
            return None
        
        rules = self.CODE_LENGTH_RULES.get(table_name, {})
        expected_length = rules.get(field_name)
        
        if expected_length and len(str(value)) != expected_length:
            return f"{field_name}编码长度应为{expected_length}位，实际为{len(str(value))}位"
        
        return None

    def validate_code_pattern(self, field_name: str, value: str) -> Optional[str]:
        """
        校验编码格式
        
        Args:
            field_name: 字段名
            value: 编码值
            
        Returns:
            错误消息或None
        """
        if not value:
            return None
        
        pattern = self.CODE_PATTERNS.get(field_name)
        
        if pattern and not re.match(pattern, str(value)):
            return f"{field_name}编码格式不正确，应为数字编码"
        
        return None

    def validate_required_field(self, table_name: str, row: Dict[str, Any]) -> List[str]:
        """
        校验必填字段
        
        Args:
            table_name: 表名
            row: 数据行
            
        Returns:
            错误消息列表
        """
        errors = []
        required_fields = self.REQUIRED_FIELDS.get(table_name, [])
        
        for field in required_fields:
            value = row.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"{field}为必填字段，不能为空")
        
        return errors

    def validate_foreign_key(
        self,
        table_name: str,
        field_name: str,
        value: str,
        match_type: str = '完整'
    ) -> Optional[str]:
        """
        校验外键引用
        
        Args:
            table_name: 表名
            field_name: 字段名
            value: 编码值
            match_type: 匹配类型（'完整' 或 '前N位'）
            
        Returns:
            错误消息或None
        """
        if not value:
            return None
        
        # 根据匹配类型获取要匹配的值
        if match_type.startswith('前'):
            # 提取前N位
            try:
                n = int(match_type.replace('前', '').replace('位', ''))
                match_value = str(value)[:n]
            except ValueError:
                match_value = str(value)
        else:
            match_value = str(value)
        
        # 检查缓存
        if field_name == 'fbfbm':
            if match_value not in self._fbfbm_cache:
                return f"外键引用失败：{field_name}={match_value}在FBF表中不存在"
        elif field_name == 'cbfbm':
            if match_value not in self._cbfbm_cache:
                return f"外键引用失败：{field_name}={match_value}在CBF表中不存在"
        elif field_name == 'cbhtbm':
            if match_value not in self._cbhtbm_cache:
                return f"外键引用失败：{field_name}={match_value}在CBHT表中不存在"
        
        return None

    def validate_row(self, table_name: str, row: Dict[str, Any]) -> List[str]:
        """
        校验单行数据
        
        Args:
            table_name: 表名
            row: 数据行
            
        Returns:
            错误消息列表
        """
        errors = []
        
        # 1. 必填字段校验
        required_errors = self.validate_required_field(table_name, row)
        errors.extend(required_errors)
        
        # 2. 编码长度校验
        length_rules = self.CODE_LENGTH_RULES.get(table_name, {})
        for field_name in length_rules.keys():
            value = row.get(field_name)
            if value:
                length_error = self.validate_code_length(table_name, field_name, value)
                if length_error:
                    errors.append(length_error)
        
        # 3. 编码格式校验
        for field_name in self.CODE_PATTERNS.keys():
            value = row.get(field_name)
            if value:
                pattern_error = self.validate_code_pattern(field_name, value)
                if pattern_error:
                    errors.append(pattern_error)
        
        # 4. 外键引用校验（可选，根据导入顺序决定）
        # 注意：外键校验需要依赖已导入的数据，在导入编排服务中处理
        
        return errors

    def validate_all_foreign_keys(
        self,
        table_name: str,
        row: Dict[str, Any]
    ) -> List[str]:
        """
        校验所有外键引用
        
        Args:
            table_name: 表名
            row: 数据行
            
        Returns:
            错误消息列表
        """
        errors = []
        
        fk_rules = self.FOREIGN_KEY_RULES.get(table_name, {})
        for rule_name, (field_name, ref_table, ref_field, match_type) in fk_rules.items():
            value = row.get(field_name)
            if value:
                fk_error = self.validate_foreign_key(
                    table_name, field_name, value, match_type
                )
                if fk_error:
                    errors.append(fk_error)
        
        return errors

    def validate_batch(
        self,
        table_name: str,
        rows: List[Dict[str, Any]]
    ) -> Dict[int, List[str]]:
        """
        批量校验数据
        
        Args:
            table_name: 表名
            rows: 数据行列表
            
        Returns:
            行号到错误消息列表的映射
        """
        all_errors = {}
        
        for row_num, row in enumerate(rows, start=1):
            errors = self.validate_row(table_name, row)
            if errors:
                all_errors[row_num] = errors
        
        return all_errors

    def get_validation_summary(
        self,
        table_name: str,
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        获取校验摘要
        
        Args:
            table_name: 表名
            rows: 数据行列表
            
        Returns:
            校验摘要字典
        """
        all_errors = self.validate_batch(table_name, rows)
        
        error_count = len(all_errors)
        success_count = len(rows) - error_count
        
        # 统计错误类型
        error_types = {}
        for row_num, errors in all_errors.items():
            for error in errors:
                # 提取错误类型
                if '必填' in error:
                    error_types['必填字段'] = error_types.get('必填字段', 0) + 1
                elif '长度' in error:
                    error_types['编码长度'] = error_types.get('编码长度', 0) + 1
                elif '格式' in error:
                    error_types['编码格式'] = error_types.get('编码格式', 0) + 1
                elif '外键' in error:
                    error_types['外键引用'] = error_types.get('外键引用', 0) + 1
                else:
                    error_types['其他'] = error_types.get('其他', 0) + 1
        
        return {
            'table_name': table_name,
            'total_count': len(rows),
            'success_count': success_count,
            'error_count': error_count,
            'error_types': error_types,
            'error_details': all_errors
        }

    def validate_dkbm_format(self, dkbm: str) -> Optional[str]:
        """
        校验地块编码格式
        
        Args:
            dkbm: 地块编码
            
        Returns:
            错误消息或None
        """
        if not dkbm:
            return "地块编码不能为空"
        
        dkbm_str = str(dkbm).strip()
        
        # 检查长度
        if len(dkbm_str) != 19:
            return f"地块编码长度应为19位，实际为{len(dkbm_str)}位"
        
        # 检查是否为数字
        if not dkbm_str.isdigit():
            return "地块编码应为纯数字"
        
        return None

    def validate_cbfbm_format(self, cbfbm: str) -> Optional[str]:
        """
        校验承包方编码格式
        
        Args:
            cbfbm: 承包方编码
            
        Returns:
            错误消息或None
        """
        if not cbfbm:
            return "承包方编码不能为空"
        
        cbfbm_str = str(cbfbm).strip()
        
        # 检查长度
        if len(cbfbm_str) != 18:
            return f"承包方编码长度应为18位，实际为{len(cbfbm_str)}位"
        
        # 检查是否为数字
        if not cbfbm_str.isdigit():
            return "承包方编码应为纯数字"
        
        return None

    def validate_fbfbm_format(self, fbfbm: str) -> Optional[str]:
        """
        校验发包方编码格式
        
        Args:
            fbfbm: 发包方编码
            
        Returns:
            错误消息或None
        """
        if not fbfbm:
            return "发包方编码不能为空"
        
        fbfbm_str = str(fbfbm).strip()
        
        # 检查长度
        if len(fbfbm_str) != 14:
            return f"发包方编码长度应为14位，实际为{len(fbfbm_str)}位"
        
        # 检查是否为数字
        if not fbfbm_str.isdigit():
            return "发包方编码应为纯数字"
        
        return None