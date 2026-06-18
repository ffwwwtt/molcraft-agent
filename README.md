# 🧪 MolCraft Agent

**自主科研智能体** —— AI 驱动的科学实验设计、数据分析与论文写作桌面应用。

MolCraft 是一个基于大语言模型的科研智能体系统，能够自动设计实验方案、执行数据分析、生成可视化图表，并导出规范的学术论文（Word / Markdown）。适用于化学、生物、材料科学等领域的计算实验。

---

## ✨ 功能特性

- 🤖 **AI 智能体引擎** — LLM 驱动的自主实验迭代（设计 → 执行 → 分析 → 优化闭环）
- 📊 **数据可视化** — 自动生成统计图表（matplotlib + seaborn，含中文字体支持）
- 📝 **论文导出** — 一键导出 Markdown / Word（.docx）格式的学术论文
- 💬 **实时对话** — WebSocket 驱动的流式对话界面，支持 Markdown 渲染
- 🔬 **化学工具集** — RDKit 分子处理、分子对接（AutoDock Vina）、OpenBabel 格式转换
- 🎨 **现代 UI** — Codex 风格深色界面，GSAP 滚动动画，响应式设计
- 🔐 **用户认证** — JWT 令牌认证，多工作空间隔离

---

## 📋 环境要求

| 依赖 | 版本 | 必须？ | 说明 |
|------|------|--------|------|
| Python | **≥ 3.12** | ✅ 必须 | |
| pip | 最新版 | ✅ 必须 | 安装依赖用 |
| FFmpeg | 最新版 | ❌ 可选 | 音视频文件处理时才需要 |

> 💡 不需要 Node.js、不需要 npm、不需要 Docker。纯 Python + 浏览器即可运行。

---

## 🚀 快速开始（3 步）

### 1. 克隆项目

```bash
git clone https://github.com/ffwwwtt/molcraft-agent.git
cd molcraft-agent
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置密钥并启动

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 API 密钥（用任意文本编辑器打开）
# 必须填的一项是 LLM_API_KEY

# 启动
python launcher.py
```

浏览器打开 **http://localhost:8501**，注册一个账号即可使用。

---

## 🔑 LLM API 密钥获取

项目使用 OpenAI 兼容接口，支持以下提供商（任选一个）：

| 提供商 | 获取地址 | 免费额度 |
|--------|----------|----------|
| **SiliconFlow**（推荐） | [siliconflow.cn](https://siliconflow.cn) | 注册送 2000 万 tokens |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com) | 注册送额度 |
| **Moonshot (Kimi)** | [platform.moonshot.cn](https://platform.moonshot.cn) | 注册送额度 |
| **OpenAI** | [platform.openai.com](https://platform.openai.com) | 需付费 |
| **其他兼容接口** | 任何 OpenAI 兼容 API | — |

获取 API Key 后，填入 `.env` 文件：

```env
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_MODEL=deepseek-ai/DeepSeek-V4-Pro
```

---

## ⚠️ 常见问题

### 页面加载后图标/按钮不显示？

GSAP 动画依赖 `cdnjs.cloudflare.com` 加载 JS 库。如遇网络问题，等几秒会自动恢复显示。不影响使用。

### Google Fonts 加载慢？

国内网络访问 Google Fonts 可能较慢或超时，页面会自动降级使用系统字体（苹方 / 微软雅黑），不影响功能。

### 需要代理才能访问 API？

在 `.env` 中配置代理：

```env
HTTP_PROXY=http://127.0.0.1:7897
HTTPS_PROXY=http://127.0.0.1:7897
```

### 数据库或工作空间在哪？

首次运行会自动在项目根目录创建 `molcraft.db`（SQLite 数据库）和 `workspace/` 目录。这些不应提交到 git。

### 化学工具包（RDKit, Vina 等）安装失败？

化学工具包是可选的，基础功能不需要它们。如需安装：

```bash
pip install rdkit vina meeko gemmi openbabel-wheel biopython
```

Windows 用户建议用 conda 安装 RDKit：`conda install -c conda-forge rdkit`

---

## 🔧 可选：安装 FFmpeg

FFmpeg 仅用于音视频文件处理，跳过不影响核心功能。

- **Windows**：下载 [ffmpeg.exe](https://ffmpeg.org/download.html) 放到项目根目录
- **macOS**：`brew install ffmpeg`
- **Linux**：`apt install ffmpeg`

---

## 📁 项目结构

```
molcraft-agent/
├── launcher.py              # 启动入口
├── requirements.txt         # Python 依赖
├── pyproject.toml           # 项目元数据（可选，uv 用）
├── .env.example             # 环境变量模板
├── README.md
├── agent_core/              # AI 智能体核心引擎
│   ├── engine.py            #   - 科研 Agent 主循环 (LLM 驱动)
│   ├── tools.py             #   - 工具定义与处理 (30+ 工具)
│   ├── experiments.py       #   - 实验记录管理
│   ├── paper_exporter.py    #   - 论文导出 (Markdown / Word)
│   ├── visualization.py     #   - 图表生成 (matplotlib)
│   └── workspace_context.py #   - 工作空间上下文
├── server/                  # Web 服务 (FastAPI)
│   ├── app.py               #   - 主应用 (路由 + WebSocket)
│   ├── auth.py              #   - JWT 认证
│   ├── database.py          #   - SQLite 异步数据库
│   ├── routers/auth.py      #   - 登录注册 API
│   ├── models/              #   - ORM 数据模型
│   └── static/              #   - 前端 (原生 HTML/CSS/JS)
│       ├── index.html       #     - SPA 主页 (含 landing page)
│       ├── css/style.css    #     - 完整样式 (~950 行)
│       └── js/app.js        #     - 前端逻辑 (~3000 行)
├── config/                  # 配置
└── workspace/               # 用户工作空间 (运行时生成，不追踪)
```

---

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | FastAPI + Uvicorn + SQLAlchemy (async) |
| **数据库** | SQLite + aiosqlite |
| **前端** | 原生 HTML/CSS/JS + GSAP ScrollTrigger |
| **AI** | OpenAI 兼容 API (DeepSeek / GLM / Kimi / GPT 等) |
| **科学计算** | NumPy · SciPy · Pandas · Matplotlib · Seaborn |
| **化学 (可选)** | RDKit · AutoDock Vina · OpenBabel · Biopython |
| **文档** | python-docx · MarkItDown |
| **认证** | bcrypt · python-jose (JWT) · cryptography |

---

## 📄 许可证

MIT License

---

## 👤 作者

**ffwwwtt** — [github.com/ffwwwtt](https://github.com/ffwwwtt)

---

*Built with ❤️ for science.*
