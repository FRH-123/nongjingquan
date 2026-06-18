"""
导入相关API路由
包括文件上传、状态查询、错误查询等接口
"""
import os
import logging
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImportTask, ImportError, ImportStatus
from app.schemas.import_schema import (
    ImportTaskResponse,
    ImportTaskListResponse,
    ImportErrorResponse,
    ImportErrorListResponse,
    ImportStatusResponse,
    FileUploadResponse,
)
from app.services.import_service import ImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["import"])


# 创建导入服务实例
import_service = ImportService()


def save_upload_file(upload_file: UploadFile) -> str:
    """
    保存上传的文件到临时目录
    
    Args:
        upload_file: 上传的文件对象
        
    Returns:
        保存的文件路径
    """
    # 创建临时目录
    temp_dir = os.path.join(tempfile.gettempdir(), "land_rights_upload")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{upload_file.filename}"
    file_path = os.path.join(temp_dir, filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
    
    logger.info(f"保存上传文件: {file_path}, 大小: {len(content)} bytes")
    
    return file_path


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    上传ZIP数据包文件
    
    Args:
        file: 上传的ZIP文件
        background_tasks: 后台任务
        db: 数据库会话
        
    Returns:
        上传响应
    """
    # 验证文件类型
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持ZIP文件格式")
    
    # 验证文件大小（最大100MB）
    max_size = 100 * 1024 * 1024  # 100MB
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 回到文件开头
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="文件大小超过100MB限制")
    
    # 保存上传文件
    try:
        zip_path = save_upload_file(file)
    except Exception as e:
        logger.error(f"保存文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    # 创建导入任务
    task = import_service.create_task(db, file.filename)
    
    # 在后台执行导入
    def run_import():
        # 创建新的数据库会话（后台任务需要独立的会话）
        from app.database import SessionLocal
        bg_db = SessionLocal()
        try:
            import_service.start_import(bg_db, task.id, zip_path)
        except Exception as e:
            logger.error(f"后台导入失败: {str(e)}")
        finally:
            bg_db.close()
    
    if background_tasks:
        background_tasks.add_task(run_import)
    
    return FileUploadResponse(
        task_id=task.id,
        filename=file.filename,
        message="文件上传成功，导入任务已创建"
    )


@router.post("/upload-sync")
async def upload_file_sync(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传ZIP数据包文件并同步导入（用于测试）
    
    Args:
        file: 上传的ZIP文件
        db: 数据库会话
        
    Returns:
        导入结果
    """
    # 验证文件类型
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持ZIP文件格式")
    
    # 保存上传文件
    try:
        zip_path = save_upload_file(file)
    except Exception as e:
        logger.error(f"保存文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    # 创建导入任务
    task = import_service.create_task(db, file.filename)
    
    # 同步执行导入
    result = import_service.start_import(db, task.id, zip_path)
    
    return result


@router.get("/tasks", response_model=ImportTaskListResponse)
async def get_import_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取导入任务列表
    
    Args:
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        
    Returns:
        任务列表响应
    """
    result = import_service.get_task_list(db, page, page_size)
    
    return ImportTaskListResponse(
        tasks=[
            ImportTaskResponse(
                id=t['id'],
                filename=t['filename'],
                status=t['status'],
                total_count=t['total_count'],
                success_count=t['success_count'],
                error_count=t['error_count'],
                started_at=t['started_at'],
                completed_at=t['completed_at'],
                created_at=t['created_at'],
                updated_at=t['created_at'],  # 使用created_at作为updated_at
            )
            for t in result['tasks']
        ],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
    )


@router.get("/tasks/{task_id}", response_model=ImportStatusResponse)
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    获取导入任务状态
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        
    Returns:
        任务状态响应
    """
    result = import_service.get_task_status(db, task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    
    # 计算进度
    progress = 0
    if result['status'] == ImportStatus.COMPLETED.value:
        progress = 100
    elif result['status'] == ImportStatus.PROCESSING.value:
        if result['total_count'] > 0:
            progress = (result['success_count'] + result['error_count']) / result['total_count'] * 100
    
    # 构建消息
    message = ""
    if result['status'] == ImportStatus.PENDING.value:
        message = "等待处理"
    elif result['status'] == ImportStatus.PROCESSING.value:
        message = f"正在处理: 成功{result['success_count']}条, 失败{result['error_count']}条"
    elif result['status'] == ImportStatus.COMPLETED.value:
        message = f"导入完成: 成功{result['success_count']}条, 失败{result['error_count']}条"
    elif result['status'] == ImportStatus.FAILED.value:
        message = "导入失败"
    
    return ImportStatusResponse(
        task_id=result['task_id'],
        status=result['status'],
        progress=progress,
        message=message,
        total_count=result['total_count'],
        success_count=result['success_count'],
        error_count=result['error_count'],
        errors=[
            ImportErrorResponse(
                id=e['id'],
                task_id=result['task_id'],
                table_name=e['table_name'],
                code=e['code'],
                row_number=e['row_number'],
                error_message=e['error_message'],
                created_at=datetime.now(),  # 使用当前时间
            )
            for e in result['errors']
        ]
    )


@router.get("/tasks/{task_id}/errors", response_model=ImportErrorListResponse)
async def get_task_errors(
    task_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取导入任务错误列表
    
    Args:
        task_id: 任务ID
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        
    Returns:
        错误列表响应
    """
    # 检查任务是否存在
    task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    
    result = import_service.get_task_errors(db, task_id, page, page_size)
    
    return ImportErrorListResponse(
        errors=[
            ImportErrorResponse(
                id=e['id'],
                task_id=e['task_id'],
                table_name=e['table_name'],
                code=e['code'],
                row_number=e['row_number'],
                error_message=e['error_message'],
                created_at=e['created_at'],
            )
            for e in result['errors']
        ],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    删除导入任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    success = import_service.delete_task(db, task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    
    return {"message": "任务已删除", "task_id": task_id}


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    取消导入任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        
    Returns:
        取消结果
    """
    success = import_service.cancel_task(db, task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="导入任务不存在或已完成")
    
    return {"message": "任务已取消", "task_id": task_id}


@router.get("/stats")
async def get_import_stats(
    db: Session = Depends(get_db)
):
    """
    获取导入统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        统计信息
    """
    # 总任务数
    total_tasks = db.query(ImportTask).count()
    
    # 各状态任务数
    pending_tasks = db.query(ImportTask).filter(
        ImportTask.status == ImportStatus.PENDING.value
    ).count()
    
    processing_tasks = db.query(ImportTask).filter(
        ImportTask.status == ImportStatus.PROCESSING.value
    ).count()
    
    completed_tasks = db.query(ImportTask).filter(
        ImportTask.status == ImportStatus.COMPLETED.value
    ).count()
    
    failed_tasks = db.query(ImportTask).filter(
        ImportTask.status == ImportStatus.FAILED.value
    ).count()
    
    # 总导入记录数
    total_records = db.query(ImportTask).with_entities(
        ImportTask.total_count
    ).filter(ImportTask.status == ImportStatus.COMPLETED.value).all()
    
    total_imported = sum(t[0] or 0 for t in total_records)
    
    # 总错误数
    total_errors = db.query(ImportError).count()
    
    return {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "processing_tasks": processing_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "total_imported_records": total_imported,
        "total_errors": total_errors,
    }