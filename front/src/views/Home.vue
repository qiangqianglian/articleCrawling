<template>
  <div class="home">
    <div class="hero">
      <h1>PAI - 个人文章智能管理</h1>
      <p class="description">
        爬取公众号文章，通过AI智能搜索和总结，快速找到你需要的观点
      </p>
      <div class="actions">
        <router-link to="/authors" class="btn btn-primary">
          开始管理作者
        </router-link>
        <router-link to="/search" class="btn btn-secondary">
          AI智能搜索
        </router-link>
      </div>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>📚 作者管理</h3>
        <p>添加公众号作者，自动提取作者信息</p>
      </div>
      <div class="feature-card">
        <h3>📝 文章爬取</h3>
        <p>一键爬取作者文章，保存为Markdown格式</p>
      </div>
      <div class="feature-card">
        <h3>🔍 AI搜索</h3>
        <p>输入观点关键词，智能定位相关文章并总结</p>
      </div>
    </div>

    <div class="stats" v-if="stats.authors > 0">
      <div class="stat-item">
        <span class="stat-number">{{ stats.authors }}</span>
        <span class="stat-label">作者</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ stats.articles }}</span>
        <span class="stat-label">文章</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { authorApi } from "../services/api.js";

const stats = ref({
  authors: 0,
  articles: 0,
});

onMounted(async () => {
  try {
    const response = await authorApi.getAll();
    const authors = response.data;
    stats.value.authors = authors.length;
    stats.value.articles = authors.reduce(
      (sum, a) => sum + (a.article_count || 0),
      0,
    );
  } catch (error) {
    console.error("获取统计失败:", error);
  }
});
</script>

<style scoped>
.home {
  text-align: center;
}

.hero {
  padding: 3rem 0;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.description {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  text-decoration: none;
  display: inline-block;
}

.btn-secondary:hover {
  background: #f8f9fa;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 3rem 0;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-card p {
  color: #666;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  color: #666;
}
</style>
