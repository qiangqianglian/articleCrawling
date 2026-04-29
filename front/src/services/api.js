import axios from "axios";

const API_BASE_URL = "http://localhost:8002";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 作者管理API
export const authorApi = {
  // 获取所有作者
  getAll: () => api.get("/authors"),

  // 获取单个作者
  getByName: (name) => api.get(`/authors/${name}`),

  // 添加作者
  create: (data) => api.post("/authors", data),

  // 删除作者
  delete: (name) => api.delete(`/authors/${name}`),

  // 爬取作者文章
  crawl: (name) => api.post(`/authors/${name}/crawl`),
};

// 文章管理API
export const articleApi = {
  // 获取作者的所有文章
  getByAuthor: (authorName) => api.get(`/articles/author/${authorName}`),

  // 获取单篇文章
  getByTitle: (authorName, title) =>
    api.get(`/articles/author/${authorName}/${title}`),

  // 爬取文章
  crawl: (data) => api.post("/articles/crawl", data),

  // 搜索文章
  search: (keyword, authorName) => {
    const params = { keyword };
    if (authorName) params.author_name = authorName;
    return api.get("/articles/search", { params });
  },

  // 删除文章
  delete: (authorName, title) =>
    api.delete(`/articles/author/${authorName}/${title}`),

  // 删除所有文章
  deleteAll: () => api.delete("/articles/all"),
};

// AI搜索API
export const searchApi = {
  // AI智能搜索
  aiSearch: (data) => api.post("/search/ai", data),

  // 简单搜索
  simpleSearch: (keyword, authorName, limit = 20) => {
    const params = { keyword, limit };
    if (authorName) params.author_name = authorName;
    return api.get("/search/simple", { params });
  },
};

// 配置管理API
export const configApi = {
  // 获取AI配置
  getAIConfig: () => api.get("/config/ai"),

  // 更新AI配置
  updateAIConfig: (data) => api.post("/config/ai", data),

  // 获取AI提供商列表
  getAIProviders: () => api.get("/config/ai/providers"),

  // 重置AI配置
  resetAIConfig: () => api.delete("/config/ai"),

  // 测试AI配置
  testAIConfig: (data) => api.post("/config/ai/test", data),
};

export default api;
