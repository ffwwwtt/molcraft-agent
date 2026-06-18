# 🧪 MolCraft Agent

**自主科研智能体** —— AI 驱动的科学实验设计、数据分析与论文写作桌面应用。

MolCraft 是一个基于大语言模型的科研智能体系统，能够自动设计实验方案、执行数据分析、生成可视化图表，并导出规范的学术论文（Word / Markdown）。适用于化学、生物、材料科学等领域的计算实验。

---

## ✨ 功能特性

- 🤖 **AI 智能体引擎** — 基于 LLM 驱动的自主实验迭代（设计 → 执行 → 分析 → 优化闭环）
- 📊 **数据可视化** — 自动生成统计图表（matplotlib + seaborn，含中文字体支持）
- 📝 **论文导出** — 一键导出 Markdown / Word（.docx）格式的学术论文
- 💬 **实时对话** — WebSocket 驱动的流式对话界面，支持 Markdown 渲染
- 🔬 **化学工具集** — RDKit 分子处理、分子对接（AutoDock Vina）、OpenBabel 格式转换
- 🎨 **现代 UI** — Codex 风格界面，GSAP 动画，响应式设计
- 🔐 **用户认证** — JWT 令牌认证，多工作空间隔离

---

## 📋 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | **≥ 3.12** | 必须 |
| uv (可选) | 最新版 | 推荐，用于依赖管理 |
| FFmpeg | 最新版 | 可选，用于音视频文件处理 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ffwwwtt/molcraft-agent.git
cd molcraft-agent
```

### 2. 创建虚拟环境并安装依赖

**方式 A：使用 uv（推荐）**

```bash
# 安装 uv（如未安装）
pip install uv

# 同步依赖
uv sync
```

**方式 B：使用 pip**

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# 或
.venv\Scripts\activate      # Windows

pip install -e .
```

**安装化学工具包（可选，用于分子计算）：**

```bash
uv sync --extra chemistry
# 或
pip install -e ".[chemistry]"
```

> ⚠️ `rdkit` 和 `vina` 在某些平台上可能需要额外的系统依赖，详见各包的官方文档。

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 LLM API 密钥：

```env
# LLM 配置（OpenAI 兼容接口）
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=deepseek-ai/DeepSeek-V4-Pro

# 代理配置（如需）
HTTP_PROXY=http://127.0.0.1:7897
HTTPS_PROXY=http://127.0.0.1:7897
```

支持的 LLM 提供商：
- [SiliconFlow](https://siliconflow.cn) — DeepSeek、GLM 等
- [Moonshot AI](https://platform.moonshot.cn) — Kimi 系列
- 任何兼容 OpenAI API 接口的服务

### 4. 安装 FFmpeg（可选）

FFmpeg 用于处理音频和视频文件。如不需要此功能可跳过。

- **Windows**: 下载 [ffmpeg.exe](https://ffmpeg.org/download.html) 放到项目根目录
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt install ffmpeg` / `yum install ffmpeg`

### 5. 启动应用

```bash
# 默认启动在 http://0.0.0.0:8501
python launcher.py

# 自定义地址和端口
python launcher.py 127.0.0.1 8080
```

浏览器打开 **http://localhost:8501** 即可使用。

---

## 📁 项目结构

```
molcraft-agent/
├── launcher.py              # 启动入口
├── pyproject.toml            # 项目配置与依赖
├── .env.example              # 环境变量模板
├── agent_core/               # AI 智能体核心引擎
│   ├── engine.py             #   - 科研 Agent 主循环
│   ├── tools.py              #   - LLM 工具定义与处理
│   ├── experiments.py        #   - 实验记录管理
│   ├── paper_exporter.py     #   - 论文导出（Markdown/Word）
│   └── visualization.py      #   - 图表生成
├── server/                   # Web 服务
│   ├── app.py                #   - FastAPI 主应用
│   ├── auth.py               #   - JWT 认证
│   ├── database.py           #   - SQLite 数据库
│   ├── routers/              #   - API 路由
│   ├── models/               #   - 数据模型
│   ├── schemas.py            #   - 请求/响应模型
│   └── static/               #   - 前端静态资源
│       ├── index.html        #     - SPA 主页
│       ├── css/style.css     #     - 样式
│       └── js/               #     - JavaScript 模块
├── config/                   # 配置文件
└── workspace/                # 用户工作空间（运行时生成，不纳入版本控制）
```

---

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | FastAPI + Uvicorn |
| **数据库** | SQLite + SQLAlchemy (async) |
| **前端** | 原生 HTML/CSS/JS + GSAP 动画 |
| **AI 引擎** | OpenAI 兼容 API（支持 DeepSeek / GLM / Kimi 等） |
| **科学计算** | NumPy, SciPy, Pandas, Matplotlib, Seaborn |
| **化学工具** | RDKit, AutoDock Vina, OpenBabel, Biopython |
| **文档处理** | python-docx, MarkItDown |

---

## 🌐 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 应用主页 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/agent/start` | POST | 启动科研 Agent |
| `/api/agent/stop` | POST | 停止 Agent |
| `/api/agent/status` | GET | 查看 Agent 状态 |
| `/api/experiments` | GET | 实验记录列表 |
| `/api/experiments/export` | GET | 导出实验摘要 |
| `/api/charts` | GET | 图表列表 |
| `/api/files/upload` | POST | 上传文件 |
| `/ws` | WebSocket | 实时通信 |

---

## 📄 许可证

MIT License

---

## 👤 作者

**ffwwwtt** ([github.com/ffwwwtt](https://github.com/ffwwwtt))

---

*Built with ❤️ for science.*
