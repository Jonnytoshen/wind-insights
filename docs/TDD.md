# 技术设计文档（TDD）
# Wind Insights —— 基于 MERRA2 的虚拟测风塔分析可视化应用

| 字段     | 内容                              |
| -------- | --------------------------------- |
| 版本     | v1.1                              |
| 创建日期 | 2026-03-13                        |
| 状态     | 草稿                              |
| 关联文档 | [PRD.md](./PRD.md)                |

---

## 目录

1. [技术选型总览](#1-技术选型总览)
2. [项目结构](#2-项目结构)
3. [前端架构](#3-前端架构)
   - [3.7 Tailwind CSS 4 集成](#37-tailwind-css-4-集成)
4. [后端架构](#4-后端架构)
5. [数据流设计](#5-数据流设计)
6. [API 接口规范](#6-api-接口规范)
7. [数据模型](#7-数据模型)
8. [核心算法实现](#8-核心算法实现)
   - [8.6 代表年选取](#86-代表年选取algorithmrepresentative_yearpy)
9. [PDF 报告生成](#9-pdf-报告生成)
10. [部署与运维](#10-部署与运维)
11. [性能策略](#11-性能策略)
12. [安全策略](#12-安全策略)

---

## 1. 技术选型总览

| 层级         | 技术                                     | 版本要求   |
| ------------ | ---------------------------------------- | ---------- |
| 前端框架     | Vue 3 + TypeScript                       | Vue ≥ 3.4  |
| 构建工具     | Vite                                     | ≥ 5.0      |
| CSS 框架      | Tailwind CSS 4                           | ≥ 4.0      |
| UI 组件库    | shadcn-vue                               | 最新       |
| 地图         | Mapbox GL JS                             | ≥ 3.0      |
| 图表         | Apache ECharts 5                         | ≥ 5.5      |
| 状态管理     | Pinia                                    | ≥ 2.1      |
| HTTP 客户端  | Axios                                    | ≥ 1.6      |
| 实时进度     | SSE（EventSource）                       | 浏览器原生 |
| 后端框架     | FastAPI                                  | ≥ 0.111    |
| Python 版本  | Python 3.12                              |            |
| Python 包管理 | uv                                       | 最新       |
| 异步运行时   | Uvicorn + asyncio                        |            |
| 数据处理     | Pandas 2 + NumPy + SciPy                 |            |
| HTTP 客户端  | httpx（async）                           | ≥ 0.27     |
| PDF 生成     | WeasyPrint                               | ≥ 62       |
| 缓存         | 内存 dict（MVP）→ Redis（生产可升级）     |            |
| 容器化       | Docker + Docker Compose                  |            |
| 反向代理     | Nginx                                    | ≥ 1.25     |

---

## 2. 项目结构

```
wind-insights/
├── frontend/                      # Vue 3 前端
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   │   └── main.css               # Tailwind CSS 4 入口（@import "tailwindcss"）
│   │   ├── components/            # 通用组件
│   │   │   ├── map/               # 地图相关组件
│   │   │   ├── charts/            # 图表组件（玫瑰图、Weibull 等）
│   │   │   └── wizard/            # Wizard 步骤组件
│   │   ├── views/                 # 页面视图（Step1～Step6）
│   │   ├── stores/                # Pinia stores
│   │   │   ├── wizard.ts          # 向导流程状态
│   │   │   ├── analysis.ts        # 分析结果状态
│   │   │   └── history.ts         # 历史记录（localStorage）
│   │   ├── composables/           # 组合式函数
│   │   │   ├── useSSE.ts          # SSE 进度订阅
│   │   │   └── useAnalysis.ts     # 分析任务管理
│   │   ├── api/                   # API 请求封装
│   │   │   └── index.ts
│   │   ├── types/                 # TypeScript 类型定义
│   │   │   └── analysis.ts
│   │   ├── utils/
│   │   │   └── geoUtils.ts        # MERRA2 网格点计算
│   │   ├── router/
│   │   └── App.vue
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                       # FastAPI 后端
│   ├── app/
│   │   ├── main.py                # FastAPI 入口
│   │   ├── config.py              # 配置（env 变量）
│   │   ├── routers/
│   │   │   ├── analysis.py        # 分析任务路由
│   │   │   └── report.py          # PDF 报告路由
│   │   ├── services/
│   │   │   ├── nasa_power.py      # NASA POWER API 代理
│   │   │   ├── analysis_engine.py # 统计分析引擎
│   │   │   └── pdf_generator.py   # PDF 生成服务
│   │   ├── models/
│   │   │   ├── request.py         # Pydantic 请求模型
│   │   │   └── response.py        # Pydantic 响应模型
│   │   ├── core/
│   │   │   ├── cache.py           # 内存缓存管理
│   │   │   ├── task_manager.py    # 异步任务状态管理
│   │   │   └── validators.py      # 参数校验
│   │   └── algorithms/
│   │       ├── weibull.py         # Weibull MLE 拟合
│   │       ├── extreme_wind.py    # 极端风速（Gumbel）
│   │       ├── turbulence.py      # 湍流强度
│   │       ├── shear.py           # 风切变回归
│   │       └── representative_year.py  # 代表年选取
│   ├── templates/                 # WeasyPrint PDF HTML 模板
│   │   ├── report_base.html
│   │   └── report_style.css
│   ├── pyproject.toml             # uv 项目配置（依赖声明）
│   ├── uv.lock                    # 依赖锁文件（提交到版本控制）
│   └── Dockerfile
│
├── docs/
│   ├── PRD.md
│   └── TDD.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 3. 前端架构

### 3.1 路由设计

应用为单页（SPA），路由仅区分主页面与可能的独立报告预览页。Wizard 步骤不使用独立路由，通过 Pinia store 管理当前步骤索引。

```
/           → 主应用（Wizard 全流程）
/preview    → PDF 报告预览页（WeasyPrint 渲染前的 HTML 预览，可选）
```

### 3.2 状态管理（Pinia）

#### `stores/wizard.ts`

```ts
interface WizardStore {
  currentStep: number          // 0-5，对应 6 个步骤
  location: {
    lng: number
    lat: number
    label?: string             // 地名（可选）
  } | null
  params: AnalysisParams       // 用户配置的分析参数
  taskId: string | null        // 后端分析任务 ID
  taskStatus: TaskStatus       // idle | running | success | error
  progress: ProgressInfo       // SSE 推送的进度信息
  result: AnalysisResult | null
  reportConfig: ReportConfig   // 报告封面配置
}
```

#### `stores/history.ts`

最近 20 个分析点位持久化到 `localStorage`，键为 `wind_insights_history`。

```ts
interface HistoryItem {
  id: string
  lng: number
  lat: number
  label?: string
  timestamp: number
  summary?: { meanWS: number; wpd: number }  // 若已完成分析可显示摘要
}
```

### 3.3 Wizard 步骤组件结构

```
App.vue
└── WizardShell.vue            # 步骤条 + 导航按钮
    ├── Step1Location.vue      # 地图选点
    ├── Step2Params.vue        # 参数配置
    ├── Step3Loading.vue       # 数据加载进度
    ├── Step4Summary.vue       # 分析总览卡片
    ├── Step5Analysis.vue      # 详细分析（左侧导航 + 各分析视图）
    │   ├── BasicStats.vue
    │   ├── WindRose.vue
    │   ├── WeibullChart.vue
    │   ├── WpdChart.vue
    │   ├── ShearProfile.vue
    │   ├── TiChart.vue
    │   ├── ExtremeWind.vue
    │   └── MultiHeightCompare.vue
    └── Step6Report.vue        # 报告生成
```

### 3.4 SSE 进度订阅（`composables/useSSE.ts`）

```ts
// 使用浏览器原生 EventSource 订阅后端 /api/analysis/{taskId}/progress 端点
export function useSSE(taskId: Ref<string | null>) {
  const progress = ref<ProgressInfo | null>(null)
  const error = ref<string | null>(null)

  watch(taskId, (id) => {
    if (!id) return
    const source = new EventSource(`/api/analysis/${id}/progress`)
    source.onmessage = (e) => {
      progress.value = JSON.parse(e.data)
      if (progress.value?.status === 'success' || progress.value?.status === 'error') {
        source.close()
      }
    }
    source.onerror = () => { error.value = '连接中断'; source.close() }
  })

  return { progress, error }
}
```

### 3.5 地图组件（Mapbox GL JS）

- 底图样式：`mapbox://styles/mapbox/satellite-streets-v12`（卫星+街道叠加）
- 标记点使用自定义 SVG 图标（风塔造型）
- MERRA2 网格叠加层使用 GeoJSON `fill` 图层，`fillOpacity: 0.08`，高亮距选点最近网格
- 网格计算：将经纬度向下取整到最近 0.5°/0.625° 格点

```ts
// utils/geoUtils.ts
export function snapToMerra2Grid(lng: number, lat: number) {
  // MERRA-2 网格：纬度 0.5°，经度 0.625°
  const latGrid = Math.round(lat / 0.5) * 0.5
  const lngGrid = Math.round(lng / 0.625) * 0.625
  return { lat: latGrid, lng: lngGrid }
}
```

### 3.6 图表组件规范

所有图表封装为独立 Vue 组件，接受 `data` prop，内部实例化 ECharts，通过 `ResizeObserver` 响应容器尺寸变化。图表定义统一存放在 `components/charts/` 目录，每个图表对应一个 `.ts` option 工厂函数文件，便于 PDF 生成时复用配置。

### 3.7 Tailwind CSS 4 集成

Tailwind CSS 4 采用 **CSS-first** 配置方式（无 `tailwind.config.js`），通过 `@tailwindcss/vite` Vite 插件驱动，与 shadcn-vue 深度集成。

**安装**

```bash
npm install tailwindcss @tailwindcss/vite
```

**`vite.config.ts` 配置**

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),   // Tailwind CSS 4 Vite 插件，替代 PostCSS 配置
  ],
})
```

**`src/assets/main.css`（全局 CSS 入口）**

```css
@import "tailwindcss";

/* shadcn-vue CSS 变量（颜色、圆角等主题令牌） */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... 其余 shadcn-vue 令牌按需补充 */
  }
}
```

**注意**：Tailwind CSS 4 默认开启 **content 自动检测**（扫描 `src/` 下所有文件），无需手动配置 `content` 路径。如需扩展主题（自定义颜色、字体等），通过 CSS `@theme` 指令内联声明：

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(60% 0.2 250);
  --font-sans: "Noto Sans SC", sans-serif;
}
```

---

## 4. 后端架构

### 4.1 应用入口（`main.py`）

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis, report

app = FastAPI(title="Wind Insights API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 生产环境通过 env 注入
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(report.router, prefix="/api/report")
```

### 4.2 异步任务管理（`core/task_manager.py`）

利用 FastAPI `BackgroundTasks` + `asyncio` 管理分析任务，任务状态存储在内存 dict 中。

```python
# 任务状态结构
class TaskState:
    task_id: str
    status: Literal["running", "success", "error"]
    progress: float          # 0.0 ~ 1.0
    message: str
    result: dict | None
    error: str | None
    created_at: datetime
    sse_queue: asyncio.Queue  # 每个任务独立的 SSE 消息队列
```

任务超时：单个任务超过 300 秒自动标记为 error，释放资源。

### 4.3 NASA POWER API 代理（`services/nasa_power.py`）

```python
import httpx
from asyncio import gather

NASA_BASE = "https://power.larc.nasa.gov/api/temporal/hourly/point"

async def fetch_year(
    client: httpx.AsyncClient,
    lat: float, lon: float,
    year: int,
    wind_elevation: int,
    wind_surface: str,
) -> dict:
    """请求单年单高度数据，返回 JSON。指数退避重试最多 3 次。"""
    params = {
        "parameters": f"WSC{wind_elevation}M,WD50M",  # WSC 为自定义高度风速参数
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "wind-elevation": wind_elevation,
        "wind-surface": wind_surface,
        "time-standard": "UTC",
        "format": "JSON",
    }
    for attempt in range(3):
        try:
            r = await client.get(NASA_BASE, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)

async def fetch_all(lat, lon, heights, start_year, end_year, wind_surface, progress_cb):
    """并行拉取所有年份 × 高度的数据，通过 progress_cb 上报进度。"""
    years = list(range(start_year, end_year + 1))
    total = len(years) * len(heights)
    done = 0

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_year(client, lat, lon, yr, h, wind_surface)
            for yr in years for h in heights
        ]
        results = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            done += 1
            await progress_cb(done / total, f"已完成 {done}/{total} 个数据块")
    return results
```

> **注意**：NASA POWER 自定义高度的风速参数命名规则需在 Phase 0 技术验证时确认，实际参数键名可能为 `WSC<h>M`（如 `WSC100M`）或通过响应体的 `properties.parameter` 键获取。

### 4.4 分析引擎（`services/analysis_engine.py`）

分析引擎接收合并后的 Pandas DataFrame，返回结构化结果字典，供 API 响应和 PDF 生成使用。

```python
class AnalysisEngine:
    def __init__(self, df: pd.DataFrame, heights: list[int]):
        self.df = df          # 列：timestamp, ws_<h>m, wd (for each height)
        self.heights = heights

    def run(self) -> AnalysisResult:
        return AnalysisResult(
            summary=self._summary(),
            basic_stats=self._basic_stats(),
            wind_rose=self._wind_rose(),
            weibull=self._weibull(),
            wpd=self._wpd(),
            shear=self._shear(),
            turbulence=self._turbulence(),
            extreme_wind=self._extreme_wind(),
            representative_year=self._representative_year(),
        )
```

---

## 5. 数据流设计

```
用户操作                前端                       后端                    NASA POWER
─────────         ──────────────────        ───────────────────        ──────────────
① 点击"开始分析"   POST /api/analysis/start  ──→  创建 task_id
                   接收 { task_id }               启动 BackgroundTask
                   建立 SSE 连接             ←──  推送进度事件 (SSE)
                                                  │
                                                  ├── 并行请求各年×各高度  ──→  NASA API
                                                  ├── 合并 DataFrame             ←──
                                                  ├── 数据预处理
                                                  ├── 调用 AnalysisEngine
                                                  └── 推送 { status: success }
                   ←── SSE: status=success
② 前端收到成功      GET /api/analysis/{id}/result
                   渲染图表和指标卡片
③ 生成报告          POST /api/report/generate
                   ←── PDF 二进制流（Content-Disposition: attachment）
```

---

## 6. API 接口规范

所有接口均以 `/api` 为前缀，返回 JSON（PDF 接口返回二进制流）。

### 6.1 启动分析任务

```
POST /api/analysis/start
Content-Type: application/json
```

**Request Body**

```json
{
  "lat": 39.9042,
  "lon": 116.4074,
  "heights": [80, 100, 120],
  "start_year": 2014,
  "end_year": 2024,
  "wind_surface": "vegtype_11",
  "filter_outliers": true,
  "project_name": "华北某风场预可研"
}
```

**参数校验规则**

| 参数           | 类型        | 校验规则                                  |
| -------------- | ----------- | ----------------------------------------- |
| `lat`          | float       | -90 ≤ lat ≤ 90                            |
| `lon`          | float       | -180 ≤ lon ≤ 180                          |
| `heights`      | list[int]   | 每个高度 10～300，最多 5 个               |
| `start_year`   | int         | 1981 ≤ start_year ≤ end_year              |
| `end_year`     | int         | start_year ≤ end_year ≤ 当前年 - 1       |
| `wind_surface` | str（enum） | 限制为 NASA POWER 支持的 alias 白名单     |

**Response 200**

```json
{
  "task_id": "a1b2c3d4-...",
  "estimated_seconds": 45
}
```

---

### 6.2 SSE 进度流

```
GET /api/analysis/{task_id}/progress
Accept: text/event-stream
```

**Event 格式**（每条 SSE 消息）

```
data: {"status": "running", "progress": 0.42, "message": "已完成 18/43 个数据块"}

data: {"status": "success", "progress": 1.0, "message": "分析完成"}

data: {"status": "error", "progress": 0.3, "message": "NASA POWER API 请求失败，请重试"}
```

当 `status` 为 `success` 或 `error` 时，前端关闭 EventSource 连接。

---

### 6.3 获取分析结果

```
GET /api/analysis/{task_id}/result
```

**Response 200**（结构摘要，完整定义见 §7.3）

```json
{
  "task_id": "a1b2c3d4-...",
  "meta": { "lat": 39.9, "lon": 116.4, "heights": [80, 100, 120], ... },
  "summary": { "mean_ws_100m": 6.8, "annual_wpd_100m": 312.4, "dominant_dir": "NNW", ... },
  "basic_stats": { ... },
  "wind_rose": { ... },
  "weibull": { ... },
  "wpd": { ... },
  "shear": { ... },
  "turbulence": { ... },
  "extreme_wind": { ... }
}
```

---

### 6.4 生成 PDF 报告

```
POST /api/report/generate
Content-Type: application/json
```

**Request Body**

```json
{
  "task_id": "a1b2c3d4-...",
  "project_name": "华北某风场预可研",
  "organization": "某能源开发有限公司",
  "confidentiality": "内部资料",
  "report_date": "2026-03-13"
}
```

**Response 200**

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="wind_report_20260313.pdf"
[binary stream]
```

**Response 404**

```json
{ "detail": "任务不存在或已过期（30分钟内有效）" }
```

---

### 6.5 错误响应格式

所有错误均返回统一结构：

```json
{
  "detail": "错误描述（人类可读）",
  "code": "ERROR_CODE_ENUM"
}
```

| code                      | HTTP 状态 | 含义                            |
| ------------------------- | --------- | ------------------------------- |
| `INVALID_PARAMS`          | 422       | 请求参数校验失败                |
| `NASA_API_UNAVAILABLE`    | 502       | NASA POWER API 不可用           |
| `TASK_NOT_FOUND`          | 404       | task_id 不存在或已过期          |
| `TASK_STILL_RUNNING`      | 409       | 尝试获取结果但任务未完成        |
| `ANALYSIS_FAILED`         | 500       | 分析过程中出现内部错误          |

---

## 7. 数据模型

### 7.1 请求模型（Pydantic）

```python
# models/request.py
from pydantic import BaseModel, field_validator
from typing import Literal

VALID_SURFACES = {
    "vegtype_1", "vegtype_2", "vegtype_3", "vegtype_4", "vegtype_5",
    "vegtype_6", "vegtype_7", "vegtype_8", "vegtype_9", "vegtype_10",
    "vegtype_11", "vegtype_12", "vegtype_20", "seaice",
    "openwater", "airportice", "airportgrass",
}

class AnalysisRequest(BaseModel):
    lat: float
    lon: float
    heights: list[int]
    start_year: int
    end_year: int
    wind_surface: str = "vegtype_11"
    filter_outliers: bool = True
    project_name: str = ""

    @field_validator("lat")
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("纬度范围 -90 ~ 90")
        return v

    @field_validator("lon")
    def validate_lon(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("经度范围 -180 ~ 180")
        return v

    @field_validator("heights")
    def validate_heights(cls, v):
        if not v or len(v) > 5:
            raise ValueError("高度列表需 1～5 个元素")
        for h in v:
            if not 10 <= h <= 300:
                raise ValueError(f"高度 {h} 超出 10～300 m 范围")
        return v

    @field_validator("wind_surface")
    def validate_surface(cls, v):
        if v not in VALID_SURFACES:
            raise ValueError(f"不支持的地表类型: {v}")
        return v
```

### 7.2 内部 DataFrame 结构

数据拉取完成后，所有高度合并为一张宽表 DataFrame：

| 列名               | 类型           | 说明                            |
| ------------------ | -------------- | ------------------------------- |
| `timestamp`        | datetime64[ns] | UTC 时间戳                      |
| `ws_{h}m`          | float64        | h 米高度风速（m/s），每个高度一列 |
| `wd`               | float64        | 风向（°，气象惯例，来风方向）   |
| `is_outlier_{h}m`  | bool           | 该时刻该高度是否被标记为异常值  |

### 7.3 分析结果响应模型

```python
# models/response.py（精简版）
class WeibullResult(BaseModel):
    k: float                  # 形状参数
    c: float                  # 尺度参数（m/s）
    r_squared: float          # 拟合优度
    bin_edges: list[float]    # 频率直方图分组边界
    bin_freq: list[float]     # 实测频率（%）
    fitted_pdf: list[float]   # Weibull 拟合 PDF 值

class WindRoseData(BaseModel):
    directions: list[str]     # 16 方位名称
    speed_bins: list[str]     # 风速区间标签
    data: list[list[float]]   # [方位][风速段] 的频率矩阵

class ExtremeWindResult(BaseModel):
    v50: float                # 50 年一遇风速（m/s）
    ci_lower: float           # 90% CI 下限
    ci_upper: float           # 90% CI 上限
    iec_class: str            # Ia / Ib / IIa / IIb / IIIa / IIIb / S
    annual_max_series: list[float]
    return_periods: list[float]
    return_wind_speeds: list[float]

class RepresentativeYearResult(BaseModel):
    representative_year: int          # 选取的代表年年份
    annual_mean_lt: float             # 长期年均风速（m/s）
    annual_mean_ry: float             # 代表年年均风速（m/s）
    deviation_pct: float              # 与长期均值偏差率（%）
    monthly_correlation: float        # 月际分布 Pearson 相关系数
    lt_monthly_means: list[float]     # 长期各月均风速（12 个值）
    ry_monthly_means: list[float]     # 代表年各月均风速（12 个值）
    years_ranking: list[dict]         # 所有候选年评分排名

class AnalysisResult(BaseModel):
    task_id: str
    meta: dict
    summary: dict
    basic_stats: dict
    wind_rose: dict[str, WindRoseData]  # key: str(height)
    weibull: dict[str, WeibullResult]
    wpd: dict
    shear: dict
    turbulence: dict
    extreme_wind: dict[str, ExtremeWindResult]
    representative_year: dict[str, RepresentativeYearResult]  # key: str(height)
```

---

## 8. 核心算法实现

### 8.1 Weibull MLE 拟合（`algorithms/weibull.py`）

采用 SciPy 的 `scipy.stats.weibull_min` 进行最大似然估计，初始值使用矩估计法提供。

```python
from scipy.stats import weibull_min
from scipy.optimize import minimize
import numpy as np

def fit_weibull(wind_speeds: np.ndarray) -> tuple[float, float, float]:
    """
    返回 (k, c, r_squared)
    注意：scipy weibull_min 参数为 (c=k, scale=c_scale, loc)
    """
    ws = wind_speeds[wind_speeds > 0]
    # 矩估计初始值
    mean_ws = ws.mean()
    std_ws = ws.std()
    k0 = (std_ws / mean_ws) ** -1.086

    shape, loc, scale = weibull_min.fit(ws, f0=k0, floc=0)
    k = shape
    c = scale  # Weibull 尺度参数

    # 计算 R²
    bin_edges = np.arange(0, ws.max() + 1, 0.5)
    observed, _ = np.histogram(ws, bins=bin_edges, density=True)
    expected = weibull_min.pdf(
        (bin_edges[:-1] + bin_edges[1:]) / 2, k, loc=0, scale=c
    )
    ss_res = np.sum((observed - expected) ** 2)
    ss_tot = np.sum((observed - observed.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return k, c, r_squared
```

### 8.2 极端风速（Gumbel 极值拟合，`algorithms/extreme_wind.py`）

```python
from scipy.stats import gumbel_r
import numpy as np

def fit_extreme_wind(annual_max: np.ndarray, return_period: int = 50) -> dict:
    """
    对年最大风速序列做 Gumbel I 型拟合，推算 50 年一遇风速。
    要求序列长度 ≥ 10 年。
    """
    loc, scale = gumbel_r.fit(annual_max)
    p_exceedance = 1 - 1 / return_period
    v50 = gumbel_r.ppf(p_exceedance, loc=loc, scale=scale)

    # 90% 置信区间（Delta 法近似）
    n = len(annual_max)
    se = scale * np.sqrt((1.1087 + 0.5140 * (return_period - 1) ** 2) / n)
    ci_lower = v50 - 1.645 * se
    ci_upper = v50 + 1.645 * se

    # IEC 61400-1 等级判定（基于 V50）
    iec_class = _iec_class(v50)

    return {"v50": v50, "ci_lower": ci_lower, "ci_upper": ci_upper, "iec_class": iec_class}

def _iec_class(v50: float) -> str:
    # IEC 61400-1 Ed.4: Vref = V50
    if v50 >= 50:  return "Ia/Ib"
    if v50 >= 42.5: return "IIa/IIb"
    if v50 >= 37.5: return "IIIa/IIIb"
    return "S（特殊级，需专项论证）"
```

### 8.3 湍流强度（`algorithms/turbulence.py`）

```python
import numpy as np
import pandas as pd

def compute_ti(df: pd.DataFrame, ws_col: str, bin_size: float = 1.0) -> dict:
    """
    以 bin_size（默认 1 m/s）分组统计 TI。
    TI = std(ws) / mean(ws)，在每个风速区间内计算。
    """
    df = df[df[ws_col] > 0].copy()
    df["ws_bin"] = (df[ws_col] // bin_size) * bin_size + bin_size / 2

    ti_by_bin = df.groupby("ws_bin")[ws_col].agg(["mean", "std"]).reset_index()
    ti_by_bin["ti"] = ti_by_bin["std"] / ti_by_bin["mean"]

    # IEC 61400-1 Ed.4 参考 TI：Iref = 0.16 (Class A), 0.14 (B), 0.12 (C)
    bins = ti_by_bin["ws_bin"].tolist()
    iec_a = [0.16 * (0.75 + 5.6 / v) for v in bins]  # 特征湍流强度公式

    return {
        "ws_bins": bins,
        "ti_values": ti_by_bin["ti"].tolist(),
        "iec_class_a": iec_a,
    }
```

### 8.4 风切变回归（`algorithms/shear.py`）

```python
import numpy as np
from scipy.optimize import curve_fit

def fit_shear_exponent(heights: list[int], mean_ws_by_height: list[float]) -> float:
    """
    对多高度年均风速做幂律回归，拟合等效 alpha_fit。
    V(h) = V_ref * (h / h_ref)^alpha
    取第一个高度为参考高度。
    """
    h_arr = np.array(heights, dtype=float)
    v_arr = np.array(mean_ws_by_height, dtype=float)
    h_ref, v_ref = h_arr[0], v_arr[0]

    def power_law(h, alpha):
        return v_ref * (h / h_ref) ** alpha

    popt, _ = curve_fit(power_law, h_arr, v_arr, p0=[0.143], bounds=(0.01, 1.0))
    return float(popt[0])
```

### 8.5 风功率密度（WPD）

```python
def compute_wpd(ws_array: np.ndarray, rho: float = 1.225) -> float:
    """年均 WPD = 0.5 * rho * mean(v^3)，单位 W/m²"""
    return 0.5 * rho * np.mean(ws_array ** 3)

def iec_wind_class(annual_wpd: float) -> str:
    """基于 WPD 判定 IEC 风电场等级（参考 IEC 61400-1）"""
    if annual_wpd >= 500: return "I 类（高风速）"
    if annual_wpd >= 300: return "II 类（中等风速）"
    if annual_wpd >= 150: return "III 类（低风速）"
    return "S 类（特殊，需专项设计）"
```

### 8.6 代表年选取（`algorithms/representative_year.py`）

从多年逐小时数据中筛选统计特性最接近长期平均的单一年份，作为风机发电量计算或进一步精细化分析的基准数据集。

**评分方法**：综合两项指标，得分越低越优：

| 指标               | 权重 | 计算方式                                              |
| ------------------ | ---- | ----------------------------------------------------- |
| 年均风速偏差率     | 60%  | `|V_year - V_lt| / V_lt`，归一化后乘以 0.6            |
| 月际分布相关性     | 40%  | Pearson r（候选年月均 vs 长期月均），`(1 - r) × 0.4` |

```python
# algorithms/representative_year.py
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

def select_representative_year(
    df: pd.DataFrame,
    ws_col: str,
) -> dict:
    """
    从多年逐小时 DataFrame 中选取代表年。
    df 必须包含 'timestamp'（datetime64）和 ws_col 列。
    """
    df = df.copy()
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month

    lt_monthly = df.groupby("month")[ws_col].mean()        # 长期月均
    lt_annual_mean = float(df[ws_col].mean())               # 长期年均

    years = sorted(df["year"].unique())
    records = []

    for year in years:
        ydf = df[df["year"] == year]
        year_mean = float(ydf[ws_col].mean())
        year_monthly = ydf.groupby("month")[ws_col].mean().reindex(
            range(1, 13), fill_value=np.nan
        )

        # 年均偏差率
        mean_dev = abs(year_mean - lt_annual_mean) / lt_annual_mean * 100

        # 月际 Pearson 相关（有效月份 ≥ 6）
        valid = ~(year_monthly.isna() | lt_monthly.isna())
        if valid.sum() >= 6:
            r, _ = pearsonr(year_monthly[valid], lt_monthly[valid])
        else:
            r = 0.0

        records.append({
            "year": int(year),
            "annual_mean": year_mean,
            "mean_deviation_pct": mean_dev,
            "monthly_correlation": float(r),
            "monthly_means": year_monthly.fillna(0).tolist(),
        })

    scores_df = pd.DataFrame(records)

    # 归一化年均偏差率，避免除零
    max_dev = scores_df["mean_deviation_pct"].max()
    scores_df["dev_norm"] = (
        scores_df["mean_deviation_pct"] / max_dev if max_dev > 0 else 0.0
    )
    scores_df["score"] = (
        0.6 * scores_df["dev_norm"]
        + 0.4 * (1 - scores_df["monthly_correlation"])
    )

    best = scores_df.loc[scores_df["score"].idxmin()]

    return {
        "representative_year": int(best["year"]),
        "annual_mean_lt": lt_annual_mean,
        "annual_mean_ry": float(best["annual_mean"]),
        "deviation_pct": float(best["mean_deviation_pct"]),
        "monthly_correlation": float(best["monthly_correlation"]),
        "lt_monthly_means": lt_monthly.tolist(),
        "ry_monthly_means": best["monthly_means"],
        "years_ranking": scores_df[
            ["year", "annual_mean", "mean_deviation_pct", "monthly_correlation", "score"]
        ].sort_values("score").to_dict("records"),
    }
```

> **注意**：代表年分析对**每个分析高度**独立执行，因不同高度的风速序列可能导致不同年份被选为代表年；响应模型中以高度为键返回各高度的代表年结果。

---

## 9. PDF 报告生成

### 9.1 技术方案

使用 **WeasyPrint** 将 Jinja2 渲染的 HTML 模板转换为 PDF。图表以 **ECharts 服务端渲染** 或 **前端传递 Base64 PNG** 方式嵌入。

**推荐方案（MVP）**：前端在完成分析后，将各图表通过 ECharts `getDataURL()` 导出为 Base64 PNG，随 `POST /api/report/generate` 请求体一并发送，后端将图片嵌入 HTML 模板后调用 WeasyPrint。

```
前端 ECharts.getDataURL() → Base64 PNG
↓
POST /api/report/generate { task_id, chart_images: { wind_rose: "data:image/png;base64,..." }, ... }
↓
后端 Jinja2 渲染 HTML（<img src="data:image/png;base64,...">）
↓
WeasyPrint.HTML(string=html).write_pdf()
↓
返回 PDF 二进制流
```

### 9.2 模板结构（`templates/report_base.html`）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="report_style.css">
  <title>{{ project_name }} 风资源评估报告</title>
</head>
<body>
  <!-- 封面 -->
  <div class="cover page-break-after">
    <div class="cover-title">{{ project_name }}</div>
    <div class="cover-subtitle">虚拟测风塔风资源评估报告</div>
    <table class="cover-meta">
      <tr><td>坐标</td><td>{{ lat }}°N, {{ lon }}°E</td></tr>
      <tr><td>分析时段</td><td>{{ start_year }} — {{ end_year }}</td></tr>
      <tr><td>分析高度</td><td>{{ heights | join(', ') }} m</td></tr>
      <tr><td>编制单位</td><td>{{ organization }}</td></tr>
      <tr><td>报告日期</td><td>{{ report_date }}</td></tr>
      <tr><td>密级</td><td>{{ confidentiality }}</td></tr>
    </table>
  </div>

  <!-- 各章节通过 Jinja2 include 引入 -->
  {% include "sections/01_overview.html" %}
  {% include "sections/02_basic_stats.html" %}
  {% include "sections/03_wind_rose.html" %}
  {% include "sections/04_weibull.html" %}
  {% include "sections/05_wpd.html" %}
  {% include "sections/06_shear.html" %}
  {% include "sections/07_turbulence.html" %}
  {% include "sections/08_extreme_wind.html" %}
  {% include "sections/09_representative_year.html" %}
  {% include "sections/10_conclusion.html" %}
</body>
</html>
```

### 9.3 CSS 分页控制

```css
/* report_style.css */
@page {
  size: A4;
  margin: 2.5cm;
  @bottom-right { content: counter(page) " / " counter(pages); }
}
.page-break-after { page-break-after: always; }
h2 { page-break-before: always; }
img.chart { width: 100%; max-height: 10cm; }
```

---

## 10. 部署与运维

### 10.1 Docker Compose 配置

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MAPBOX_TOKEN=${MAPBOX_TOKEN}
      - CORS_ORIGINS=http://localhost
      - TASK_TIMEOUT_SECONDS=300
      - CACHE_TTL_SECONDS=1800
    restart: unless-stopped

networks:
  default:
    name: wind-insights-net
```

### 10.2 前端 Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**nginx.conf** — 将 `/api` 反向代理到后端，其余请求返回 `index.html`：

```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;

  location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_read_timeout 300s;
    # SSE 必要配置
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection "";
    chunked_transfer_encoding on;
  }

  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

### 10.3 后端 Dockerfile

使用 `uv` 代替 `pip` 安装依赖，利用其构建缓存层提升镜像重建速度。

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app

# 安装系统依赖（WeasyPrint 所需）
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangoft2-1.0-0 libffi-dev \
    fontconfig fonts-noto-cjk curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 先复制依赖声明文件，利用 Docker layer 缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 10.4 后端 `pyproject.toml`（uv 项目配置）

```toml
[project]
name = "wind-insights-backend"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "httpx>=0.27",
    "pandas>=2.2",
    "numpy>=1.26",
    "scipy>=1.13",
    "weasyprint>=62",
    "jinja2>=3.1",
    "pydantic>=2.7",
    "python-multipart>=0.0.9",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8",
    "httpx>=0.27",  # 用于 FastAPI TestClient
]
```

**常用 uv 命令**

```bash
# 初始化项目（首次）
uv init --no-workspace

# 添加依赖
uv add fastapi uvicorn httpx pandas numpy scipy weasyprint

# 同步安装所有依赖（生产）
uv sync --frozen

# 运行开发服务器
uv run uvicorn app.main:app --reload
```

### 10.5 环境变量（`.env.example`）

```env
# Mapbox（前端构建时注入）
VITE_MAPBOX_TOKEN=pk.xxxxx

# 后端
CORS_ORIGINS=http://localhost
TASK_TIMEOUT_SECONDS=300
CACHE_TTL_SECONDS=1800
```

---

## 11. 性能策略

### 11.1 NASA POWER API 并行请求

单次分析（10 年 × 3 高度 = 30 个请求）使用 `asyncio.as_completed` 并发执行，理论完成时间约为单次请求时间（约 3～5 秒）× 并发调度开销，预计 15～25 秒内完成所有数据拉取。

NASA POWER API 默认无显式速率限制文档，但建议控制**并发连接数 ≤ 10**，避免触发服务端限流。可在 `httpx.AsyncClient` 中设置：

```python
limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
async with httpx.AsyncClient(limits=limits) as client:
    ...
```

### 11.2 结果缓存

以 `(lat_grid, lon_grid, heights_tuple, start_year, end_year, wind_surface)` 为缓存键，将分析结果存入内存 dict，TTL 30 分钟。相同参数的重复请求直接命中缓存，跳过数据拉取与分析。

```python
# core/cache.py
from datetime import datetime, timedelta
from threading import Lock

class AnalysisCache:
    def __init__(self, ttl_seconds: int = 1800):
        self._store: dict[str, tuple[datetime, dict]] = {}
        self._lock = Lock()
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> dict | None:
        with self._lock:
            entry = self._store.get(key)
            if entry and datetime.utcnow() - entry[0] < self._ttl:
                return entry[1]
        return None

    def set(self, key: str, value: dict):
        with self._lock:
            self._store[key] = (datetime.utcnow(), value)
```

### 11.3 前端图表渲染优化

- 详细分析页（Step 5）采用**懒渲染**：切换到某分析模块时才初始化 ECharts 实例
- 大数据集（10 年逐小时 ~ 87,600 条）的频率直方图、持续曲线等在后端预计算分组，前端只接收聚合数据，避免前端 JS 处理原始 8 万条记录

---

## 12. 安全策略

### 12.1 输入校验

所有后端接口使用 Pydantic v2 强类型校验，拒绝任何未声明字段（`model_config = ConfigDict(extra="forbid")`）。坐标范围、年份范围、高度范围均做服务端边界校验（详见 §7.1），前端校验仅作 UX 辅助，不作为安全依据。

### 12.2 NASA POWER API 代理安全

后端作为代理，仅转发白名单内的参数，不将用户原始输入直接拼接到外部 URL：

```python
# 构建参数时使用显式的 dict，而非 **user_input
params = {
    "latitude": validated_lat,       # 已经过 Pydantic 校验的值
    "longitude": validated_lon,
    "wind-elevation": validated_height,
    "wind-surface": validated_surface,
    ...
}
```

### 12.3 SSE 端点防滥用

- 每个 `task_id` 的 SSE 连接最多保持 300 秒（任务超时时间），超时后服务端主动关闭
- 对同一 IP 的并发 SSE 连接数限制（Nginx 层 `limit_conn`）

### 12.4 CORS

CORS 白名单通过环境变量 `CORS_ORIGINS` 配置，生产环境限定为前端域名，不使用 `*` 通配符。

### 12.5 依赖安全

- Python 依赖通过 `pip-audit` 在 CI 阶段扫描已知 CVE
- Dockerfile 使用官方 slim 镜像，减少攻击面
- WeasyPrint 渲染的 HTML 内容完全由后端模板生成，不包含用户输入的 HTML（仅插入文本节点），防止 HTML 注入

---

*本文档与 [PRD.md](./PRD.md) 配套使用，技术实现细节如有调整请同步更新版本号。*
