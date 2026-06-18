# 农经权二轮延包可视化平台 — UI 设计规范

> **版本**：v1.0  
> **来源**：基于静态 Demo 提取，作为后续开发的一致性标准  
> **适用范围**：大屏端（1920×1080 及以上）、管理后台页面

---

## 一、配色方案

### 1.1 语义色阶

| 语义变量 | 色值 | 用途 |
|----------|------|------|
| `--bg-primary` | `#0a0e27` | 页面主背景 |
| `--bg-secondary` | `#0d1135` | 次级背景（备用） |
| `--bg-card` | `rgba(13, 25, 65, 0.85)` | 卡片/面板背景（半透明毛玻璃感） |
| `--bg-card-hover` | `rgba(20, 35, 80, 0.9)` | 卡片 hover 背景 |
| `--border-card` | `rgba(32, 80, 160, 0.35)` | 卡片边框 |
| `--border-highlight` | `rgba(0, 180, 255, 0.4)` | 高亮边框（标题栏底线、卡片 hover） |

### 1.2 文字色阶

| 语义变量 | 色值 | 用途 |
|----------|------|------|
| `--text-primary` | `#e8f0ff` | 主文字（标题、数值、表格内容） |
| `--text-secondary` | `rgba(180, 200, 240, 0.75)` | 次要文字（标签、说明、图例文字） |
| `--text-muted` | `rgba(140, 165, 210, 0.55)` | 弱化文字（版权信息、占位提示） |
| `#fff` | 纯白 | 核心数值、指标卡数字 |

### 1.3 强调色体系

| 语义变量 | 色值 | 场景 |
|----------|------|------|
| `--accent-cyan` | `#00d4ff` | **主强调色**：面板标题、选中态、地图标记、图标高亮、筛选 focus |
| `--accent-blue` | `#2196f3` | 辅助蓝（图表系列色之一） |
| `--accent-gold` | `#ffb830` | **辅助强调色**：待处理状态、上报数据系列、警示 |
| `--accent-green` | `#00e676` | 完成态、已通过状态 |
| `--accent-purple` | `#a855f7` | 审核相关指标、特定系列 |
| `--accent-red` | `#ff4757` | 错误、未开始、危急预警 |

### 1.4 渐变色

| 名称 | 定义 | 用途 |
|------|------|------|
| `--gradient-cyan` | `linear-gradient(135deg, #00d4ff, #0080ff)` | 指标卡图标背景（发包方） |
| `--gradient-gold` | `linear-gradient(135deg, #ffb830, #ff8800)` | 指标卡图标背景（承包方） |
| `--gradient-green` | `linear-gradient(135deg, #00e676, #00b862)` | 指标卡图标背景（已摸底） |
| `--gradient-purple` | `linear-gradient(135deg, #a855f7, #7c3aed)` | 指标卡图标背景（内业审核） |
| `--gradient-red` | `linear-gradient(135deg, #ff4757, #e0324a)` | 指标卡图标背景（已完成） |
| 标题渐变 | `linear-gradient(90deg, #ffffff, #00d4ff)` | 大屏标题文字（background-clip: text） |
| 底线渐变 | `linear-gradient(90deg, transparent, #00d4ff, transparent)` | 标题栏装饰线 |

### 1.5 图表系列色

| 用途 | 色值 | 渐变 | 说明 |
|------|------|------|------|
| 已审核/已调查 | `#0090ff` → `#0050cc` | `linear-gradient(180deg, #0090ff, #0050cc)` | 柱状图蓝色系列 |
| 已上报 | `#ffb830` → `#e09500` | `linear-gradient(180deg, #ffb830, #e09500)` | 柱状图金色系列 |

### 1.6 饼图分类色

| 分类 | 色值 |
|------|------|
| 分户-保留户 | `#4fc3f7` |
| 分户-新增户 | `#ffd54f` |
| 地块转 | `#81c784` |
| 有变化 | `#ff8a65` |
| 无变化 | `#7986cb` |

---

## 二、字体规范

### 2.1 字体族

```css
font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
```

- 优先使用 PingFang SC（macOS 系统字体，清晰锐利）
- Windows 降级使用 Microsoft YaHei
- 全局开启字体平滑：`-webkit-font-smoothing: antialiased`

### 2.2 字体层级

| 层级 | 字号 | 字重 | 字间距 | 行高 | 用途 |
|------|------|------|--------|------|------|
| **H1 大屏标题** | `22px` | 700 (Bold) | `6px` | — | 页面顶部主标题 |
| **数值-大** | `26px` | 700 (Bold) | `1px` | — | 指标卡核心数值 |
| **数值-中** | `20px` | 700 (Bold) | — | — | 用途统计卡片数值 |
| **数值-饼图中心** | `16px` | 700 (Bold) | — | — | 饼图中心汇总数字 |
| **正文-主** | `13px` | 400 (Regular) | — | — | 日期、筛选框文字、面板 body |
| **正文-次** | `12px` | 400 (Regular) | — | — | 表格内容、分页文字 |
| **标签-大** | `13px` | 600 (SemiBold) | `1px` | — | 面板 header 标题 |
| **标签-中** | `12px` | 400 (Regular) | `1px` | — | 指标卡标签文字 |
| **标签-小** | `11px` | 400/500 | — | — | 图例文字、状态标签、表格表头、饼图图例 |
| **标签-微** | `9px` | 400 (Regular) | — | — | 饼图中心标签、柱状图 X 轴 |
| **版权** | `10px` | 400 (Regular) | — | — | 地图版权信息 |

---

## 三、阴影与光效

### 3.1 阴影

| 名称 | 定义 | 用途 |
|------|------|------|
| `--shadow-card` | `0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(100,180,255,0.06)` | 所有面板/卡片 |
| 图标阴影-青 | `0 4px 12px rgba(0,212,255,0.3)` | cyan 指标卡图标 |
| 图标阴影-金 | `0 4px 12px rgba(255,184,48,0.3)` | gold 指标卡图标 |
| 图标阴影-绿 | `0 4px 12px rgba(0,230,118,0.3)` | green 指标卡图标 |
| 图标阴影-紫 | `0 4px 12px rgba(168,85,247,0.3)` | purple 指标卡图标 |
| 图标阴影-红 | `0 4px 12px rgba(255,71,87,0.3)` | red 指标卡图标 |
| 柱状图-蓝 | `0 0 8px rgba(0,144,255,0.3)` | 已审核柱体 |
| 柱状图-金 | `0 0 8px rgba(255,184,48,0.3)` | 已上报柱体 |

### 3.2 光效 / 发光

| 名称 | 定义 | 用途 |
|------|------|------|
| `--glow-cyan` | `0 0 20px rgba(0,212,255,0.15)` | 卡片 hover 发光 |
| 地图标记外圈 | `0 0 16px rgba(0,212,255,0.6), 0 0 40px rgba(0,212,255,0.2)` | 村组标记点常驻 |
| 地图标记脉冲 | `0 0 24px rgba(0,212,255,0.8)` | 村组标记点动画峰值 |

### 3.3 背景装饰光

```css
/* body::before — 页面全局氛围光 */
radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,80,180,0.12), transparent 60%),   /* 顶部中央蓝光 */
radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,160,255,0.06), transparent 50%), /* 右下角青光 */
radial-gradient(ellipse 50% 30% at 10% 80%, rgba(100,0,200,0.05), transparent 50%)   /* 左下角紫光 */
```

---

## 四、圆角规范

| 组件 | 圆角值 |
|------|--------|
| 面板/卡片 | `8px` |
| 指标卡图标容器 | `10px` |
| 下拉选择框 | `6px` |
| 用途统计小卡片 | `6px` |
| 地图标记标签 | `4px` |
| 地图控件按钮 | `4px` |
| 分页按钮 | `4px` |
| 状态标签 | `3px` |
| 类型标签 | `3px` |
| 柱状图柱体 | `3px 3px 0 0`（顶部圆角） |
| 饼图中心圆 | `50%` |
| 分页指示器圆点 | `50%` → `3px`（active 态拉伸） |
| 图例色块 | `2px` |

---

## 五、间距与布局

### 5.1 全局间距

| 位置 | 值 |
|------|------|
| 大屏容器 padding | `12px 16px` |
| 大屏容器 gap | `10px` |
| 三栏列 gap | `12px` |
| 左/右侧栏内面板 gap | `10px` |
| 指标卡行 gap | `12px` |
| 用途统计网格 gap | `8px` |

### 5.2 面板内部间距

| 位置 | 值 |
|------|------|
| 面板 header padding | `10px 14px` |
| 面板 body padding | `12px 14px` |
| 指标卡 padding | `14px 18px` |
| 指标卡图标与文字 gap | `14px` |
| 用途统计小卡 padding | `12px` |
| 筛选框 padding | `8px 12px` |

### 5.3 三栏比例

```css
grid-template-columns: 280px 1fr 300px;
```

- 左侧固定 280px
- 中央弹性填充
- 右侧固定 300px

### 5.4 指标卡行

```css
grid-template-columns: repeat(5, 1fr);
gap: 12px;
```

---

## 六、组件样式规范

### 6.1 面板 (Panel)

```
┌─────────────────────────────────────────┐
│ ▶ 面板标题                               │  ← header: 13px/600, accent-cyan, letter-spacing 1px
├─────────────────────────────────────────┤  ← 分隔线: rgba(32,80,160,0.2)
│                                         │
│  内容区域                                │  ← body: padding 12px 14px
│                                         │
└─────────────────────────────────────────┘

背景: var(--bg-card)
边框: 1px solid var(--border-card)
圆角: 8px
阴影: var(--shadow-card)
```

### 6.2 指标卡 (Metric Card)

```
┌──────────────────────────┐
│  ┌────┐                  │
│  │图标│  标签文字          │  ← label: 12px, text-secondary, letter-spacing 1px
│  │44px│  数值             │  ← value: 26px/700, #fff, letter-spacing 1px
│  └────┘                  │
└──────────────────────────┘

卡片: padding 14px 18px, bg-card, border-card, rounded-8, shadow-card
图标容器: 44×44px, rounded-10, 渐变背景 + 对应色阴影
图标与文字 gap: 14px
Hover: border → border-highlight, shadow → glow-cyan
```

### 6.3 下拉选择框 (Select)

```
┌─────────────────────── ▾┐
│  村组                    │  ← 13px, text-primary
└─────────────────────────┘

背景: rgba(10,20,50,0.7)
边框: 1px solid var(--border-card)
圆角: 6px
padding: 8px 12px
下拉箭头: SVG 内联，accent-cyan 色，right 10px center
Focus: border → accent-cyan
外观: appearance: none（自定义箭头）
```

### 6.4 统计小卡片 (Usage Item)

```
┌──────────────┐
│    标签       │  ← 11px, text-secondary
│    数值       │  ← 20px/700, accent-cyan
└──────────────┘

背景: rgba(10,20,50,0.5)
边框: 1px solid rgba(32,80,160,0.2)
圆角: 6px
padding: 12px
文字居中
```

### 6.5 状态标签 (Status Tag)

| 状态 | 背景色 | 文字色 | 边框色 |
|------|--------|--------|--------|
| 待公示 `.public-notice` | `rgba(0,230,118,0.12)` | `#00e676` | `rgba(0,230,118,0.3)` |
| 村干部审核 `.reviewing` | `rgba(0,212,255,0.12)` | `#00d4ff` | `rgba(0,212,255,0.3)` |
| 未调查 `.not-started` | `rgba(255,71,87,0.12)` | `#ff6b7a` | `rgba(255,71,87,0.3)` |
| 待审核 `.pending` | `rgba(255,184,48,0.15)` | `#ffb830` | `rgba(255,184,48,0.3)` |

```
通用: display:inline-block, padding 2px 8px, rounded-3, 11px/500, nowrap
```

### 6.6 类型标签 (Type Tag)

```
┌───────┐
│ 无变化 │  ← 11px, text-secondary
└───────┘

背景: rgba(100,160,255,0.1)
文字: var(--text-secondary)
边框: 1px solid rgba(100,160,255,0.2)
圆角: 3px
padding: 2px 6px
```

### 6.7 数据表格 (Table)

```
┌──────────┬──────────┬──────────┬──────────┐
│ 表头     │ 表头     │ 表头     │ 表头     │  ← 11px/600, text-secondary, border-bottom rgba(32,80,160,0.3)
├──────────┼──────────┼──────────┼──────────┤
│ 内容     │ 内容     │ 内容     │ 状态标签  │  ← 12px, text-primary, border-bottom rgba(32,80,160,0.1)
│ 内容     │ 内容     │ 内容     │ 状态标签  │  ← hover: rgba(0,100,200,0.08)
└──────────┴──────────┴──────────┴──────────┘

表头 padding: 8px 6px
行 padding: 9px 6px
border-collapse: collapse
nowrap: 表头强制不换行
```

### 6.8 分页控件 (Pagination)

```
   ◄  1  ►    前往 [  ] 页

按钮: 26×26px, bg rgba(10,20,50,0.5), border border-card, rounded-4
Hover: border → accent-cyan
文字: 12px, text-secondary
整体: flex center, gap 8px, padding 10px 0 4px
```

### 6.9 分页指示器（饼图）

```
  ● ━━ ● ●    1/3

圆点: 6×6px, rounded-50%, bg rgba(100,160,255,0.3)
Active: bg accent-cyan, width 16px, rounded-3px（拉伸态）
文字: 11px, text-secondary
```

### 6.10 地图控件按钮

```
┌──┐
│ + │  ← 16px, text-primary
└──┘

尺寸: 32×32px
背景: var(--bg-card)
边框: 1px solid var(--border-card)
圆角: 4px
Hover: bg → bg-card-hover, border → accent-cyan
垂直排列: gap 4px
位置: absolute, bottom 16px, right 16px
```

### 6.11 地图村组标记

```
     ┌─────────┐
     │ 村组名称  │  ← 11px, accent-cyan, bg rgba(0,20,60,0.75), padding 2px 8px, rounded-4, border rgba(0,180,255,0.3)
     └────┬────┘
          ●          ← 14×14px, rounded-50%, bg accent-cyan, 脉冲动画

脉冲动画 (2s ease-in-out infinite):
  0%/100%: scale(1), box-shadow 0 0 16px rgba(0,212,255,0.6)
  50%:     scale(1.3), box-shadow 0 0 24px rgba(0,212,255,0.8)
```

---

## 七、标题栏样式

```
┌──────────────────────────────────────────────────────────┐
│  农经权二轮延包可视化平台              2026年06月18日      │
└──────────────────────────┬───────────────────────────────┘
                           └─ 渐变装饰线: linear-gradient(90deg, transparent, #00d4ff, transparent)
                              位置: bottom -1px, left 10%, right 10%

标题: 22px/700, letter-spacing 6px, gradient text (白→青)
日期: 13px, text-secondary, letter-spacing 1px
背景: linear-gradient(90deg, rgba(0,40,100,0.3), rgba(0,80,160,0.15), rgba(0,40,100,0.3))
底部边框: 1px solid border-highlight
padding: 8px 20px
```

---

## 八、动画规范

### 8.1 过渡动画

| 属性 | 时长 | 缓动 | 场景 |
|------|------|------|------|
| `border-color, box-shadow` | `0.3s` | ease | 指标卡 hover |
| `background` | `0.2s` | ease | 地图控件 hover |
| `border-color` | `0.2s` | ease | 分页按钮 hover |
| `opacity` | `0.2s` | ease | 柱状图 hover |

### 8.2 关键帧动画

**脉冲标记 (pulse-dot)**：

```css
@keyframes pulse-dot {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 16px rgba(0,212,255,0.6);
  }
  50% {
    transform: scale(1.3);
    box-shadow: 0 0 24px rgba(0,212,255,0.8);
  }
}
/* 周期: 2s, 缓动: ease-in-out, 重复: infinite */
```

---

## 九、图例规范

### 9.1 通用图例

```
 ■ 已审核   ■ 已上报

色块: 10×10px, rounded-2px
文字: 11px, text-secondary
色块与文字 gap: 5px
图例项之间 gap: 16px
整体居中
```

---

## 十、设计禁忌

| 编号 | 禁止事项 | 原因 |
|------|----------|------|
| D-01 | 禁止在深色背景上使用纯黑文字 | 对比度不足，不可读 |
| D-02 | 禁止卡片使用纯实色背景（opacity = 1） | 破坏毛玻璃氛围感 |
| D-03 | 禁止使用 `#000` 或 `#1a1a1a` 作为边框色 | 与深色背景融合，无层次 |
| D-04 | 禁止状态标签使用实色填充 | 必须保持半透明底 + 边框风格 |
| D-05 | 禁止指标卡数值使用非白色文字 | 核心数据必须最醒目 |
| D-06 | 禁止标题栏装饰线使用实色 | 必须渐变过渡到透明 |
| D-07 | 禁止地图标记使用静态无动画效果 | 脉冲动画是空间感知的关键 |
| D-08 | 禁止新增非规范色系中的颜色 | 新色必须先经本规范确认并补充 |
| D-09 | 禁止圆角超过 10px | 政务系统偏严谨，避免过度圆润 |
| D-10 | 禁止正文使用纯白 `#fff` | 正文使用 `--text-primary` (#e8f0ff)，纯白仅用于数值 |

---

## 十一、CSS 变量速查表

开发时直接复制以下变量块至项目根样式文件：

```css
:root {
  /* 背景 */
  --bg-primary: #0a0e27;
  --bg-secondary: #0d1135;
  --bg-card: rgba(13, 25, 65, 0.85);
  --bg-card-hover: rgba(20, 35, 80, 0.9);
  --bg-input: rgba(10, 20, 50, 0.7);
  --bg-usage-card: rgba(10, 20, 50, 0.5);

  /* 边框 */
  --border-card: rgba(32, 80, 160, 0.35);
  --border-highlight: rgba(0, 180, 255, 0.4);
  --border-divider: rgba(32, 80, 160, 0.2);
  --border-divider-strong: rgba(32, 80, 160, 0.3);
  --border-divider-light: rgba(32, 80, 160, 0.1);

  /* 文字 */
  --text-primary: #e8f0ff;
  --text-secondary: rgba(180, 200, 240, 0.75);
  --text-muted: rgba(140, 165, 210, 0.55);
  --text-value: #ffffff;

  /* 强调色 */
  --accent-cyan: #00d4ff;
  --accent-blue: #2196f3;
  --accent-gold: #ffb830;
  --accent-green: #00e676;
  --accent-purple: #a855f7;
  --accent-red: #ff4757;

  /* 渐变 */
  --gradient-cyan: linear-gradient(135deg, #00d4ff 0%, #0080ff 100%);
  --gradient-gold: linear-gradient(135deg, #ffb830 0%, #ff8800 100%);
  --gradient-green: linear-gradient(135deg, #00e676 0%, #00b862 100%);
  --gradient-purple: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
  --gradient-red: linear-gradient(135deg, #ff4757 0%, #e0324a 100%);
  --gradient-title: linear-gradient(90deg, #ffffff 0%, #00d4ff 100%);
  --gradient-header-bg: linear-gradient(90deg, rgba(0,40,100,0.3) 0%, rgba(0,80,160,0.15) 50%, rgba(0,40,100,0.3) 100%);
  --gradient-header-line: linear-gradient(90deg, transparent, #00d4ff, transparent);
  --gradient-bar-blue: linear-gradient(180deg, #0090ff 0%, #0050cc 100%);
  --gradient-bar-gold: linear-gradient(180deg, #ffb830 0%, #e09500 100%);

  /* 阴影 */
  --shadow-card: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(100,180,255,0.06);
  --glow-cyan: 0 0 20px rgba(0,212,255,0.15);

  /* 字体 */
  --font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
}
```
