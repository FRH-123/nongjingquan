# Checklist

## Phase 1: 项目初始化

- [x] `pnpm dev` 启动无报错，访问 localhost:5000 可看到深色背景大屏骨架
- [x] 顶部标题栏显示渐变标题 + 日期 + 装饰线，与 Demo 一致
- [x] 5 个指标卡占位可见，样式与 Demo 一致
- [x] 三栏布局比例正确（左 280px / 中弹性 / 右 300px）
- [x] CSS 变量完整覆盖 UI 规范速查表所有变量

## Phase 2: 后端基础

- [x] `alembic upgrade head` 成功创建所有表
- [x] `uvicorn backend.app.main:app` 启动无报错
- [x] `GET /api/health` 返回 `{"status": "ok", "db": "connected"}`
- [x] 所有模型字段与概要设计文档中的表结构一致
- [x] GeoAlchemy2 的 Geometry 列类型正确配置（SRID=4326）

## Phase 3: 数据导入

- [x] 上传 ZIP 文件后，数据正确入库（fbf/cbf/cbdkxx 表）
- [x] `land_parcel_geom` 表中几何数据支持 WKT 格式存储
- [x] `admin_division` 表构建行政区划树结构
- [x] `dict_item` 表包含字典编码映射
- [x] 导入错误记录写入 `import_error` 表
- [x] `GET /api/import/tasks` 返回导入任务列表及状态

## Phase 4: 指标聚合

- [x] `GET /api/indicators/overview` 返回 5 个核心指标
- [x] `GET /api/indicators/overview?village_code=xxx` 返回指定村的指标
- [x] `GET /api/indicators/land-usage` 返回用途统计数据
- [x] `GET /api/indicators/survey-stats` 返回按村组分组的已上报/已审核户数
- [x] `GET /api/indicators/survey-categories` 返回饼图分类占比数据
- [x] `GET /api/audit/list?page=1&size=10` 返回审核表格分页数据
- [x] 缓存服务实现（内存缓存替代 Redis）
- [x] 导入新数据后缓存自动刷新

## Phase 5: 大屏左栏

- [x] 5 个指标卡显示从后端 API 获取的真实数值
- [x] 筛选框可选村→组，选择后指标卡和柱状图数据联动更新
- [x] 用途统计 4 卡显示地块分类数量
- [x] 柱状图正确渲染分组数据，蓝/金双色与 Demo 一致
- [x] 数据加载中显示 skeleton 动画，加载失败显示错误提示

## Phase 6: 大屏中央与右栏

- [x] 地图可正常加载，显示行政区划底图 + 村组标记点（脉冲动画）
- [x] 饼图正确渲染 5 分类环形图，分页切换正常
- [x] 审核表格显示真实数据，状态标签颜色正确
- [x] 分页控件可用，翻页后表格数据更新
- [x] 整体大屏视觉效果与静态 Demo 一致
- [x] 筛选联动：左侧选择村组后，地图定位到该区域、饼图和表格数据同步更新

## Phase 7: 辅助页面

- [x] 拖拽上传 ZIP 文件后，点击"开始导入"可触发后端导入流程
- [x] 导入历史表格显示历史导入记录，状态/成功数/失败数正确
- [x] 点击"详情"可查看导入错误记录
- [x] 登录页输入 admin/admin 可登录并跳转大屏
- [x] 未登录状态访问 `/dashboard` 自动跳转 `/login`
- [x] 登录后点击"返回大屏"可正常导航

## Phase 8: P1 增强功能

- [x] 点击地图村组标记，弹窗显示该村的 5 个指标 + 进度条
- [x] 发证指标卡显示真实计算值
- [x] 趋势折线图可按日/周切换
- [x] 数据质量看板显示空间重叠/面积异常/编码异常的数量
- [x] 版本对比页可选择两次导入，差异表格正确显示变化量和百分比