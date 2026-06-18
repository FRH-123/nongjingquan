"""
导入错误模型 (ImportError)
用于记录数据导入过程中的错误信息
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ImportError(Base):
    """
    导入错误表
    记录数据导入过程中的校验失败记录
    """
    __tablename__ = "import_error"

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    # 关联的导入任务ID
    task_id = Column(Integer, ForeignKey("import_task.id"), nullable=False, index=True, comment="导入任务ID")
    # 表名
    table_name = Column(String(50), nullable=False, comment="表名")
    # 记录编码
    code = Column(String(50), nullable=True, comment="记录编码")
    # 行号
    row_number = Column(Integer, nullable=True, comment="行号")
    # 错误信息
    error_message = Column(Text, nullable=False, comment="错误信息")
    # 创建时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    task = relationship("ImportTask", backref="errors")

    def __repr__(self):
        return f"<ImportError(id={self.id}, table_name='{self.table_name}', code='{self.code}')>"