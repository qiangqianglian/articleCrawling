<template>
  <div class="search-page">
    <div class="search-header">
      <h2>🔍 AI智能搜索</h2>
      <p class="subtitle">输入观点关键词，智能定位相关文章并生成总结</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        class="input search-input"
        placeholder="输入你想了解的观点，例如：'猫对人工智能的看法'"
        @keyup.enter="performSearch"
      />
      <button
        class="btn btn-primary search-btn"
        @click="performSearch"
        :disabled="searching"
      >
        {{ searching ? "搜索中..." : "AI搜索" }}
      </button>
    </div>

    <!-- 作者筛选 -->
    <div class="author-filter" v-if="authors.length > 0">
      <label>筛选作者：</label>
      <select v-model="selectedAuthor" class="input">
        <option value="">全部作者</option>
        <option
          v-for="author in authors"
          :key="author.name"
          :value="author.name"
        >
          {{ author.name }}
        </option>
      </select>
    </div>

    <!-- AI总结结果 -->
    <div v-if="searchResult" class="ai-answer card">
      <div class="ai-header">
        <h3>🤖 AI总结</h3>
        <span class="ai-badge" :class="{ 'ai-active': searchResult.ai_used }">
          {{ searchResult.ai_used ? "AI生成" : "基础搜索" }}
        </span>
      </div>
      <div class="answer-content">{{ searchResult.answer }}</div>
      <div class="search-meta">
        <span>找到 {{ searchResult.total_count }} 篇相关文章</span>
        <span v-if="!searchResult.ai_used" class="ai-hint">
          💡 {{ searchResult.message }}
          <router-link to="/ai-settings" class="config-link"
            >去配置</router-link
          >
        </span>
      </div>
    </div>

    <!-- 搜索结果列表 -->
    <div
      v-if="searchResult && searchResult.results.length > 0"
      class="search-results"
    >
      <h3>📄 相关文章</h3>
      <div class="result-cards">
        <div
          v-for="(result, index) in searchResult.results"
          :key="index"
          class="result-card"
          @click="viewArticle(result)"
        >
          <div class="result-header">
            <h4>{{ result.title }}</h4>
            <span class="relevance-score"
              >相关度: {{ result.relevance_score }}%</span
            >
          </div>
          <div class="result-meta">
            <span class="author">{{ result.author }}</span>
            <span class="date">{{ result.publish_date }}</span>
          </div>
          <p class="result-summary">{{ result.summary }}</p>
        </div>
      </div>
    </div>

    <!-- 文章详情弹窗 -->
    <div
      v-if="selectedArticle"
      class="modal-overlay"
      @click="selectedArticle = null"
    >
      <div class="modal article-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedArticle.title }}</h3>
          <button class="close-btn" @click="selectedArticle = null">×</button>
        </div>
        <div class="modal-body">
          <div class="article-info">
            <span>作者: {{ selectedArticle.author }}</span>
            <span>发布日期: {{ selectedArticle.publish_date }}</span>
          </div>
          <div class="article-content">
            {{ selectedArticle.content || selectedArticle.summary }}
          </div>
        </div>
        <div class="modal-footer">
          <a
            v-if="selectedArticle.url"
            :href="selectedArticle.url"
            target="_blank"
            class="btn btn-primary"
          >
            查看原文
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { searchApi, authorApi, articleApi } from "../services/api.js";

const searchQuery = ref("");
const selectedAuthor = ref("");
const authors = ref([]);
const searching = ref(false);
const searchResult = ref(null);
const selectedArticle = ref(null);

const loadAuthors = async () => {
  try {
    const response = await authorApi.getAll();
    authors.value = response.data;
  } catch (error) {
    console.error("加载作者列表失败:", error);
  }
};

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    console.log("请输入搜索关键词");
    return;
  }

  searching.value = true;
  searchResult.value = null;

  try {
    const response = await searchApi.aiSearch({
      query: searchQuery.value,
      author_name: selectedAuthor.value || null,
      max_results: 10,
    });
    searchResult.value = response.data;
  } catch (error) {
    console.log("搜索失败: " + error.message);
  } finally {
    searching.value = false;
  }
};

const viewArticle = async (result) => {
  try {
    // 尝试获取完整文章内容
    const response = await articleApi.getByTitle(result.author, result.title);
    selectedArticle.value = response.data;
  } catch (error) {
    // 如果获取失败，显示搜索结果中的信息
    selectedArticle.value = result;
  }
};

onMounted(loadAuthors);
</script>

<style scoped>
.search-page {
  max-width: 900px;
  margin: 0 auto;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.search-header h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
}

.search-box {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 1rem;
  font-size: 1rem;
}

.search-btn {
  padding: 1rem 2rem;
  font-size: 1rem;
}

.author-filter {
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-filter label {
  color: #666;
}

.author-filter select {
  width: auto;
  min-width: 200px;
}

.ai-answer {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-left: 4px solid #667eea;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.ai-answer h3 {
  color: #667eea;
  margin: 0;
}

.ai-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  background: #e9ecef;
  color: #666;
}

.ai-badge.ai-active {
  background: #667eea;
  color: white;
}

.answer-content {
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  margin-bottom: 1rem;
}

.search-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #999;
  font-size: 0.9rem;
}

.ai-hint {
  color: #ffc107;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.config-link {
  color: #667eea;
  text-decoration: underline;
  cursor: pointer;
}

.config-link:hover {
  color: #764ba2;
}

.search-results {
  margin-top: 2rem;
}

.search-results h3 {
  color: #333;
  margin-bottom: 1rem;
}

.result-cards {
  display: grid;
  gap: 1rem;
}

.result-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.result-header h4 {
  color: #333;
  margin: 0;
  flex: 1;
}

.relevance-score {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-left: 1rem;
}

.result-meta {
  display: flex;
  gap: 1rem;
  color: #999;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.result-summary {
  color: #666;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  max-height: 60vh;
  overflow-y: auto;
}

.article-info {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.article-content {
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.modal-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  text-align: right;
}
</style>
