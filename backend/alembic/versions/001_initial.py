"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create fbf table (发包方)
    op.create_table(
        'fbf',
        sa.Column('fbfbm', sa.String(14), primary_key=True, comment='发包方编码'),
        sa.Column('fbfmc', sa.String(100), nullable=True, comment='发包方名称'),
        sa.Column('fbffzrxm', sa.String(50), nullable=True, comment='发包方负责人姓名'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )

    # Create cbf table (承包方)
    op.create_table(
        'cbf',
        sa.Column('cbfbm', sa.String(18), primary_key=True, comment='承包方编码'),
        sa.Column('cbfmc', sa.String(100), nullable=True, comment='承包方名称'),
        sa.Column('cbfzjlx', sa.String(10), nullable=True, comment='承包方证件类型'),
        sa.Column('cbfzjhm', sa.String(30), nullable=True, comment='承包方证件号码'),
        sa.Column('cbfcysl', sa.Integer, nullable=True, comment='承包方成员数量'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )

    # Create cbf_jtcy table (家庭成员)
    op.create_table(
        'cbf_jtcy',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('cbfbm', sa.String(18), sa.ForeignKey('cbf.cbfbm'), nullable=False, comment='承包方编码'),
        sa.Column('cyxm', sa.String(50), nullable=True, comment='成员姓名'),
        sa.Column('yhzgx', sa.String(20), nullable=True, comment='与户主关系'),
        sa.Column('sfzhm', sa.String(30), nullable=True, comment='身份证号码'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_cbf_jtcy_cbfbm', 'cbf_jtcy', ['cbfbm'])

    # Create cbht table (承包合同)
    op.create_table(
        'cbht',
        sa.Column('cbhtbm', sa.String(19), primary_key=True, comment='承包合同编码'),
        sa.Column('fbfbm', sa.String(14), sa.ForeignKey('fbf.fbfbm'), nullable=True, comment='发包方编码'),
        sa.Column('cbfbm', sa.String(18), sa.ForeignKey('cbf.cbfbm'), nullable=True, comment='承包方编码'),
        sa.Column('cbfs', sa.String(20), nullable=True, comment='承包方式'),
        sa.Column('cbqxq', sa.Date, nullable=True, comment='承包期限起'),
        sa.Column('cbqxz', sa.Date, nullable=True, comment='承包期限止'),
        sa.Column('htmjm', sa.Numeric(12, 2), nullable=True, comment='合同总面积（亩）'),
        sa.Column('cbdkzs', sa.Integer, nullable=True, comment='承包地块总数'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_cbht_fbfbm', 'cbht', ['fbfbm'])
    op.create_index('ix_cbht_cbfbm', 'cbht', ['cbfbm'])

    # Create cbdkxx table (承包地块信息)
    op.create_table(
        'cbdkxx',
        sa.Column('id', sa.String(20), primary_key=True, comment='主键ID'),
        sa.Column('cbfbm', sa.String(18), sa.ForeignKey('cbf.cbfbm'), nullable=True, comment='承包方编码'),
        sa.Column('cbhtbm', sa.String(19), sa.ForeignKey('cbht.cbhtbm'), nullable=True, comment='承包合同编码'),
        sa.Column('dkbm', sa.String(19), nullable=True, comment='地块编码'),
        sa.Column('cbjyqzbm', sa.String(19), nullable=True, comment='承包经营权证编码'),
        sa.Column('htmjm', sa.Numeric(12, 2), nullable=True, comment='合同面积（亩）'),
        sa.Column('scmjm', sa.Numeric(12, 2), nullable=True, comment='实测面积（亩）'),
        sa.Column('dkmc', sa.String(100), nullable=True, comment='地块名称'),
        sa.Column('syqxz', sa.String(10), nullable=True, comment='所有权性质'),
        sa.Column('dklb', sa.String(10), nullable=True, comment='地块类别'),
        sa.Column('tdyt', sa.String(10), nullable=True, comment='土地用途'),
        sa.Column('dldj', sa.String(10), nullable=True, comment='地块等级'),
        sa.Column('dkdz', sa.String(200), nullable=True, comment='地块地址'),
        sa.Column('dkxz', sa.String(200), nullable=True, comment='地块坐落'),
        sa.Column('dkbz', sa.String(500), nullable=True, comment='地块备注'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_cbdkxx_cbfbm', 'cbdkxx', ['cbfbm'])
    op.create_index('ix_cbdkxx_cbhtbm', 'cbdkxx', ['cbhtbm'])
    op.create_index('ix_cbdkxx_dkbm', 'cbdkxx', ['dkbm'])

    # Create land_parcel_geom table (地块空间几何)
    op.create_table(
        'land_parcel_geom',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('dkbm', sa.String(19), sa.ForeignKey('cbdkxx.dkbm'), nullable=True, unique=True, comment='地块编码'),
        sa.Column('geom_wkt', sa.String, nullable=True, comment='地块几何 WKT 格式'),
        sa.Column('geom_type', sa.String(20), nullable=True, default='POLYGON', comment='几何类型'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_land_parcel_geom_dkbm', 'land_parcel_geom', ['dkbm'])

    # Create dict_item table (字典项)
    op.create_table(
        'dict_item',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('category', sa.String(50), nullable=False, comment='字典类别'),
        sa.Column('code', sa.String(20), nullable=False, comment='编码'),
        sa.Column('name', sa.String(100), nullable=False, comment='名称'),
        sa.Column('sort_order', sa.Integer, nullable=True, default=0, comment='排序号'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_dict_item_category', 'dict_item', ['category'])

    # Create admin_division table (行政区划)
    op.create_table(
        'admin_division',
        sa.Column('code', sa.String(14), primary_key=True, comment='行政区划编码'),
        sa.Column('name', sa.String(100), nullable=False, comment='行政区划名称'),
        sa.Column('parent_code', sa.String(14), nullable=True, comment='上级行政区划编码'),
        sa.Column('level', sa.Integer, nullable=False, comment='层级'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )
    op.create_index('ix_admin_division_parent_code', 'admin_division', ['parent_code'])

    # Create import_task table (导入任务)
    op.create_table(
        'import_task',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('filename', sa.String(255), nullable=False, comment='导入文件名'),
        sa.Column('status', sa.String(20), nullable=False, default='pending', comment='任务状态'),
        sa.Column('total_count', sa.Integer, nullable=True, default=0, comment='总记录数'),
        sa.Column('success_count', sa.Integer, nullable=True, default=0, comment='成功记录数'),
        sa.Column('error_count', sa.Integer, nullable=True, default=0, comment='错误记录数'),
        sa.Column('started_at', sa.DateTime, nullable=True, comment='开始时间'),
        sa.Column('completed_at', sa.DateTime, nullable=True, comment='完成时间'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, server_default=func.now(), comment='更新时间'),
    )

    # Create import_error table (导入错误)
    op.create_table(
        'import_error',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('import_task.id'), nullable=False, comment='导入任务ID'),
        sa.Column('table_name', sa.String(50), nullable=False, comment='表名'),
        sa.Column('code', sa.String(50), nullable=True, comment='记录编码'),
        sa.Column('row_number', sa.Integer, nullable=True, comment='行号'),
        sa.Column('error_message', sa.Text, nullable=False, comment='错误信息'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
    )
    op.create_index('ix_import_error_task_id', 'import_error', ['task_id'])

    # Create indicator_snapshot table (指标快照)
    op.create_table(
        'indicator_snapshot',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='主键ID'),
        sa.Column('snapshot_date', sa.Date, nullable=False, comment='快照日期'),
        sa.Column('level', sa.String(20), nullable=False, comment='层级'),
        sa.Column('code', sa.String(14), nullable=False, comment='行政区划编码'),
        sa.Column('metrics_json', sa.Text, nullable=False, comment='指标数据 JSON'),
        sa.Column('created_at', sa.DateTime, server_default=func.now(), comment='创建时间'),
    )
    op.create_index('ix_indicator_snapshot_snapshot_date', 'indicator_snapshot', ['snapshot_date'])
    op.create_index('ix_indicator_snapshot_code', 'indicator_snapshot', ['code'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('indicator_snapshot')
    op.drop_table('import_error')
    op.drop_table('import_task')
    op.drop_table('admin_division')
    op.drop_table('dict_item')
    op.drop_table('land_parcel_geom')
    op.drop_table('cbdkxx')
    op.drop_table('cbht')
    op.drop_table('cbf_jtcy')
    op.drop_table('cbf')
    op.drop_table('fbf')