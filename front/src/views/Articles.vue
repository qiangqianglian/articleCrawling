<template>
  <div class="articles-page">
    <div class="page-header">
      <div class="header-left">
        <router-link to="/authors" class="back-link"
          >← 返回作者列表</router-link
        >
        <h2>{{ authorName }} 的文章</h2>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCrawlModal = true">
          + 爬取新文章
        </button>
        <button class="btn btn-danger" @click="confirmDeleteAll">
          删除全部
        </button>
      </div>
    </div>

    <!-- 文章列表 -->
    <div class="articles-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="articles.length === 0" class="empty">
        暂无文章，点击"爬取新文章"添加
      </div>
      <div v-else class="article-cards">
        <div
          v-for="article in articles"
          :key="article.title"
          class="article-card"
          @click="viewArticle(article)"
        >
          <h3 class="article-title">{{ article.title }}</h3>
          <div class="article-meta">
            <span class="publish-date">{{ article.publish_date }}</span>
            <span class="word-count">{{ article.word_count }} 字</span>
          </div>
          <p class="article-summary" v-if="article.summary">
            {{ article.summary }}
          </p>
          <div class="article-actions">
            <button
              class="btn btn-danger btn-sm"
              @click.stop="confirmDelete(article)"
            >
              删除
            </button>
          </div>
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
            <span>字数: {{ selectedArticle.word_count }}</span>
          </div>
          <div
            class="article-content"
            v-if="selectedArticle.content"
            v-html="renderMarkdown(selectedArticle.content)"
          ></div>
          <div class="article-content empty-content" v-else>
            <p>文章内容为空，可能原因：</p>
            <ul>
              <li>文章爬取时未能获取到正文内容</li>
              <li>文章需要重新爬取</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-danger"
            @click="confirmDelete(selectedArticle)"
          >
            删除文章
          </button>
          <a
            :href="selectedArticle.url"
            target="_blank"
            class="btn btn-primary"
          >
            查看原文
          </a>
        </div>
      </div>
    </div>

    <!-- 爬取文章弹窗 -->
    <div
      v-if="showCrawlModal"
      class="modal-overlay"
      @click="showCrawlModal = false"
    >
      <div class="modal" @click.stop>
        <h3>爬取新文章</h3>
        <div class="form-group">
          <label>文章URL</label>
          <input
            v-model="crawlUrl"
            type="text"
            class="input"
            placeholder="粘贴公众号文章链接"
          />
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showCrawlModal = false">取消</button>
          <button
            class="btn btn-primary"
            @click="crawlArticle"
            :disabled="crawling"
          >
            {{ crawling ? "爬取中..." : "开始爬取" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div
      v-if="showDeleteModal"
      class="modal-overlay"
      @click="showDeleteModal = false"
    >
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>确定要删除文章《{{ articleToDelete?.title }}》吗？</p>
        <p class="warning-text">此操作不可恢复！</p>
        <div class="modal-actions">
          <button class="btn" @click="showDeleteModal = false">取消</button>
          <button
            class="btn btn-danger"
            @click="deleteArticle"
            :disabled="deleting"
          >
            {{ deleting ? "删除中..." : "确认删除" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除全部确认弹窗 -->
    <div
      v-if="showDeleteAllModal"
      class="modal-overlay"
      @click="showDeleteAllModal = false"
    >
      <div class="modal" @click.stop>
        <h3>⚠️ 确认删除全部文章</h3>
        <p>确定要删除<strong>所有作者的所有文章</strong>吗？</p>
        <p class="warning-text">此操作不可恢复！作者信息将保留。</p>
        <div class="modal-actions">
          <button class="btn" @click="showDeleteAllModal = false">取消</button>
          <button
            class="btn btn-danger"
            @click="deleteAllArticles"
            :disabled="deletingAll"
          >
            {{ deletingAll ? "删除中..." : "确认删除全部" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { articleApi } from "../services/api.js";

const route = useRoute();
const authorName = route.params.authorName;

const articles = ref([]);
const loading = ref(false);
const selectedArticle = ref(null);
const showCrawlModal = ref(false);
const crawlUrl = ref("");
const crawling = ref(false);

// 删除相关
const showDeleteModal = ref(false);
const articleToDelete = ref(null);
const deleting = ref(false);

// 删除全部相关
const showDeleteAllModal = ref(false);
const deletingAll = ref(false);

const loadArticles = async () => {
  loading.value = true;
  try {
    const response = await articleApi.getByAuthor(authorName);
    articles.value = response.data;
  } catch (error) {
    console.log("加载文章列表失败: " + error.message);
  } finally {
    loading.value = false;
  }
};

const viewArticle = async (article) => {
  try {
    const response = await articleApi.getByTitle(authorName, article.title);
    selectedArticle.value = response.data;
  } catch (error) {
    console.log("加载文章详情失败: " + error.message);
  }
};

const crawlArticle = async () => {
  if (!crawlUrl.value) {
    console.log("请输入文章URL");
    return;
  }

  crawling.value = true;
  try {
    await articleApi.crawl({
      url: crawlUrl.value,
      author_name: authorName,
    });
    showCrawlModal.value = false;
    crawlUrl.value = "";
    await loadArticles();
    console.log("文章爬取成功！");
  } catch (error) {
    console.log("爬取失败: " + (error.response?.data?.detail || error.message));
  } finally {
    crawling.value = false;
  }
};

const confirmDelete = (article) => {
  articleToDelete.value = article;
  showDeleteModal.value = true;
};

const deleteArticle = async () => {
  if (!articleToDelete.value) return;

  deleting.value = true;
  try {
    await articleApi.delete(authorName, articleToDelete.value.title);
    showDeleteModal.value = false;
    articleToDelete.value = null;
    selectedArticle.value = null;
    await loadArticles();
    console.log("文章删除成功！");
  } catch (error) {
    console.log("删除失败: " + (error.response?.data?.detail || error.message));
  } finally {
    deleting.value = false;
  }
};

// Markdown渲染函数
const renderMarkdown = (content) => {
  if (!content) return "";

  // 将Markdown图片格式 ![alt](url) 转换为HTML img标签
  let html = content
    .replace(
      /!\[([^\]]*)\]\(([^)]+)\)/g,
      '<img src="$2" alt="$1" style="max-width:100%;margin:10px 0;">',
    )
    .replace(/\n/g, "<br>");

  return html;
};

const confirmDeleteAll = () => {
  showDeleteAllModal.value = true;
};

const deleteAllArticles = async () => {
  deletingAll.value = true;
  try {
    const response = await articleApi.deleteAll();
    showDeleteAllModal.value = false;
    await loadArticles();
    console.log(response.data.message);
  } catch (error) {
    console.log(
      "删除全部失败: " + (error.response?.data?.detail || error.message),
    );
  } finally {
    deletingAll.value = false;
  }
};

onMounted(loadArticles);
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.back-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h2 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.articles-list {
  min-height: 200px;
}

.loading,
.empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.article-cards {
  display: grid;
  gap: 1rem;
}

.article-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.article-title {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.article-meta {
  display: flex;
  gap: 1rem;
  color: #999;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.article-summary {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.article-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
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
  max-width: 500px;
}

.article-modal {
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
}

.article-content img {
  max-width: 100%;
  height: auto;
  margin: 10px 0;
  border-radius: 4px;
}

.article-content.empty-content {
  color: #999;
  text-align: center;
  padding: 2rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.article-content.empty-content p {
  margin-bottom: 0.5rem;
}

.article-content.empty-content ul {
  text-align: left;
  display: inline-block;
  margin: 0;
  padding-left: 1.5rem;
}

.article-content.empty-content li {
  margin: 0.25rem 0;
}

.modal-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  text-align: right;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.warning-text {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* 按钮样式 */
.btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn:hover {
  background: #f5f5f5;
}

.btn-primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.input:focus {
  outline: none;
  border-color: #667eea;
}
</style>
