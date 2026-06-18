# Tasks

## Phase 1: 基础框架搭建

- [x] Task 1: 项目初始化 & 基础框架搭建
  - [x] SubTask 1.1: 初始化 Next.js 项目，配置 Tailwind CSS 4
  - [x] SubTask 1.2: 实现 CSS 变量配置（从 ui-design-spec.md 复制）
  - [x] SubTask 1.3: 实现大屏布局骨架（顶部标题栏 + 指标卡行 + 三栏布局）
  - [x] SubTask 1.4: 实现顶部标题栏组件（渐变标题 + 日期 + 装饰线）
  - [x] SubTask 1.5: 实现指标卡组件（5 个占位卡）
  - [x] SubTask 1.6: 实现通用面板组件（Panel）

## Phase 2: 后端基础架构

- [x] Task 2: 数据库建模 & 后端 API 骨架
  - [x] SubTask 2.1: 创建 FastAPI 项目骨架（main.py、config.py、database.py）
  - [x] SubTask 2.2: 定义 SQLAlchemy ORM 模型（fbf、cbf、cbf_jtcy、cbht、cbdkxx、land_parcel_geom）
  - [x] SubTask 2.3: 定义字典表和系统表模型（dict_item、admin_division、import_task、import_error、indicator_snapshot）
  - [x] SubTask 2.4: 配置 Alembic 数据库迁移
  - [x] SubTask 2.5: 实现健康检查接口 `/api/health`
  - [x] SubTask 2.6: 配置 CORS 中间件

## Phase 3: 数据导入功能

- [x] Task 3: 数据包导入功能
  - [x] SubTask 3.1: 实现文件上传接口（接收 ZIP 文件）
  - [x] SubTask 3.2: 实现 ZIP 解压与文件识别服务
  - [x] SubTask 3.3: 实现 MDB 解析服务（读取 12 张业务表）
  - [x] SubTask 3.4: 实现 Shapefile 解析服务（geopandas + 坐标转换 EPSG:4527→4326）
  - [x] SubTask 3.5: 实现 XLS 代码表解析服务（构建行政区划树）
  - [x] SubTask 3.6: 实现数据校验服务（编码格式、必填字段、外键完整性）
  - [x] SubTask 3.7: 实现导入编排服务（串联上述步骤）
  - [x] SubTask 3.8: 实现导入任务状态追踪和错误记录

## Phase 4: 指标聚合与 API

- [x] Task 4: 指标聚合计算 & API 接口
  - [x] SubTask 4.1: 实现指标聚合服务（全局指标计算）
  - [x] SubTask 4.2: 实现用途统计聚合（种植业/林业/畜牧业/渔业）
  - [x] SubTask 4.3: 实现摸底填报统计聚合（按村组分组）
  - [x] SubTask 4.4: 实现填报分类统计聚合（饼图数据）
  - [x] SubTask 4.5: 实现审核列表查询（分页）
  - [x] SubTask 4.6: 实现 Redis 缓存服务（内存缓存替代）
  - [x] SubTask 4.7: 实现指标快照保存
  - [x] SubTask 4.8: 实现指标查询 API 路由

## Phase 5: 大屏前端左栏与指标卡

- [x] Task 5: 大屏前端开发（左栏 + 指标卡）
  - [x] SubTask 5.1: 改造指标卡组件为动态数据（对接 `/api/indicators/overview`）
  - [x] SubTask 5.2: 实现指标卡行容器组件
  - [x] SubTask 5.3: 实现权属单位筛选面板（行政区划树下拉框）
  - [x] SubTask 5.4: 实现地块用途统计面板（4 个统计小卡片）
  - [x] SubTask 5.5: 实现摸底填报柱状图面板（ECharts 分组柱状图）
  - [x] SubTask 5.6: 实现前端 API 请求封装（统一 baseURL + 错误处理）
  - [x] SubTask 5.7: 实现指标数据 SWR hook
  - [x] SubTask 5.8: 实现筛选状态管理 hook

## Phase 6: 大屏前端中央地图与右栏

- [x] Task 6: 大屏前端开发（中央地图 + 右栏）
  - [x] SubTask 6.1: 实现天地图面板组件（使用 Leaflet + OpenStreetMap 作为降级方案）
  - [x] SubTask 6.2: 实现村组标记点渲染（脉冲动画）
  - [x] SubTask 6.3: 实现摸底填报饼图面板（ECharts 环形饼图）
  - [x] SubTask 6.4: 实现内业审核表格面板（分页表格）
  - [x] SubTask 6.5: 实现状态标签组件（待公示/村干部审核/未调查/待审核）
  - [x] SubTask 6.6: 实现类型标签组件
  - [x] SubTask 6.7: 实现分页控件组件
  - [x] SubTask 6.8: 实现审核列表分页 hook
  - [x] SubTask 6.9: 实现筛选联动（左侧选择村组后，地图定位、饼图和表格数据同步更新）

## Phase 7: 辅助页面

- [x] Task 7: 数据导入管理页 & 登录页
  - [x] SubTask 7.1: 实现数据导入管理页面（`/import`）
  - [x] SubTask 7.2: 实现文件拖拽上传组件（DropZone）
  - [x] SubTask 7.3: 实现导入历史表格组件
  - [x] SubTask 7.4: 实现导入进度组件
  - [x] SubTask 7.5: 实现错误详情弹窗组件
  - [x] SubTask 7.6: 实现登录页面（`/login`）
  - [x] SubTask 7.7: 实现登录表单组件
  - [x] SubTask 7.8: 实现路由守卫（middleware.ts）
  - [x] SubTask 7.9: 实现后端登录接口（临时硬编码校验）

## Phase 8: P1 增强功能

- [x] Task 8: P1 增强功能（村组下钻 + 趋势 + 质量看板）
  - [x] SubTask 8.1: 实现村组详情弹窗组件（点击地图标记触发）
  - [x] SubTask 8.2: 实现发证进度指标卡组件
  - [x] SubTask 8.3: 实现趋势折线图组件（基于 indicator_snapshot）
  - [x] SubTask 8.4: 实现数据质量看板页面（`/quality`）
  - [x] SubTask 8.5: 实现数据质量检测服务（空间重叠、面积异常、编码异常）
  - [x] SubTask 8.6: 实现历史趋势对比页面（`/trend`）
  - [x] SubTask 8.7: 实现快照对比服务
  - [x] SubTask 8.8: 实现版本对比差异表格

---

# Task Dependencies

- Task 2 depends on Task 1（后端需要前端项目结构确定）
- Task 3 depends on Task 2（数据导入需要数据库表结构）
- Task 4 depends on Task 3（指标聚合需要数据导入完成）
- Task 5 depends on Task 4（前端需要后端 API）
- Task 6 depends on Task 5（右栏组件需要左栏筛选联动）
- Task 7 depends on Task 6（辅助页面需要大屏完成）
- Task 8 depends on Task 7（P1 功能需要 P0 完成）

---

# Parallelizable Work

- Task 1 和 Task 2 可并行开发（前端和后端独立初始化）
- Task 5 和 Task 6 可部分并行（左栏和右栏组件独立开发，最后集成）
- SubTask 3.3、3.4、3.5 可并行（MDB、Shapefile、XLS 解析独立）