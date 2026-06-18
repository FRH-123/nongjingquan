"""
行政区划 API 路由 (AdminDivisionAPI)
提供行政区划查询相关的 REST API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminDivision
from app.schemas.indicator_schema import AdminDivisionNode, AdminDivisionTreeResponse


router = APIRouter(prefix="/admin-divisions", tags=["admin-divisions"])


@router.get("/tree", response_model=AdminDivisionTreeResponse)
async def get_admin_division_tree(
    db: Session = Depends(get_db),
):
    """
    获取行政区划树
    
    返回完整的行政区划树结构（县→镇→村→组）
    
    Args:
        db: 数据库会话
        
    Returns:
        AdminDivisionTreeResponse: 行政区划树
    """
    # 获取所有行政区划
    divisions = db.query(AdminDivision).order_by(
        AdminDivision.level, AdminDivision.code
    ).all()
    
    # 构建树结构
    nodes_map = {}
    root_nodes = []
    
    # 先创建所有节点
    for div in divisions:
        node = AdminDivisionNode(
            code=div.code,
            name=div.name,
            level=div.level,
            parent_code=div.parent_code,
            children=[],
        )
        nodes_map[div.code] = node
    
    # 构建父子关系
    for div in divisions:
        node = nodes_map[div.code]
        if div.parent_code and div.parent_code in nodes_map:
            nodes_map[div.parent_code].children.append(node)
        else:
            root_nodes.append(node)
    
    return AdminDivisionTreeResponse(
        nodes=root_nodes,
        total_count=len(divisions),
    )


@router.get("/list")
async def get_admin_division_list(
    level: Optional[int] = Query(None, description="层级筛选（1-6）"),
    parent_code: Optional[str] = Query(None, description="父级编码筛选"),
    db: Session = Depends(get_db),
):
    """
    获取行政区划列表（平铺）
    
    Args:
        level: 层级筛选（可选）
        parent_code: 父级编码筛选（可选）
        db: 数据库会话
        
    Returns:
        行政区划列表
    """
    query = db.query(AdminDivision)
    
    if level:
        query = query.filter(AdminDivision.level == level)
    
    if parent_code:
        query = query.filter(AdminDivision.parent_code == parent_code)
    
    divisions = query.order_by(AdminDivision.code).all()
    
    return {
        "items": [
            {
                "code": div.code,
                "name": div.name,
                "level": div.level,
                "parent_code": div.parent_code,
            }
            for div in divisions
        ],
        "total": len(divisions),
    }


@router.get("/{code}")
async def get_admin_division(
    code: str,
    db: Session = Depends(get_db),
):
    """
    获取单个行政区划详情
    
    Args:
        code: 行政区划编码
        db: 数据库会话
        
    Returns:
        行政区划详情
    """
    division = db.query(AdminDivision).filter(
        AdminDivision.code == code
    ).first()
    
    if not division:
        return {"error": "行政区划不存在", "code": code}
    
    # 获取子级列表
    children = db.query(AdminDivision).filter(
        AdminDivision.parent_code == code
    ).all()
    
    return {
        "code": division.code,
        "name": division.name,
        "level": division.level,
        "parent_code": division.parent_code,
        "children": [
            {
                "code": child.code,
                "name": child.name,
                "level": child.level,
            }
            for child in children
        ],
    }