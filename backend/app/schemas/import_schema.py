"""
Pydantic schemas for import-related API requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from app.models.import_task import ImportStatus


class ImportTaskCreate(BaseModel):
    """Schema for creating an import task."""
    filename: str = Field(..., description="上传的文件名")


class ImportErrorResponse(BaseModel):
    """Schema for import error response."""
    id: int = Field(..., description="错误记录ID")
    task_id: int = Field(..., description="导入任务ID")
    table_name: str = Field(..., description="表名")
    code: Optional[str] = Field(None, description="记录编码")
    row_number: Optional[int] = Field(None, description="行号")
    error_message: str = Field(..., description="错误信息")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class ImportTaskResponse(BaseModel):
    """Schema for import task response."""
    id: int = Field(..., description="任务ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="任务状态")
    total_count: int = Field(default=0, description="总记录数")
    success_count: int = Field(default=0, description="成功记录数")
    error_count: int = Field(default=0, description="错误记录数")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ImportTaskListResponse(BaseModel):
    """Schema for import task list response."""
    tasks: List[ImportTaskResponse] = Field(..., description="任务列表")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=10, description="每页数量")


class ImportStatusResponse(BaseModel):
    """Schema for import status response."""
    task_id: int = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="进度百分比 (0-100)")
    message: str = Field(..., description="状态消息")
    total_count: int = Field(default=0, description="总记录数")
    success_count: int = Field(default=0, description="成功记录数")
    error_count: int = Field(default=0, description="错误记录数")
    errors: List[ImportErrorResponse] = Field(default=[], description="错误列表")


class ImportErrorListResponse(BaseModel):
    """Schema for import error list response."""
    errors: List[ImportErrorResponse] = Field(..., description="错误列表")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页数量")


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    task_id: int = Field(..., description="任务ID")
    filename: str = Field(..., description="文件名")
    message: str = Field(..., description="上传消息")


class ValidationResult(BaseModel):
    """Schema for validation result."""
    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default=[], description="错误列表")


class ParsedFileInfo(BaseModel):
    """Schema for parsed file info from ZIP."""
    mdb_files: List[str] = Field(default=[], description="MDB文件列表")
    shp_files: List[str] = Field(default=[], description="Shapefile主文件列表")
    xls_files: List[str] = Field(default=[], description="XLS文件列表")
    extract_path: str = Field(..., description="解压路径")