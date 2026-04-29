<template>
  <div class="authors-page">
    <div class="page-header">
      <h2>作者管理</h2>
      <button class="btn btn-primary" @click="showAddModal = true">
        + 添加作者
      </button>
    </div>

    <!-- 作者列表 -->
    <div class="authors-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="authors.length === 0" class="empty">
        暂无作者，点击上方按钮添加
      </div>
      <div v-else class="author-cards">
        <div v-for="author in authors" :key="author.name" class="author-card">
          <div class="author-info">
            <img
              v-if="author.avatar"
              :src="author.avatar"
              :alt="author.name"
              class="author-avatar"
            />
            <div v-else class="author-avatar placeholder">
              {{ author.name.charAt(0) }}
            </div>
            <div class="author-details">
              <h3>{{ author.name }}</h3>
              <p class="platform">平台: {{ author.platform }}</p>
              <p class="description" v-if="author.description">
                {{ author.description }}
              </p>
              <p class="stats">文章数: {{ author.article_count || 0 }}</p>
            </div>
          </div>
          <div class="author-actions">
            <router-link :to="`/articles/${author.name}`" class="btn btn-small">
              查看文章
            </router-link>
            <button
              class="btn btn-small btn-crawl"
              @click="crawlAuthor(author.name)"
              :disabled="crawling === author.name"
            >
              {{ crawling === author.name ? "爬取中..." : "爬取文章" }}
            </button>
            <button
              class="btn btn-small btn-danger"
              @click="deleteAuthor(author.name)"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加作者弹窗 -->
    <div
      v-if="showAddModal"
      class="modal-overlay"
      @click="showAddModal = false"
    >
      <div class="modal" @click.stop>
        <h3>添加新作者</h3>
        <div class="form-group">
          <label>文章URL</label>
          <input
            v-model="newAuthor.url"
            type="text"
            class="input"
            placeholder="粘贴公众号文章链接"
          />
        </div>
        <div class="form-group">
          <label>平台</label>
          <select v-model="newAuthor.platform" class="input">
            <option value="wechat">微信公众号</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showAddModal = false">取消</button>
          <button class="btn btn-primary" @click="addAuthor" :disabled="adding">
            {{ adding ? "添加中..." : "添加" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { authorApi } from "../services/api.js";

const authors = ref([]);
const loading = ref(false);
const showAddModal = ref(false);
const adding = ref(false);
const crawling = ref("");

const newAuthor = ref({
  url: "",
  platform: "wechat",
});

const loadAuthors = async () => {
  loading.value = true;
  try {
    const response = await authorApi.getAll();
    authors.value = response.data;
  } catch (error) {
    console.log("加载作者列表失败: " + error.message);
  } finally {
    loading.value = false;
  }
};

const addAuthor = async () => {
  if (!newAuthor.value.url) {
    console.log("请输入文章URL");
    return;
  }

  adding.value = true;
  try {
    await authorApi.create(newAuthor.value);
    showAddModal.value = false;
    newAuthor.value = { url: "", platform: "wechat" };
    await loadAuthors();
    console.log("作者添加成功！");
  } catch (error) {
    console.log("添加失败: " + (error.response?.data?.detail || error.message));
  } finally {
    adding.value = false;
  }
};

const deleteAuthor = async (name) => {
  if (!confirm(`确定要删除作者 "${name}" 吗？这将删除该作者的所有文章。`)) {
    return;
  }

  try {
    await authorApi.delete(name);
    await loadAuthors();
    console.log("作者已删除");
  } catch (error) {
    console.log("删除失败: " + error.message);
  }
};

const crawlAuthor = async (name) => {
  crawling.value = name;
  try {
    const response = await authorApi.crawl(name);
    console.log(`爬取完成！${response.data.message}`);
    // 重新加载作者列表以更新文章数
    await loadAuthors();
  } catch (error) {
    console.log("爬取失败: " + error.message);
  } finally {
    crawling.value = "";
  }
};

onMounted(loadAuthors);
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  color: #333;
}

.authors-list {
  min-height: 200px;
}

.loading,
.empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.author-cards {
  display: grid;
  gap: 1rem;
}

.author-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.author-avatar.placeholder {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.author-details h3 {
  margin-bottom: 0.25rem;
  color: #333;
}

.author-details .platform {
  color: #667eea;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.author-details .description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author-details .stats {
  color: #999;
  font-size: 0.85rem;
}

.author-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-crawl {
  background: #27ae60;
  color: white;
}

.btn-crawl:hover {
  background: #229954;
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

.modal h3 {
  margin-bottom: 1.5rem;
  color: #333;
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
</style>
