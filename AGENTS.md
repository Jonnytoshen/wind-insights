# AGENTS.md — Wind Insights 开发 Agent 指令文件

> 本文件是面向 AI 编程助手（Copilot Agent、Cursor 等）的项目级指令文件。
> 所有代码生成、修改、重构操作均需遵守本文件的规范。
> 详细需求见 [docs/PRD.md](docs/PRD.md)，详细技术设计见 [docs/TDD.md](docs/TDD.md)。

---

## 目录

1. [项目概述](#1-项目概述)
2. [项目结构](#2-项目结构)
3. [开发规范](#3-开发规范)
4. [代码风格](#4-代码风格)
5. [Vue 最佳实践](#5-vue-最佳实践)
6. [FastAPI 最佳实践](#6-fastapi-最佳实践)
7. [测试要求](#7-测试要求)
8. [注意事项](#8-注意事项)

---

## 1. 项目概述

**Wind Insights** 是一款面向风电行业的在线虚拟测风塔分析平台。用户通过向导式（Wizard）流程，在地图上选定候选点位，系统自动调用 **NASA POWER API** 获取 MERRA-2 逐小时再分析风速数据，完成多维度风资源评估，并一键生成符合行业规范的 PDF 分析报告。

### 1.1 核心功能模块

| 模块 | 描述 |
|------|------|
| F1 向导框架 | 6 步 Wizard 流程（选点 → 参数 → 加载 → 总览 → 详析 → 报告） |
| F2 地图选点 | Mapbox GL JS 地图，支持点击选点与坐标直接输入 |
| F3 参数配置 | 分析高度（10～300 m）、时间范围、地表类型等 |
| F4 数据引擎 | 后端代理 NASA POWER API，并行拉取，SSE 实时进度推送 |
| F5 分析可视化 | 基础统计、玫瑰图、Weibull、WPD、风切变、TI、极端风速、代表年 |
| F6 多高度对比 | ≥2 高度时自动启用对比视图 |
| F7 PDF 报告 | WeasyPrint 生成 A4 专业报告，前端 ECharts 图表以 Base64 PNG 嵌入 |

### 1.2 技术栈速览

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | Vue ≥ 3.4 |
| 构建工具 | Vite | ≥ 5.0 |
| 前端包管理 | pnpm | ≥ 9.0 |
| CSS 框架 | Tailwind CSS 4 | ≥ 4.0 |
| UI 组件库 | shadcn-vue | 最新 |
| 地图 | Mapbox GL JS | ≥ 3.0 |
| 图表 | Apache ECharts 5 | ≥ 5.5 |
| 状态管理 | Pinia | ≥ 2.1 |
| 后端框架 | FastAPI | ≥ 0.111 |
| Python 版本 | Python | 3.12 |
| Python 包管理 | uv | 最新 |
| 数据处理 | Pandas 2 + NumPy + SciPy | — |
| PDF 生成 | WeasyPrint | ≥ 62 |
| 容器化 | Docker + Docker Compose | — |

---

## 2. 项目结构

生成或修改代码时，**严格遵守以下目录约定**，不得在规划目录之外随意创建文件：

```
wind-insights/
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   └── main.css               # Tailwind CSS 4 唯一入口，只写 @import "tailwindcss" 和 @theme
│   │   ├── components/
│   │   │   ├── map/                   # 地图相关组件
│   │   │   ├── charts/                # ECharts 图表组件（每个图表一个 .vue + 一个 .ts option 工厂）
│   │   │   └── wizard/                # Wizard 步骤子组件
│   │   ├── views/                     # 页面级组件（Step1～Step6）
│   │   ├── stores/                    # Pinia stores（wizard.ts / analysis.ts / history.ts）
│   │   ├── composables/               # 组合式函数（useSSE.ts / useAnalysis.ts）
│   │   ├── api/                       # Axios 请求封装（index.ts）
│   │   ├── types/                     # TypeScript 类型定义（analysis.ts）
│   │   ├── utils/                     # 工具函数（geoUtils.ts 等）
│   │   └── router/
│   ├── vite.config.ts
│   └── pnpm-lock.yaml                 # 必须提交到版本控制
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/                   # analysis.py / report.py
│   │   ├── services/                  # nasa_power.py / analysis_engine.py / pdf_generator.py
│   │   ├── models/                    # request.py / response.py（Pydantic 模型）
│   │   ├── core/                      # cache.py / task_manager.py / validators.py
│   │   └── algorithms/                # weibull.py / extreme_wind.py / turbulence.py / shear.py / representative_year.py
│   ├── templates/                     # WeasyPrint Jinja2 HTML 模板
│   ├── pyproject.toml                 # uv 项目配置
│   └── uv.lock                        # 必须提交到版本控制
│
├── docs/
│   ├── PRD.md
│   └── TDD.md
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 3. 开发规范

### 3.1 通用原则

- **最小化改动**：只修改与任务直接相关的代码，不做无关重构或"顺手优化"。
- **类型安全优先**：前端所有变量、函数参数、返回值均须有明确的 TypeScript 类型；后端所有接口参数和返回值均须通过 Pydantic 模型约束。
- **安全性第一**：任何涉及外部输入的处理，都必须在服务端做校验（前端校验仅为 UX 辅助）。
- **不引入未列出的依赖**：未在 TDD 技术栈中出现的库，须在引入前明确说明必要性。

### 3.2 前端开发规范

#### 依赖管理

- 使用 `pnpm` 管理所有前端依赖，**禁止使用 npm 或 yarn**。
- 安装依赖命令：`pnpm add <pkg>`；开发依赖：`pnpm add -D <pkg>`。
- `pnpm-lock.yaml` 必须提交。

#### Tailwind CSS 4 使用规范

- **无 `tailwind.config.js`**：Tailwind CSS 4 采用 CSS-first 配置，通过 `@tailwindcss/vite` Vite 插件驱动。
- 全局样式唯一入口为 `src/assets/main.css`，内容仅允许：
  ```css
  @import "tailwindcss";

  @theme {
    /* 自定义令牌，如品牌色、字体 */
  }

  @layer base {
    /* shadcn-vue CSS 变量 */
  }
  ```
- **禁止**直接写裸 CSS 类，统一使用 Tailwind 工具类；如需过渡动画等复杂样式，在 `@layer utilities` 中声明。

#### 状态管理

- 全局状态只能存放在 `src/stores/` 的 Pinia store 中，**禁止**在组件内用 `provide/inject` 替代全局 store。
- Pinia store 使用 **Setup Store** 风格（`defineStore(id, () => { ... })`），而非 Options Store 风格。
- Wizard 流程唯一状态源为 `stores/wizard.ts`，各步骤组件通过 `storeToRefs` 解构响应式状态。
- 历史记录持久化到 `localStorage`，键名固定为 `wind_insights_history`，最多保存 20 条。

#### HTTP 与 SSE

- 所有后端请求通过 `src/api/index.ts` 的 Axios 封装发出，**禁止**在组件中直接调用 `axios` 或 `fetch`。
- SSE 连接封装在 `composables/useSSE.ts` 中，使用浏览器原生 `EventSource`。
- SSE 状态为 `success` 或 `error` 时必须调用 `source.close()` 关闭连接。

### 3.3 后端开发规范

#### 依赖管理

- 使用 `uv` 管理所有 Python 依赖，**禁止使用 pip 直接安装**。
- 新增依赖：`uv add <pkg>`；开发依赖：`uv add --dev <pkg>`。
- `uv.lock` 必须提交；Dockerfile 中使用 `uv sync --frozen --no-dev`。
- 开发服务器启动：`uv run uvicorn app.main:app --reload`。

#### 路由与中间件

- 所有路由注册在对应的 `routers/` 模块中，**禁止**在 `main.py` 中直接写路由函数。
- `main.py` 仅负责应用初始化、中间件注册和路由挂载。
- CORS 来源必须通过环境变量 `CORS_ORIGINS` 注入，**禁止**硬编码为 `*`。

#### 异步任务

- 分析任务通过 FastAPI `BackgroundTasks` 启动，任务状态存储在 `core/task_manager.py` 的内存 dict 中。
- 单个任务超过 300 秒（`TASK_TIMEOUT_SECONDS`）自动标记为 `error`。
- NASA POWER API 请求使用 `httpx.AsyncClient`，并发连接数限制 ≤ 10：
  ```python
  limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
  ```

#### 错误处理

- 所有 HTTP 错误须返回统一的错误结构：`{"detail": "...", "code": "ERROR_CODE_ENUM"}`。
- 支持的错误码见 TDD §6.5。外部 API 失败时返回 502（`NASA_API_UNAVAILABLE`），禁止将原始异常栈直接暴露给客户端。

---

## 4. 代码风格

### 4.1 TypeScript / Vue

- 缩进：**2 个空格**。
- 引号：字符串使用**单引号**（模板字面量除外）。
- 分号：**不加分号**（ASI 风格）。
- 组件文件名：**PascalCase**（如 `WindRoseChart.vue`）。
- 类型文件：接口名以 `I` 开头（如 `IAnalysisResult`）；类型别名以大驼峰命名。
- 禁止使用 `any`；必须推断不出类型时，使用 `unknown` 并做类型守卫。
- Vue 组件必须使用 `<script setup lang="ts">` 语法，禁止 Options API。
- `defineProps` 和 `defineEmits` 必须使用泛型形式提供类型：
  ```ts
  const props = defineProps<{ data: IWindRoseData; height: number }>()
  const emit = defineEmits<{ (e: 'update', value: number): void }>()
  ```

### 4.2 Python

- 遵循 **PEP 8**，单行最大 100 字符。
- 缩进：**4 个空格**。
- 函数和变量命名：`snake_case`；类命名：`PascalCase`；常量：`UPPER_SNAKE_CASE`。
- 所有公共函数必须有类型注解（参数和返回值）。
- 使用 `from __future__ import annotations` 支持 PEP 604 联合类型语法（`X | Y`）。
- Pydantic 模型必须设置 `model_config = ConfigDict(extra="forbid")`，拒绝未声明字段。
- 算法函数（`algorithms/` 目录）必须是**纯函数**，无副作用，便于单元测试。

### 4.3 提交规范

提交信息遵循 **Conventional Commits**：

```
feat(wizard): 添加步骤3数据加载进度条
fix(api): 修复NASA POWER API重试逻辑
refactor(charts): 提取ECharts配置工厂函数
test(weibull): 添加MLE拟合边界用例
docs: 更新AGENTS.md开发规范
```

---

## 5. Vue 最佳实践

### 5.1 组件设计

- **单一职责**：每个组件只负责一件事。图表组件只负责渲染，数据获取在 composable 或 store 中处理。
- **Props 向下，Events 向上**：子组件通过 props 接收数据，通过 emit 通知父组件，禁止子组件直接修改 props。
- **图表组件规范**：
  - 所有 ECharts 图表封装为独立 `.vue` 组件，放在 `components/charts/`。
  - ECharts option 配置提取到同名 `.ts` 工厂函数文件（如 `windRoseOption.ts`），便于 PDF 生成时复用。
  - 使用 `ResizeObserver` 响应容器尺寸变化，组件卸载时必须销毁 ECharts 实例（`chart.dispose()`）。
  - 切换到某分析模块时才初始化 ECharts 实例（懒渲染），避免 Step 5 一次性初始化所有图表。

### 5.2 Pinia Store

- Setup Store 风格示例：
  ```ts
  // stores/wizard.ts
  export const useWizardStore = defineStore('wizard', () => {
    const currentStep = ref(0)
    const location = ref<ILocation | null>(null)
    // ...
    function nextStep() { currentStep.value++ }
    return { currentStep, location, nextStep }
  })
  ```
- 跨 store 引用时直接在 setup 函数内调用另一个 store，不通过 `$patch` 或全局事件。

### 5.3 Composables

- 命名以 `use` 开头（如 `useSSE`、`useAnalysis`）。
- 必须在 `onUnmounted` 中清理副作用（关闭 SSE 连接、取消 Axios 请求、销毁图表实例等）。
- `useSSE` 实现要点：
  ```ts
  export function useSSE(taskId: Ref<string | null>) {
    const progress = ref<IProgressInfo | null>(null)
    let source: EventSource | null = null

    watch(taskId, (id) => {
      source?.close()
      if (!id) return
      source = new EventSource(`/api/analysis/${id}/progress`)
      source.onmessage = (e) => {
        progress.value = JSON.parse(e.data)
        if (['success', 'error'].includes(progress.value?.status ?? '')) {
          source?.close()
        }
      }
    })

    onUnmounted(() => source?.close())
    return { progress }
  }
  ```

### 5.4 地图（Mapbox GL JS）

- Mapbox 实例在 `onMounted` 中初始化，在 `onUnmounted` 中调用 `map.remove()`。
- MERRA-2 网格计算逻辑独立在 `utils/geoUtils.ts` 的 `snapToMerra2Grid()` 函数中，不写在组件内：
  ```ts
  export function snapToMerra2Grid(lng: number, lat: number) {
    const latGrid = Math.round(lat / 0.5) * 0.5
    const lngGrid = Math.round(lng / 0.625) * 0.625
    return { lat: latGrid, lng: lngGrid }
  }
  ```
- Mapbox Token 通过 `import.meta.env.VITE_MAPBOX_TOKEN` 注入，**禁止**硬编码在代码中。

### 5.5 路由

- Wizard 步骤**不使用 Vue Router 独立路由**，由 `stores/wizard.ts` 的 `currentStep` 控制显示哪个步骤组件。
- 路由仅有两个：`/`（主应用）和 `/preview`（PDF 预览，可选）。

### 5.6 LocalStorage 持久化

- 历史记录的读写封装在 `stores/history.ts` 中，不在组件内直接操作 `localStorage`。
- Wizard 已完成步骤的状态通过 Pinia 插件（`pinia-plugin-persistedstate` 或手动序列化）持久化，页面刷新后可恢复。

---

## 6. FastAPI 最佳实践

### 6.1 路由设计

- 路由函数保持**薄**（thin router）：参数解析、业务逻辑分别委托给 Pydantic 模型和 service 层，路由函数本身只做协调。
- 所有路由函数声明为 `async def`，即使当前无异步操作，也为后续扩展保留。
- 使用 `APIRouter` 按模块拆分路由，通过 `app.include_router()` 注册，统一 `prefix="/api/..."`.

### 6.2 Pydantic 数据模型

- 请求模型放在 `models/request.py`，响应模型放在 `models/response.py`。
- 所有模型设置 `model_config = ConfigDict(extra="forbid")` 防止多余字段注入。
- 输入校验使用 `@field_validator`，在 validator 内只做约束，不做业务逻辑。
- 枚举类型（如 `wind_surface`）优先使用 `Literal` 类型注解或 `Enum`，而非 `str` 加运行时判断。

### 6.3 异步与并发

- I/O 密集型操作（HTTP 请求、文件写入）必须使用 `async/await`。
- CPU 密集型操作（SciPy 计算、Pandas 大批量处理）放在 `BackgroundTask` 中，若计算量很大可用 `asyncio.get_event_loop().run_in_executor` 转移到线程池，避免阻塞事件循环。
- `httpx.AsyncClient` 实例通过上下文管理器（`async with`）使用，不在模块级别创建全局实例。

### 6.4 SSE 端点

- SSE 响应使用 FastAPI 的 `StreamingResponse`，`media_type="text/event-stream"`。
- 必须设置响应头 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no`（配合 Nginx 关闭缓冲）。
- 每个任务使用独立的 `asyncio.Queue` 传递进度消息，避免任务间数据污染。
- 任务完成或超时后，服务端主动关闭 SSE 连接。

### 6.5 缓存

- 缓存键为 `(lat_grid, lon_grid, heights_tuple, start_year, end_year, wind_surface)` 的元组哈希，坐标先经 `snapToMerra2Grid()` 归一化后再生成键。
- 缓存操作必须加锁（`threading.Lock`），防止并发写入导致竞态条件。
- TTL 通过环境变量 `CACHE_TTL_SECONDS`（默认 1800）配置。

### 6.6 NASA POWER API 代理

- 构建请求参数时使用**显式 dict**，从 Pydantic 已校验的字段中赋值，**禁止** `**user_input` 直接展开用户原始输入：
  ```python
  params = {
      "latitude": req.lat,          # 已通过 Pydantic 校验
      "longitude": req.lon,
      "wind-elevation": height,
      "wind-surface": req.wind_surface,
      "start": f"{year}0101",
      "end": f"{year}1231",
      "parameters": "WS,WD50M",
      "community": "RE",
      "time-standard": "UTC",
      "format": "JSON",
  }
  ```
- 指数退避重试，最多 3 次，退避时间 `2^attempt` 秒。
- 失败时抛出自定义异常，由路由层捕获后返回统一错误格式（502）。

### 6.7 PDF 生成

- 前端在 Step 6 点击"生成 PDF"时，调用各 ECharts 实例的 `getDataURL({ type: 'png', pixelRatio: 2 })` 收集图表图片，作为 `chart_images` 字典随请求发送给后端。
- 后端使用 Jinja2 渲染 HTML 模板时，仅插入**文本节点**（`{{ value | e }}`），**禁止**插入用户可控的原始 HTML，防止 HTML 注入。
- WeasyPrint 渲染调用：`weasyprint.HTML(string=rendered_html, base_url=template_dir).write_pdf()`。
- PDF 以 `StreamingResponse` 返回，设置 `Content-Disposition: attachment; filename="..."`.

### 6.8 环境变量与配置

- 所有可变配置通过 `config.py` 统一管理，使用 `pydantic-settings` 或 `os.environ.get` 读取：
  ```python
  # config.py
  import os
  CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "http://localhost").split(",")
  TASK_TIMEOUT_SECONDS: int = int(os.environ.get("TASK_TIMEOUT_SECONDS", "300"))
  CACHE_TTL_SECONDS: int = int(os.environ.get("CACHE_TTL_SECONDS", "1800"))
  ```
- 敏感配置（Token、密钥）**只能**通过环境变量注入，不得出现在代码库中。
- 参考 `.env.example` 文件中的变量定义。

---

## 7. 测试要求

### 7.1 前端测试

- 框架：**Vitest**（已随 Vite 生态集成）。
- 工具函数（`utils/`）和纯逻辑 composables 必须有单元测试。
- ECharts option 工厂函数（`.ts`）必须覆盖核心数据输入的快照测试。
- 组件测试使用 **Vue Test Utils**，重点测试：
  - `WizardShell`：步骤前进/后退逻辑。
  - `Step2Params`：参数边界校验（高度范围 10～300 m，时间范围等）。
  - `useSSE`：SSE 消息解析与连接关闭逻辑。

### 7.2 后端测试

- 框架：**pytest**（Async 测试使用 `pytest-asyncio`）。
- 测试文件放在 `backend/tests/` 目录，与 `app/` 目录并列。
- **算法模块**（`algorithms/`）必须 100% 单元测试覆盖，包含：
  - `weibull.py`：已知风速序列的 k、c 参数误差 < 5%；全零序列不崩溃。
  - `extreme_wind.py`：已知年最大值序列的 V50 结果校验；序列长度 < 10 时给出明确错误。
  - `turbulence.py`：各风速分组 TI 值正确；空 DataFrame 不崩溃。
  - `shear.py`：幂律回归拟合结果在合理 α 范围内（0.01～1.0）。
  - `representative_year.py`：代表年年份在输入数据的年份范围内；单年数据边界情况。
- **API 端点**测试使用 FastAPI 的 `TestClient` 或 `httpx.AsyncClient`：
  - `POST /api/analysis/start`：合法参数返回 200；越界坐标返回 422；非法 `wind_surface` 返回 422。
  - `GET /api/analysis/{task_id}/result`：不存在的 task_id 返回 404；任务仍在进行时返回 409。
  - `POST /api/report/generate`：任务过期返回 404；成功时返回 PDF 二进制流。
- **NASA POWER API 代理**测试使用 `pytest-mock` 或 `respx` Mock 外部 HTTP 请求，不在测试中发起真实网络请求。

### 7.3 性能测试目标（非自动化，手工验收）

| 场景 | 目标 |
|------|------|
| 单点 10 年数据完整分析（2 高度） | ≤ 60 秒 |
| 单点 20 年数据完整分析 | ≤ 120 秒 |
| PDF 报告生成 | ≤ 30 秒 |
| 地图交互响应 | ≤ 200 ms |

---

## 8. 注意事项

### 8.1 安全红线

以下行为**绝对禁止**，出现即为重大缺陷：

1. **不校验坐标范围**：必须在 Pydantic validator 中校验 lat ∈ [-90, 90]、lon ∈ [-180, 180]。
2. **直接拼接用户输入到外部 URL 或 SQL**：NASA POWER API 请求参数必须使用显式白名单 dict 构建。
3. **在 HTML 模板中插入用户原始 HTML**：Jinja2 必须用 `{{ value | e }}` 转义，防止 HTML 注入。
4. **CORS 使用通配符 `*`**：生产环境 CORS 来源必须白名单化。
5. **硬编码 Mapbox Token 或其他密钥**：所有敏感信息只能从环境变量读取。

### 8.2 NASA POWER API 注意事项

- Phase 0 技术验证时须确认自定义高度风速的参数键名（可能为 `WSC<h>M`，如 `WSC100M`），实际结果以 API 响应体中的 `properties.parameter` 键为准，不得硬编码假设的键名。
- 高度范围限制为 **10～300 m**，超出此范围 API 不支持，前后端均须校验。
- 风向参数：≤50 m 的高度使用 `WD10M`，>50 m 的高度使用 `WD50M`（API 无独立自定义高度风向参数）。
- 每次请求最多跨 366 天，长序列须**按年分段并行**请求后合并。
- 建议控制并发连接数 ≤ 10，避免触发服务端限流。

### 8.3 数据处理注意事项

- 异常值检测默认开启（3σ 法），结果中标记 `is_outlier_{h}m` 列，计算统计量时排除异常值，但在报告中注明缺失/异常率。
- 代表年分析对**每个分析高度独立执行**，不同高度可能选出不同的代表年。
- Weibull 拟合前过滤风速 ≤ 0 的记录；极端风速分析要求年最大值序列长度 ≥ 10 年，否则给出明确警告，而非直接崩溃。
- 风功率密度计算使用 `0.5 * ρ * mean(v³)`，而非 `0.5 * ρ * mean(v)³`（两者结果不同，前者正确）。

### 8.4 前端渲染注意事项

- Step 5（详细分析）有 7～8 个分析模块，**必须使用懒渲染**：仅在用户切换到某模块时才初始化对应的 ECharts 实例，避免一次性渲染导致页面卡顿。
- 后端预计算聚合数据（直方图分组、持续曲线等），前端不处理 8 万条原始时序记录。
- ECharts 组件销毁时调用 `chart.dispose()` 释放内存。

### 8.5 报告生成注意事项

- WeasyPrint 需要系统安装 Pango、字体等依赖（见 `backend/Dockerfile`），本地开发须确认 `apt-get install libpango-1.0-0 libpangoft2-1.0-0 fonts-noto-cjk`。
- 中文字体必须在 Docker 镜像中安装（`fonts-noto-cjk`），否则 PDF 中文字符显示为方块。
- ECharts 图表导出时设置 `pixelRatio: 2` 保证 PDF 清晰度。

### 8.6 Docker 部署注意事项

- Nginx 的 SSE 端点配置**必须**关闭缓冲，否则进度事件无法实时推送：
  ```nginx
  location /api/ {
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection "";
    chunked_transfer_encoding on;
    proxy_read_timeout 300s;
  }
  ```
- `.env` 文件不提交版本控制，仅提交 `.env.example`。
- 生产环境通过 `docker-compose --env-file .env up` 注入环境变量。

---

*本文件与 [docs/PRD.md](docs/PRD.md) 和 [docs/TDD.md](docs/TDD.md) 配套使用。代码规范或技术决策有变更时，同步更新本文件。*
