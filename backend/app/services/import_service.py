"""
导入编排服务
负责串联所有导入步骤，协调ZIP解压、MDB解析、Shapefile解析、XLS解析等
"""
import os
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session
from app.models import ImportTask, ImportError, ImportStatus
from app.services.unzip_service import UnzipService
from app.services.mdb_parser import MDBParserService
from app.services.shp_parser import ShapefileParserService
from app.services.xls_parser import XLSParserService
from app.services.validator import DataValidator
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


@dataclass
class ImportProgress:
    """导入进度"""
    stage: str  # 当前阶段
    stage_progress: float  # 当前阶段进度 (0-100)
    total_progress: float  # 总进度 (0-100)
    message: str  # 进度消息
    current_count: int  # 当前处理数量
    total_count: int  # 总数量


class ImportService:
    """导入编排服务"""

    # 导入阶段
    STAGES = [
        ('extract', 'ZIP解压', 5),
        ('identify', '文件识别', 5),
        ('mdb_fbf', '发包方数据导入', 15),
        ('mdb_cbf', '承包方数据导入', 15),
        ('mdb_cbf_jtcy', '家庭成员数据导入', 10),
        ('mdb_cbht', '合同数据导入', 10),
        ('mdb_cbdkxx', '地块数据导入', 20),
        ('shp', 'Shapefile解析', 10),
        ('xls', '行政区划导入', 5),
        ('finalize', '导入完成', 5),
    ]

    def __init__(
        self,
        unzip_service: Optional[UnzipService] = None,
        mdb_parser: Optional[MDBParserService] = None,
        shp_parser: Optional[ShapefileParserService] = None,
        xls_parser: Optional[XLSParserService] = None,
        validator: Optional[DataValidator] = None
    ):
        """
        初始化导入编排服务
        
        Args:
            unzip_service: ZIP解压服务
            mdb_parser: MDB解析服务
            shp_parser: Shapefile解析服务
            xls_parser: XLS解析服务
            validator: 数据校验服务
        """
        self.unzip_service = unzip_service or UnzipService()
        self.mdb_parser = mdb_parser or MDBParserService()
        self.shp_parser = shp_parser or ShapefileParserService()
        self.xls_parser = xls_parser or XLSParserService()
        self.validator = validator or DataValidator()
        
        # 进度状态
        self._current_stage = 0
        self._progress_callback: Optional[Callable[[ImportProgress], None]] = None

    def set_progress_callback(self, callback: Callable[[ImportProgress], None]) -> None:
        """
        设置进度回调函数
        
        Args:
            callback: 进度回调函数
        """
        self._progress_callback = callback

    def _update_progress(
        self,
        stage_name: str,
        stage_progress: float,
        message: str,
        current_count: int = 0,
        total_count: int = 0
    ) -> None:
        """
        更新进度
        
        Args:
            stage_name: 阶段名称
            stage_progress: 阶段进度
            message: 进度消息
            current_count: 当前处理数量
            total_count: 总数量
        """
        # 计算总进度
        total_progress = 0
        for i, (name, _, weight) in enumerate(self.STAGES):
            if i < self._current_stage:
                total_progress += weight
            elif i == self._current_stage:
                total_progress += weight * (stage_progress / 100)
        
        progress = ImportProgress(
            stage=stage_name,
            stage_progress=stage_progress,
            total_progress=total_progress,
            message=message,
            current_count=current_count,
            total_count=total_count
        )
        
        if self._progress_callback:
            self._progress_callback(progress)
        
        logger.info(f"导入进度: {stage_name} - {stage_progress:.1f}% - {message}")

    def create_task(self, db: Session, filename: str) -> ImportTask:
        """
        创建导入任务
        
        Args:
            db: 数据库会话
            filename: 文件名
            
        Returns:
            ImportTask: 导入任务对象
        """
        task = ImportTask(
            filename=filename,
            status=ImportStatus.PENDING.value,
            total_count=0,
            success_count=0,
            error_count=0
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"创建导入任务: id={task.id}, filename={filename}")
        return task

    def start_import(
        self,
        db: Session,
        task_id: int,
        zip_path: str
    ) -> Dict[str, Any]:
        """
        开始导入流程
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            zip_path: ZIP文件路径
            
        Returns:
            导入结果字典
        """
        # 获取任务
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if not task:
            raise ValueError(f"导入任务不存在: {task_id}")
        
        # 更新任务状态
        task.status = ImportStatus.PROCESSING.value
        task.started_at = datetime.now()
        db.commit()
        
        # 清空校验器缓存
        self.validator.clear_cache()
        
        # 结果汇总
        results = {
            'task_id': task_id,
            'filename': task.filename,
            'status': 'processing',
            'total_count': 0,
            'success_count': 0,
            'error_count': 0,
            'errors': [],
            'details': {}
        }
        
        try:
            # 阶段1: ZIP解压
            self._current_stage = 0
            self._update_progress('extract', 0, '开始解压ZIP文件')
            
            extract_dir, extracted_files = self.unzip_service.extract_zip(zip_path, task_id)
            
            self._update_progress('extract', 100, f'解压完成，共{len(extracted_files)}个文件')
            
            # 阶段2: 文件识别
            self._current_stage = 1
            self._update_progress('identify', 0, '识别文件类型')
            
            file_info = self.unzip_service.identify_files(extract_dir)
            
            self._update_progress('identify', 100, 
                f'发现MDB:{len(file_info.mdb_files)}, SHP:{len(file_info.shp_files)}, XLS:{len(file_info.xls_files)}')
            
            results['details']['files'] = {
                'mdb_files': file_info.mdb_files,
                'shp_files': file_info.shp_files,
                'xls_files': file_info.xls_files,
            }
            
            # 阶段3-7: MDB解析（按顺序处理各表）
            mdb_results = []
            mdb_errors = []
            
            if file_info.mdb_files:
                mdb_path = file_info.mdb_files[0]  # 使用第一个MDB文件
                
                def mdb_progress_callback(table_name, current, total):
                    stage_map = {
                        'FBF': 2,
                        'CBF': 3,
                        'CBF_JTCY': 4,
                        'CBHT': 5,
                        'CBDKXX': 6,
                    }
                    self._current_stage = stage_map.get(table_name, 2)
                    progress = (current / total) * 100
                    self._update_progress(
                        f'mdb_{table_name.lower()}',
                        progress,
                        f'导入{table_name}表: {current}/{total}',
                        current,
                        total
                    )
                
                mdb_results, mdb_errors = self.mdb_parser.parse_all_tables(
                    mdb_path, db, task_id, mdb_progress_callback
                )
                
                # 更新编码缓存
                for result in mdb_results:
                    if result.table_name == 'FBF':
                        codes = [r.get('fbfbm') for r in mdb_results if r.table_name == 'FBF']
                        self.validator.update_cache('FBF', codes)
                    elif result.table_name == 'CBF':
                        codes = [r.get('cbfbm') for r in mdb_results if r.table_name == 'CBF']
                        self.validator.update_cache('CBF', codes)
                    elif result.table_name == 'CBHT':
                        codes = [r.get('cbhtbm') for r in mdb_results if r.table_name == 'CBHT']
                        self.validator.update_cache('CBHT', codes)
                
                # 汇总MDB结果
                for result in mdb_results:
                    results['total_count'] += result.total_count
                    results['success_count'] += result.success_count
                    results['error_count'] += result.error_count
                    results['details'][result.table_name] = {
                        'total': result.total_count,
                        'success': result.success_count,
                        'error': result.error_count,
                    }
                
                # 写入错误记录
                for error in mdb_errors:
                    db.add(error)
                db.commit()
            
            # 阶段8: Shapefile解析
            self._current_stage = 7
            shp_errors = []
            
            if file_info.shp_files:
                shp_path = file_info.shp_files[0]  # 使用第一个Shapefile
                
                def shp_progress_callback(current, total):
                    progress = (current / total) * 100
                    self._update_progress(
                        'shp',
                        progress,
                        f'解析Shapefile: {current}/{total}',
                        current,
                        total
                    )
                
                shp_result = self.shp_parser.parse_shapefile(
                    shp_path, db, task_id, shp_progress_callback
                )
                
                results['total_count'] += shp_result.total_count
                results['success_count'] += shp_result.success_count
                results['error_count'] += shp_result.error_count
                results['details']['land_parcel_geom'] = {
                    'total': shp_result.total_count,
                    'success': shp_result.success_count,
                    'error': shp_result.error_count,
                }
                
                # 写入错误记录
                shp_errors = self.shp_parser.create_import_errors(shp_result, task_id)
                for error in shp_errors:
                    db.add(error)
                db.commit()
            
            # 阶段9: XLS解析（行政区划）
            self._current_stage = 8
            xls_errors = []
            
            if file_info.xls_files:
                # 寻找权属单位代码表
                qsdw_xls = None
                for xls_path in file_info.xls_files:
                    if '权属单位' in xls_path or 'QSDW' in xls_path.upper():
                        qsdw_xls = xls_path
                        break
                
                if qsdw_xls:
                    def xls_progress_callback(current, total):
                        progress = (current / total) * 100
                        self._update_progress(
                            'xls',
                            progress,
                            f'导入行政区划: {current}/{total}',
                            current,
                            total
                        )
                    
                    xls_result = self.xls_parser.parse_admin_division(
                        qsdw_xls, db, task_id, xls_progress_callback
                    )
                    
                    results['total_count'] += xls_result.total_count
                    results['success_count'] += xls_result.success_count
                    results['error_count'] += xls_result.error_count
                    results['details']['admin_division'] = {
                        'total': xls_result.total_count,
                        'success': xls_result.success_count,
                        'error': xls_result.error_count,
                    }
                    
                    # 写入错误记录
                    xls_errors = self.xls_parser.create_import_errors(xls_result, task_id)
                    for error in xls_errors:
                        db.add(error)
                    db.commit()
            
            # 阶段10: 导入完成
            self._current_stage = 9
            self._update_progress('finalize', 0, '正在完成导入')
            
            # 更新任务状态
            task.status = ImportStatus.COMPLETED.value
            task.completed_at = datetime.now()
            task.total_count = results['total_count']
            task.success_count = results['success_count']
            task.error_count = results['error_count']
            db.commit()
            
            # 刷新指标缓存
            self._update_progress('finalize', 50, '刷新指标缓存')
            cache_service.refresh_cache()
            logger.info("指标缓存已刷新")
            
            # 保存指标快照
            self._update_progress('finalize', 75, '保存指标快照')
            self._save_indicator_snapshot(db)
            logger.info("指标快照已保存")
            
            self._update_progress('finalize', 100, 
                f'导入完成: 成功{results["success_count"]}条, 失败{results["error_count"]}条')
            
            results['status'] = 'completed'
            
            # 清理临时文件
            self.unzip_service.cleanup(task_id)
            
            logger.info(f"导入任务完成: task_id={task_id}, "
                       f"total={results['total_count']}, "
                       f"success={results['success_count']}, "
                       f"error={results['error_count']}")
            
            return results
            
        except Exception as e:
            # 导入失败
            logger.error(f"导入失败: {str(e)}")
            
            task.status = ImportStatus.FAILED.value
            task.completed_at = datetime.now()
            db.commit()
            
            # 记录错误
            import_error = ImportError(
                task_id=task_id,
                table_name='import_service',
                error_message=str(e)
            )
            db.add(import_error)
            db.commit()
            
            # 清理临时文件
            self.unzip_service.cleanup(task_id)
            
            results['status'] = 'failed'
            results['error_count'] += 1
            results['errors'].append({
                'table_name': 'import_service',
                'error_message': str(e)
            })
            
            return results

    def get_task_status(self, db: Session, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Returns:
            任务状态字典
        """
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if not task:
            return None
        
        # 获取错误记录
        errors = db.query(ImportError).filter(
            ImportError.task_id == task_id
        ).order_by(ImportError.created_at.desc()).limit(20).all()
        
        return {
            'task_id': task.id,
            'filename': task.filename,
            'status': task.status,
            'total_count': task.total_count,
            'success_count': task.success_count,
            'error_count': task.error_count,
            'started_at': task.started_at,
            'completed_at': task.completed_at,
            'created_at': task.created_at,
            'errors': [
                {
                    'id': e.id,
                    'table_name': e.table_name,
                    'code': e.code,
                    'row_number': e.row_number,
                    'error_message': e.error_message,
                }
                for e in errors
            ]
        }

    def get_task_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取任务列表
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            
        Returns:
            任务列表字典
        """
        total = db.query(ImportTask).count()
        
        tasks = db.query(ImportTask).order_by(
            ImportTask.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            'tasks': [
                {
                    'id': t.id,
                    'filename': t.filename,
                    'status': t.status,
                    'total_count': t.total_count,
                    'success_count': t.success_count,
                    'error_count': t.error_count,
                    'started_at': t.started_at,
                    'completed_at': t.completed_at,
                    'created_at': t.created_at,
                }
                for t in tasks
            ],
            'total': total,
            'page': page,
            'page_size': page_size,
        }

    def get_task_errors(
        self,
        db: Session,
        task_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取任务错误列表
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            错误列表字典
        """
        total = db.query(ImportError).filter(
            ImportError.task_id == task_id
        ).count()
        
        errors = db.query(ImportError).filter(
            ImportError.task_id == task_id
        ).order_by(
            ImportError.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            'errors': [
                {
                    'id': e.id,
                    'task_id': e.task_id,
                    'table_name': e.table_name,
                    'code': e.code,
                    'row_number': e.row_number,
                    'error_message': e.error_message,
                    'created_at': e.created_at,
                }
                for e in errors
            ],
            'total': total,
            'page': page,
            'page_size': page_size,
        }

    def cancel_task(self, db: Session, task_id: int) -> bool:
        """
        取消导入任务
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if not task:
            return False
        
        if task.status == ImportStatus.COMPLETED.value:
            return False  # 已完成的任务不能取消
        
        task.status = ImportStatus.FAILED.value
        task.completed_at = datetime.now()
        db.commit()
        
        # 清理临时文件
        self.unzip_service.cleanup(task_id)
        
        logger.info(f"取消导入任务: task_id={task_id}")
        return True

    def delete_task(self, db: Session, task_id: int) -> bool:
        """
        删除导入任务及相关错误记录
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Returns:
            是否成功删除
        """
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if not task:
            return False
        
        # 删除错误记录
        db.query(ImportError).filter(ImportError.task_id == task_id).delete()
        
        # 删除任务
        db.delete(task)
        db.commit()
        
        logger.info(f"删除导入任务: task_id={task_id}")
        return True
    
    def _save_indicator_snapshot(self, db: Session) -> bool:
        """
        保存指标快照
        
        Args:
            db: 数据库会话
            
        Returns:
            是否成功
        """
        try:
            from app.services.indicator_service import IndicatorService
            from app.models import IndicatorSnapshot, AdminDivision
            import json
            
            indicator_service = IndicatorService(db)
            snapshot_date = date.today()
            
            # 获取所有行政区划
            divisions = db.query(AdminDivision).all()
            
            # 保存各行政区划的快照
            for div in divisions:
                overview = indicator_service.get_overview(div.code)
                snapshot = IndicatorSnapshot(
                    snapshot_date=snapshot_date,
                    level=self._get_level_name(div.level),
                    code=div.code,
                    metrics_json=json.dumps(overview.model_dump(), ensure_ascii=False),
                )
                db.add(snapshot)
            
            # 保存全局快照
            global_overview = indicator_service.get_overview()
            global_snapshot = IndicatorSnapshot(
                snapshot_date=snapshot_date,
                level="global",
                code="",
                metrics_json=json.dumps(global_overview.model_dump(), ensure_ascii=False),
            )
            db.add(global_snapshot)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存快照失败: {e}")
            db.rollback()
            return False
    
    def _get_level_name(self, level: int) -> str:
        """
        获取层级名称
        
        Args:
            level: 层级数字
            
        Returns:
            层级名称
        """
        level_names = {
            1: "province",
            2: "city",
            3: "county",
            4: "town",
            5: "village",
            6: "group",
        }
        return level_names.get(level, "unknown")