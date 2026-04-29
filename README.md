# articleCrawling

PAI (Personal Article Intelligence) - 个人文章智能管理系统

一个能够自动爬取公众号文章、本地存储管理，并通过AI进行智能搜索和总结的工具。

## 功能特性

- **智能作者发现**：通过文章URL自动提取作者信息，建立作者档案
- **文章爬取与存储**：全量爬取历史文章，支持增量更新，Markdown格式存储
- **AI搜索与总结**：支持作者筛选、观点定位、AI智能总结和原文引用
- **Web界面管理**：直观的作者管理、文章浏览、AI搜索界面

## 技术栈

- **后端**：Python 3.9+ + FastAPI
- **前端**：Vue 3 + TypeScript + Element Plus
- **爬虫**：requests + BeautifulSoup4
- **数据存储**：Markdown文件 + JSON索引 + SQLite

## 项目结构

```
articleCrawling/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/      # API接口
│   │   ├── core/     # 核心逻辑
│   │   └── platforms/# 平台适配器
│   └── data/         # 数据存储
├── frontend/          # Vue3 前端
│   └── src/
│       ├── views/    # 页面组件
│       └── api/      # API接口
└── README.md
```

## 快速开始

### 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 启动服务

```bash
# 启动后端
cd backend
python start.py

# 启动前端
cd frontend
npm run dev
```

### 使用说明

1. 访问 `http://localhost:5173` 打开Web界面
2. 在"作者管理"页面添加公众号文章URL
3. 系统自动发现作者并爬取历史文章
4. 在"AI搜索"页面进行智能搜索和总结

## 数据存储

- 作者信息：`data/authors.json`
- 文章存储：`data/wechat/{作者名}/`
- 文章格式：Markdown + YAML Frontmatter

## 支持的公众号平台

- ✅ 微信公众号
- 🚧 小红书（计划中）

## 许可证

MIT License
