"""
导入任务模型 (ImportTask)
用于追踪数据包导入任务的状态
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class ImportStatus(str, enum.Enum):
    """导入任务状态枚举"""
    PENDING = "pending"      # 等待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


class ImportTask(Base):
    """
    导入任务表
    记录每次数据包导入的状态和统计信息
    """
    __tablename__ = "import_task"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 文件名
    filename = Column(String(255), nullable=False, comment="导入文件名")
    # 任务状态
    status = Column(
        String(20), 
        nullable=False, 
        default=ImportStatus.PENDING.value,
        comment="任务状态"
    )
    # 总记录数
    total_count = Column(Integer, nullable=True, default=0, comment="总记录数")
    # 成功记录数
    success_count = Column(Integer, nullable=True, default=0, comment="成功记录数")
    # 错误记录数
    error_count = Column(Integer, nullable=True, default=0, comment="错误记录数")
    # 开始时间
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    # 完成时间
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ImportTask(id={self.id}, filename='{self.filename}', status='{self.status}')>"