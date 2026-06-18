# 农经权二轮延包可视化平台 — 开发计划

> **版本**：v1.0  
> **编制日期**：2025-07-11  
> **总步骤**：8 步（P0 首期交付 = Step 1~7，P1 二期 = Step 8）  
> **设计依据**：PRD.md + ui-design-spec.md + high-level-design.md + 静态 Demo

---

## 项目背景（供新会话理解）

本项目是一个**数据监控可视化大屏平台**，不是业务操作管理系统。

- **核心定位**：专业内业软件处理好的确权数据，输出为 ZIP 数据包（含 MDB 数据库 + Shapefile 矢量数据 + XLS 代码表），本平台负责**导入这些数据包 → 自动聚合统计 → 大屏可视化呈现**，让各级领导一目了然掌握项目进度。
- **数据格式**：ZIP 内含 `*.mdb`（Access 数据库，12 张业务表：FBF/CBF/CBF_JTCY/CBHT/CBDKXX/CBJYQZ 等）、`DK.shp/.dbf/.prj/.shx`（地块矢量，EPSG:4527 坐标系）、`权属单位代码表.xls`
- **设计风格**：深色科技风大屏，主色 #0a0e27 深蓝底 + #00d4ff 青色高亮 + #ffb830 金色辅助
- **现有产出**：静态 Demo（`index.html` + `styles/main.css`）、PRD、UI 设计规范、概要设计文档

---

## Step 1 — 项目初始化 & 基础框架搭建

### 目标
将项目从原生 HTML 迁移到 Next.js 全栈框架，建立前后端分离的项目骨架，确保开发服务器可启动、首页可访问。

### 要实现的功能
1. 使用 `coze init` 初始化 Next.js 项目（`--template nextjs`）
2. 配置 Tailwind CSS 4，将 UI 规范中所有 CSS 变量写入 `globals.css` 的 `@theme`
3. 实现大屏布局骨架：顶部标题栏 + 核心指标卡行 + 三栏（左 280px / 中弹性 / 右 300px）
4. 顶部标题栏：渐变标题「农经权二轮延包可视化平台」+ 当前日期 + 渐变装饰线
5. 所有面板/卡片使用 UI 规范中的深色半透明背景 + 边框样式，暂时放置占位文字

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `src/app/layout.tsx` | 根布局，引入全局样式 |
| `src/app/globals.css` | 全局 CSS 变量（从 ui-design-spec.md 复制 `:root` 变量块）、Tailwind @theme |
| `src/app/page.tsx` | 大屏页面骨架（重定向到 /dashboard 或直接作为大屏） |
| `src/components/dashboard/DashboardLayout.tsx` | 大屏布局容器：header + metric-row + 三栏 grid |
| `src/components/dashboard/Header.tsx` | 顶部标题栏组件 |
| `src/components/dashboard/MetricCard.tsx` | 指标卡组件（接受 label/value/icon-variant 属性） |
| `src/components/dashboard/Panel.tsx` | 通用面板组件（header + body 插槽） |

### 完成标准
- [ ] `pnpm dev` 启动无报错，访问 localhost:5000 可看到深色背景大屏骨架
- [ ] 顶部标题栏显示渐变标题 + 日期 + 装饰线，与 Demo 一致
- [ ] 5 个指标卡占位（数值暂时写死 0），样式与 Demo 一致
- [ ] 三栏布局比例正确（左 280 / 中弹性 / 右 300），各面板占位框可见
- [ ] CSS 变量完整覆盖 UI 规范速查表所有变量

---

## Step 2 — 数据库建模 & 后端 API 骨架

### 目标
建立 PostgreSQL 数据库表结构，创建 FastAPI 后端服务的基础骨架和数据库连接，实现第一个健康检查接口。

### 要实现的功能
1. 设计并创建 PostgreSQL 数据库表（基于概要设计文档，对齐 MDB 实际字段）
   - 核心业务表：`fbf`（发包方）、`cbf`（承包方）、`cbf_jtcy`（家庭成员）、`cbht`（合同）、`cbdkxx`（承包地块）、`land_parcel_geom`（地块空间几何）
   - 编码/字典表：`dict_item`（字典项）、`admin_division`（行政区划树）
   - 系统表：`import_task`（导入任务）、`import_error`（导入错误）、`indicator_snapshot`（指标快照）
2. 使用 SQLAlchemy 2.0 + GeoAlchemy2 定义 ORM 模型
3. 配置 Alembic 数据库迁移
4. 创建 FastAPI 应用骨架：项目配置、数据库连接、CORS 中间件
5. 实现 `/api/health` 健康检查接口

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `backend/app/main.py` | FastAPI 应用入口 |
| `backend/app/config.py` | 配置管理（数据库连接串从环境变量读取） |
| `backend/app/database.py` | SQLAlchemy 引擎 + Session 工厂 |
| `backend/app/models/__init__.py` | 模型导出 |
| `backend/app/models/fbf.py` | 发包方模型 |
| `backend/app/models/cbf.py` | 承包方模型 |
| `backend/app/models/cbf_jtcy.py` | 家庭成员模型 |
| `backend/app/models/cbht.py` | 合同模型 |
| `backend/app/models/cbdkxx.py` | 承包地块模型 |
| `backend/app/models/land_parcel_geom.py` | 地块空间几何模型 |
| `backend/app/models/dict_item.py` | 字典项模型 |
| `backend/app/models/admin_division.py` | 行政区划模型 |
| `backend/app/models/import_task.py` | 导入任务模型 |
| `backend/app/models/import_error.py` | 导入错误模型 |
| `backend/app/models/indicator_snapshot.py` | 指标快照模型 |
| `backend/app/api/health.py` | 健康检查路由 |
| `backend/alembic.ini` | Alembic 配置 |
| `backend/alembic/env.py` | Alembic 迁移环境 |
| `backend/requirements.txt` | Python 依赖清单 |

### 完成标准
- [ ] `alembic upgrade head` 成功创建所有表（可用 `\dt` 验证）
- [ ] `uvicorn backend.app.main:app` 启动无报错
- [ ] `GET /api/health` 返回 `{"status": "ok", "db": "connected"}`
- [ ] 所有模型字段与概要设计文档中的表结构一致
- [ ] GeoAlchemy2 的 Geometry 列类型正确配置（SRID=4326）

---

## Step 3 — 数据包导入功能

### 目标
实现 ZIP 数据包上传 → 解压 → 解析 MDB/Shapefile → 入库 → 坐标转换的全流程，这是整个平台的数据入口。

### 要实现的功能
1. 文件上传接口：接收 ZIP 文件，保存到临时目录
2. 解压与识别：自动识别 ZIP 内的 MDB 文件、Shapefile 文件集、XLS 文件
3. MDB 解析：使用 `mdb-tools` 或 `pandas-access` 读取 12 张业务表，逐条写入 PostgreSQL
4. Shapefile 解析：使用 `geopandas` 读取 DK.shp，将几何字段从 EPSG:4527 转换为 EPSG:4326 后写入 `land_parcel_geom` 表
5. XLS 代码表解析：读取权属单位代码表，构建行政区划树（县→镇→村→组）
6. 数据校验：编码格式校验（CBFBM 18 位 / DKBM 19 位等）、必填字段非空、外键引用完整性
7. 导入任务状态追踪：记录导入开始/完成/失败时间、成功/失败条数
8. 错误记录：每条失败记录写入 `import_error` 表，含表名、编码、错误原因

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `backend/app/api/import_api.py` | 导入相关路由（上传 / 状态查询 / 错误查询） |
| `backend/app/services/unzip_service.py` | ZIP 解压与文件识别 |
| `backend/app/services/mdb_parser.py` | MDB 表数据解析与入库 |
| `backend/app/services/shp_parser.py` | Shapefile 解析 + 坐标转换 + 入库 |
| `backend/app/services/xls_parser.py` | XLS 代码表解析 + 行政区划树构建 |
| `backend/app/services/validator.py` | 数据校验逻辑 |
| `backend/app/services/import_service.py` | 导入编排服务（串联上述步骤） |
| `backend/app/schemas/import_schema.py` | Pydantic 请求/响应模型 |

### 完成标准
- [ ] 上传 `370199测试县.zip` 后，`fbd` 表有 21 条记录、`cbf` 表有 657 条、`cbdkxx` 有 2920 条
- [ ] `land_parcel_geom` 表中几何数据 SRID=4326，用 `ST_AsGeoJSON` 可正确输出多边形
- [ ] `admin_division` 表构建出完整的行政区划树（县→镇→村→组层级）
- [ ] `dict_item` 表包含 SYQXZ/DKLB/TDLYLX/DLDJ 等字典的编码-名称映射
- [ ] 导入过程中故意传入含错误数据的 ZIP，`import_error` 表有对应错误记录
- [ ] `GET /api/import/tasks` 返回导入任务列表及状态

---

## Step 4 — 指标聚合计算 & API 接口

### 目标
实现核心指标的聚合计算逻辑，提供前端大屏所需的所有数据接口。这是大屏的数据引擎。

### 要实现的功能
1. 指标聚合服务：导入完成后自动计算以下指标
   - 全局指标：发包方总数、承包方总数、已摸底户数、已内业审核数、已完成户数
   - 用途统计：种植业/林业/畜牧业/渔业地块数量（从 CBDKXX.TDYT + 字典翻译）
   - 摸底填报：按村组统计已上报户数 vs 已审核户数（分组柱状图数据）
   - 填报分类：分户保留户/新增户/地块转/有变化/无变化的占比（饼图数据）
   - 审核列表：承包方名称/村组/上报类型/当前状态（分页表格数据）
2. 聚合粒度：支持全局 / 按镇 / 按村 / 按组 四级
3. 筛选参数：接收行政区划代码前缀，返回对应粒度的聚合数据
4. Redis 缓存：聚合结果缓存至 Redis，TTL 5 分钟，导入新数据后主动刷新
5. 指标快照：每次导入后保存一份 `indicator_snapshot`，供后续趋势对比

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `backend/app/api/indicator_api.py` | 指标查询路由 |
| `backend/app/services/indicator_service.py` | 指标聚合计算核心逻辑 |
| `backend/app/services/cache_service.py` | Redis 缓存读写逻辑 |
| `backend/app/schemas/indicator_schema.py` | 指标响应 Pydantic 模型 |
| `backend/app/api/audit_api.py` | 审核列表查询路由（分页） |
| `backend/app/schemas/audit_schema.py` | 审核列表响应模型 |

### 完成标准
- [ ] `GET /api/indicators/overview` 返回 5 个核心指标，数值与 Demo 一致（发包方 21 / 承包方 657 / 已摸底 538 / 已审核 331 / 已完成 26）
- [ ] `GET /api/indicators/overview?village_code=370199xxx` 返回指定村的指标
- [ ] `GET /api/indicators/land-usage` 返回种植业 3810 / 林业 47 / 畜牧业 20 / 渔业 12
- [ ] `GET /api/indicators/survey-stats` 返回按村组分组的已上报/已审核户数
- [ ] `GET /api/indicators/survey-categories` 返回饼图分类占比数据
- [ ] `GET /api/audit/list?page=1&size=10` 返回审核表格分页数据
- [ ] 第二次请求命中 Redis 缓存（响应时间 < 50ms）
- [ ] 重新导入数据后缓存自动刷新

---

## Step 5 — 大屏前端开发（左栏 + 指标卡）

### 目标
将 Demo 中左侧栏和顶部指标卡从静态 HTML 迁移为 Next.js 动态组件，对接后端 API 获取真实数据。

### 要实现的功能
1. **指标卡组**（顶部 5 卡）：
   - 从 `/api/indicators/overview` 获取数据，动态渲染
   - 每张卡：渐变图标 + 标签 + 数值，数据加载前显示 skeleton
2. **权属单位筛选**（左上）：
   - 从 `/api/admin-divisions/tree` 获取行政区划树
   - 双层下拉框：第一级选村、第二级选组
   - 选择后触发全局筛选，所有面板数据联动刷新
3. **承包地块用途统计**（左中）：
   - 从 `/api/indicators/land-usage` 获取数据
   - 4 个统计小卡片（种植业/林业/畜牧业/渔业）
4. **摸底填报情况统计**（左下）：
   - 从 `/api/indicators/survey-stats` 获取数据
   - 使用 ECharts 渲染分组柱状图（蓝=已审核 / 金=已上报）
   - 横轴显示村组名称，纵轴显示户数

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `src/components/dashboard/MetricCard.tsx` | 指标卡组件（改造为动态数据） |
| `src/components/dashboard/MetricRow.tsx` | 指标卡行容器 |
| `src/components/dashboard/FilterPanel.tsx` | 权属单位筛选面板 |
| `src/components/dashboard/LandUsagePanel.tsx` | 地块用途统计面板 |
| `src/components/dashboard/SurveyBarChart.tsx` | 摸底填报柱状图面板 |
| `src/lib/api.ts` | 前端 API 请求封装（统一 baseURL + 错误处理） |
| `src/hooks/useIndicators.ts` | 指标数据 SWR hook |
| `src/hooks/useFilter.ts` | 筛选状态管理 hook |
| `src/app/dashboard/page.tsx` | 大屏页面（组合所有组件） |

### 完成标准
- [ ] 5 个指标卡显示从后端 API 获取的真实数值
- [ ] 筛选框可选村→组，选择后指标卡和柱状图数据联动更新
- [ ] 用途统计 4 卡显示真实地块分类数量
- [ ] 柱状图正确渲染分组数据，蓝/金双色与 Demo 一致
- [ ] 数据加载中显示 skeleton 动画，加载失败显示错误提示

---

## Step 6 — 大屏前端开发（中央地图 + 右栏）

### 目标
完成大屏中央天地图和右侧饼图、审核表格的开发，实现完整大屏。

### 要实现的功能
1. **天地图**（中央）：
   - 接入天地图 API（需申请 Key），展示行政区划底图
   - 从 `/api/indicators/villages` 获取村组坐标列表，在地图上标注脉冲标记点
   - 地图缩放控件（+/-/定位）
   - 底部版权信息 `天地图 GS(2024)0568号`
   - *如天地图 Key 不可用，降级使用 Leaflet + OpenStreetMap*
2. **摸底填报统计饼图**（右上）：
   - 从 `/api/indicators/survey-categories` 获取数据
   - 使用 ECharts 渲染环形饼图（5 分类 + 中心数字 + 图例）
   - 分页指示器（1/3），点击切换饼图数据组
3. **内业审核表格**（右下）：
   - 从 `/api/audit/list` 获取分页数据
   - 渲染表格：承包方名称 / 村组 / 上报类型 / 当前状态
   - 状态列使用彩色标签（待公示=绿 / 村干部审核=青 / 未调查=红 / 待审核=金）
   - 分页控件：上一页 / 下一页 / 页码 / 前往

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `src/components/dashboard/MapPanel.tsx` | 天地图面板组件 |
| `src/components/dashboard/SurveyPieChart.tsx` | 填报统计饼图面板 |
| `src/components/dashboard/AuditTable.tsx` | 内业审核表格面板 |
| `src/components/dashboard/Pagination.tsx` | 通用分页控件 |
| `src/components/dashboard/StatusTag.tsx` | 状态标签组件 |
| `src/components/dashboard/TypeTag.tsx` | 类型标签组件 |
| `src/hooks/useAuditList.ts` | 审核列表分页 hook |
| `src/hooks/useSurveyCategories.ts` | 饼图数据 hook |

### 完成标准
- [ ] 天地图可正常加载，显示行政区划底图 + 村组标记点（脉冲动画）
- [ ] 饼图正确渲染 5 分类环形图，分页切换正常
- [ ] 审核表格显示真实数据，状态标签颜色正确
- [ ] 分页控件可用，翻页后表格数据更新
- [ ] 整体大屏视觉效果与静态 Demo 一致（对照 ui-design-spec.md）
- [ ] 筛选联动：左侧选择村组后，地图定位到该区域、饼图和表格数据同步更新

---

## Step 7 — 数据导入管理页 & 登录页

### 目标
完成两个 P0 辅助页面，实现完整的首期交付闭环。

### 要实现的功能
1. **数据导入管理页**（`/import`）：
   - 文件拖拽上传区域（支持 ZIP）
   - 上传进度条
   - 导入开始按钮 → 调用 `/api/import/upload` → 轮询 `/api/import/tasks/{id}` 获取进度
   - 导入历史表格：导入时间 / 文件名 / 状态 / 成功数 / 失败数 / 操作（查看详情）
   - 错误详情弹窗：展示 `import_error` 表中的校验失败记录
   - 页面顶部"返回大屏"导航
2. **登录页**（`/login`）：
   - 居中卡片式登录表单：用户名 + 密码 + 登录按钮
   - 深色背景 + 氛围光效（与主屏统一风格）
   - 暂用硬编码账号（admin/admin），后续对接 Supabase Auth
   - 登录成功后跳转至 `/dashboard`
3. **路由守卫**：未登录访问 `/dashboard` 或 `/import` 时重定向到 `/login`

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `src/app/import/page.tsx` | 数据导入管理页 |
| `src/app/login/page.tsx` | 登录页 |
| `src/components/import/DropZone.tsx` | 文件拖拽上传组件 |
| `src/components/import/ImportHistory.tsx` | 导入历史表格 |
| `src/components/import/ImportProgress.tsx` | 导入进度组件 |
| `src/components/import/ErrorDetail.tsx` | 错误详情弹窗 |
| `src/components/auth/LoginForm.tsx` | 登录表单组件 |
| `src/middleware.ts` | Next.js 路由守卫 |
| `src/lib/auth.ts` | 前端认证工具（token 存取 / 登出） |
| `backend/app/api/auth_api.py` | 登录接口（临时硬编码校验） |

### 完成标准
- [ ] 拖拽上传 ZIP 文件后，点击"开始导入"可触发后端导入流程
- [ ] 导入历史表格显示历史导入记录，状态/成功数/失败数正确
- [ ] 点击"详情"可查看导入错误记录
- [ ] 登录页输入 admin/admin 可登录并跳转大屏
- [ ] 未登录状态访问 `/dashboard` 自动跳转 `/login`
- [ ] 登录后点击"返回大屏"可正常导航

---

## Step 8 — P1 增强功能（村组下钻 + 趋势 + 质量看板）

### 目标
实现二期增强功能，包括村组详情下钻弹窗、确权发证监控、进度趋势、数据质量看板。

### 要实现的功能
1. **村组详情弹窗**（大屏下钻）：
   - 点击地图标记或柱状图村组名称，弹出该村详情面板
   - 展示：总户数/已摸底/已审核/已完成/流转中 5 个指标 + 3 条进度条
   - 地块用途分布饼图 + 家庭成员统计
2. **确权发证进度监控**：
   - 新增指标卡：合同签订率 / 发证率 / 领证率
   - 后端聚合 CBJYQZ / CBHT 表数据
3. **进度趋势折线**：
   - 基于 `indicator_snapshot` 表按日/周聚合
   - ECharts 折线图，支持选择指标类型
4. **数据质量看板**（`/quality`）：
   - 空间重叠检测（PostGIS `ST_Overlaps`）
   - 面积异常检测（面积为 0 或超阈值）
   - 编码校验异常
   - 异常明细表格 + 严重程度标签
5. **历史数据包版本对比**（`/trend`）：
   - 选择两次导入快照进行指标差异对比
   - 差异表格：指标 / 基准值 / 对比值 / 变化量与百分比

### 涉及的文件

| 文件 | 说明 |
|------|------|
| `src/components/dashboard/VillageDetailModal.tsx` | 村组详情弹窗 |
| `src/components/dashboard/CertProgressCards.tsx` | 发证进度指标卡 |
| `src/components/dashboard/TrendChart.tsx` | 趋势折线图 |
| `src/app/quality/page.tsx` | 数据质量看板页 |
| `src/app/trend/page.tsx` | 历史趋势对比页 |
| `backend/app/services/quality_service.py` | 数据质量检测逻辑 |
| `backend/app/services/snapshot_service.py` | 快照对比逻辑 |
| `backend/app/api/quality_api.py` | 质量检测路由 |
| `backend/app/api/snapshot_api.py` | 快照对比路由 |
| `backend/app/api/cert_api.py` | 发证进度路由 |

### 完成标准
- [ ] 点击地图村组标记，弹窗显示该村的 5 个指标 + 进度条
- [ ] 发证指标卡显示真实计算值
- [ ] 趋势折线图可按日/周切换，至少有 2 个数据点
- [ ] 数据质量看板显示空间重叠/面积异常/编码异常的数量
- [ ] 版本对比页可选择两次导入，差异表格正确显示变化量和百分比

---

## 项目技术栈总览

### 前端

| 层面 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | Next.js (App Router) | 16 | SSR/SSG 全栈框架，路由 + API Routes |
| UI 库 | React | 19 | 组件化 UI |
| 样式 | Tailwind CSS | 4 | 原子化 CSS，配合 @theme 管理设计变量 |
| 图表 | ECharts | 5 | 柱状图 / 饼图 / 折线图 |
| 地图 | 天地图 JS API / Leaflet | — | 行政区划底图 + 村组标注 |
| 数据请求 | SWR | 2 | 前端数据缓存 + 自动重验证 |
| 语言 | TypeScript | 5 | 类型安全 |
| 包管理 | pnpm | — | 依赖管理 |

### 后端

| 层面 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | FastAPI | 0.115+ | 异步高性能 API 框架 |
| ORM | SQLAlchemy | 2.0 | 数据库模型 + 查询 |
| 空间 ORM | GeoAlchemy2 | — | PostGIS Geometry 字段支持 |
| 迁移 | Alembic | — | 数据库版本管理 |
| 校验 | Pydantic | 2 | 请求/响应数据模型 |
| 数据解析 | pandas + geopandas | — | MDB / Shapefile / XLS 解析 |
| MDB 读取 | mdb-tools (系统命令) | — | 导出 MDB 表为 CSV |
| 坐标转换 | pyproj | — | EPSG:4527 → EPSG:4326 |
| 缓存 | Redis | 7+ | 指标缓存 + 会话存储 |
| 任务队列 | Celery | 5 | 异步导入任务 |
| 语言 | Python | 3.11+ | — |

### 数据库

| 层面 | 技术 | 用途 |
|------|------|------|
| 主库 | PostgreSQL 16 + PostGIS 3.4 | 业务数据 + 空间数据 |
| 缓存 | Redis 7 | 指标缓存 + Celery Broker |

### 部署

| 层面 | 方式 | 说明 |
|------|------|------|
| 前端 | Next.js 内置（端口 5000） | 由 `.coze` 配置管理 build/run |
| 后端 | Uvicorn + Gunicorn | ASGI 生产部署，独立端口（如 8000） |
| 数据库 | Supabase 托管 PostgreSQL | 开发环境使用沙箱本地 PostgreSQL |
| 文件存储 | MinIO / S3 | 数据包 ZIP 暂存、导入后可清理 |

### 关键环境变量

| 变量 | 用途 |
|------|------|
| `DEPLOY_RUN_PORT` | 前端服务监听端口（必须从此读取） |
| `DATABASE_URL` | PostgreSQL 连接串 |
| `REDIS_URL` | Redis 连接串 |
| `TIANDITU_KEY` | 天地图 API Key |
| `COZE_PROJECT_DOMAIN_DEFAULT` | 对外访问域名 |

### 参考文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| 产品需求文档 | `PRDS/PRD.md` | 功能范围、页面结构、优先级 |
| UI 设计规范 | `doc/ui-design-spec.md` | 配色/字体/组件样式，开发时必读 |
| 概要设计文档 | `doc/high-level-design.md` | 数据架构、模块划分、数据库表设计 |
| 静态 Demo | `index.html` + `styles/main.css` | 视觉还原的参考标准 |
