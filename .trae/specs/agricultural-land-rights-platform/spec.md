# 农经权二轮延包可视化平台 Spec

## Why
本项目是一个数据监控可视化大屏平台，用于接入内业数据处理软件输出的确权数据包，自动聚合统计各村组摸底调查、内业审核、合同签订、确权发证等关键进度指标，以大屏可视化方式一目了然地呈现项目整体推进情况。

## What Changes
- 建立前后端分离的全栈项目架构（Next.js + FastAPI）
- 实现数据包导入功能（ZIP → MDB/Shapefile/XLS 解析入库）
- 实现核心指标聚合计算与缓存
- 实现数据监控大屏可视化（地图、图表、表格）
- 实现数据导入管理页面与登录认证

## Impact
- Affected specs: 数据导入、指标聚合、大屏可视化、用户认证
- Affected code: 前端 Next.js 项目、后端 FastAPI 项目、PostgreSQL 数据库

---

## ADDED Requirements

### Requirement: 项目初始化与基础框架
系统 SHALL 提供基于 Next.js 的前端项目框架和基于 FastAPI 的后端项目框架。

#### Scenario: 前端项目初始化成功
- **WHEN** 执行 `pnpm dev` 启动前端开发服务器
- **THEN** 访问 localhost:5000 可看到深色背景大屏骨架
- **AND** 顶部标题栏显示渐变标题 + 日期 + 装饰线
- **AND** 5 个指标卡占位可见
- **AND** 三栏布局比例正确（左 280px / 中弹性 / 右 300px）

#### Scenario: 后端项目初始化成功
- **WHEN** 执行 `uvicorn backend.app.main:app` 启动后端服务
- **THEN** `GET /api/health` 返回 `{"status": "ok", "db": "connected"}`
- **AND** 所有数据库表通过 Alembic 迁移成功创建

---

### Requirement: 数据库建模
系统 SHALL 提供 PostgreSQL 数据库表结构，支持业务数据存储和空间数据存储。

#### Scenario: 数据库表创建成功
- **WHEN** 执行 `alembic upgrade head`
- **THEN** 所有核心业务表创建成功（fbf、cbf、cbf_jtcy、cbht、cbdkxx、land_parcel_geom）
- **AND** 编码/字典表创建成功（dict_item、admin_division）
- **AND** 系统表创建成功（import_task、import_error、indicator_snapshot）
- **AND** GeoAlchemy2 的 Geometry 列类型正确配置（SRID=4326）

---

### Requirement: 数据包导入功能
系统 SHALL 支持 ZIP 数据包上传、解压、解析 MDB/Shapefile/XLS 文件并入库。

#### Scenario: ZIP 数据包导入成功
- **WHEN** 用户上传 `370199测试县.zip` 数据包
- **THEN** `fbf` 表有 21 条记录
- **AND** `cbf` 表有 657 条记录
- **AND** `cbdkxx` 表有 2920 条记录
- **AND** `land_parcel_geom` 表中几何数据 SRID=4326
- **AND** `admin_division` 表构建出完整的行政区划树（县→镇→村→组层级）
- **AND** `dict_item` 表包含 SYQXZ/DKLB/TDLYLX/DLDJ 等字典映射

#### Scenario: 导入错误记录
- **WHEN** 导入过程中发现数据校验错误
- **THEN** 错误记录写入 `import_error` 表
- **AND** 包含表名、编码、错误原因

---

### Requirement: 指标聚合计算
系统 SHALL 支持核心指标的聚合计算，并提供 API 接口供前端调用。

#### Scenario: 全局指标查询成功
- **WHEN** 调用 `GET /api/indicators/overview`
- **THEN** 返回 5 个核心指标：发包方总数 21 / 承包方总数 657 / 已摸底 538 / 已审核 331 / 已完成 26

#### Scenario: 指标缓存生效
- **WHEN** 第二次请求相同指标
- **THEN** 响应时间 < 50ms（命中 Redis 缓存）

#### Scenario: 用途统计查询成功
- **WHEN** 调用 `GET /api/indicators/land-usage`
- **THEN** 返回种植业 3810 / 林业 47 / 畜牧业 20 / 渔业 12

---

### Requirement: 大屏前端可视化
系统 SHALL 提供数据监控大屏，展示核心指标、地图、图表和表格。

#### Scenario: 指标卡动态渲染
- **WHEN** 大屏加载完成
- **THEN** 5 个指标卡显示从后端 API 获取的真实数值
- **AND** 数据加载中显示 skeleton 动画

#### Scenario: 筛选联动
- **WHEN** 用户选择村组筛选
- **THEN** 指标卡和柱状图数据联动更新

#### Scenario: 天地图加载成功
- **WHEN** 大屏中央地图区域加载
- **THEN** 天地图正常显示行政区划底图
- **AND** 村组标记点显示脉冲动画

#### Scenario: 饼图渲染成功
- **WHEN** 右侧饼图区域加载
- **THEN** 饼图正确渲染 5 分类环形图
- **AND** 分页切换正常

#### Scenario: 审核表格渲染成功
- **WHEN** 右侧表格区域加载
- **THEN** 表格显示真实数据
- **AND** 状态标签颜色正确
- **AND** 分页控件可用

---

### Requirement: 数据导入管理页面
系统 SHALL 提供数据导入管理页面，支持 ZIP 文件上传和导入历史查看。

#### Scenario: 文件上传成功
- **WHEN** 用户拖拽上传 ZIP 文件并点击"开始导入"
- **THEN** 后端导入流程触发
- **AND** 导入进度显示

#### Scenario: 导入历史查看
- **WHEN** 用户查看导入历史表格
- **THEN** 显示导入时间、文件名、状态、成功数、失败数
- **AND** 点击"详情"可查看导入错误记录

---

### Requirement: 登录认证
系统 SHALL 提供登录页面和路由守卫。

#### Scenario: 登录成功
- **WHEN** 用户输入 admin/admin 登录
- **THEN** 跳转至 `/dashboard` 大屏页面

#### Scenario: 路由守卫生效
- **WHEN** 未登录状态访问 `/dashboard` 或 `/import`
- **THEN** 自动跳转 `/login`

---

### Requirement: P1 增强功能
系统 SHALL 提供村组下钻、趋势对比、数据质量看板等增强功能。

#### Scenario: 村组详情弹窗
- **WHEN** 用户点击地图村组标记
- **THEN** 弹窗显示该村的 5 个指标 + 进度条

#### Scenario: 数据质量看板
- **WHEN** 用户访问 `/quality` 页面
- **THEN** 显示空间重叠/面积异常/编码异常的数量

#### Scenario: 版本对比
- **WHEN** 用户选择两次导入进行对比
- **THEN** 差异表格正确显示变化量和百分比