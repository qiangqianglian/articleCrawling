<template>
  <div class="ai-settings-page">
    <div class="page-header">
      <h2>🤖 AI设置</h2>
      <p class="subtitle">配置AI服务以获得更智能的文章搜索和总结</p>
    </div>

    <!-- 当前状态卡片 -->
    <div class="status-card card" :class="{ configured: config.is_configured }">
      <div class="status-icon">
        {{ config.is_configured ? "✅" : "⚠️" }}
      </div>
      <div class="status-content">
        <h3>{{ config.is_configured ? "AI服务已配置" : "AI服务未配置" }}</h3>
        <p>
          {{
            config.is_configured
              ? "您可以使用AI智能搜索功能"
              : "当前使用基础搜索，配置AI可获得更智能的总结"
          }}
        </p>
      </div>
    </div>

    <!-- 配置表单 -->
    <div class="config-form card">
      <h3>AI服务配置</h3>

      <div class="form-group">
        <label>AI提供商</label>
        <select
          v-model="form.provider"
          class="input"
          @change="onProviderChange"
        >
          <option
            v-for="provider in providers"
            :key="provider.id"
            :value="provider.id"
          >
            {{ provider.name }}
          </option>
        </select>
        <p class="help-text" v-if="selectedProvider">
          {{ selectedProvider.description }}
        </p>
      </div>

      <div class="form-group" v-if="form.provider !== 'none'">
        <label>API密钥</label>
        <input
          v-model="form.api_key"
          type="password"
          class="input"
          placeholder="请输入您的API密钥"
        />
        <p class="help-text">
          您的API密钥将安全地存储在本地，不会上传到任何服务器
        </p>
      </div>

      <div class="form-group" v-if="form.provider !== 'none'">
        <label>模型</label>
        <select v-model="form.model" class="input">
          <option value="">请选择模型</option>
          <option v-for="model in availableModels" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
      </div>

      <div class="form-group" v-if="form.provider !== 'none'">
        <label>自定义API地址（可选）</label>
        <input
          v-model="form.base_url"
          type="text"
          class="input"
          placeholder="留空使用默认地址"
        />
      </div>

      <div class="form-actions">
        <button
          class="btn btn-secondary"
          @click="testConfig"
          :disabled="testing || !canTest"
        >
          {{ testing ? "测试中..." : "测试连接" }}
        </button>
        <button class="btn btn-primary" @click="saveConfig" :disabled="saving">
          {{ saving ? "保存中..." : "保存配置" }}
        </button>
      </div>

      <!-- 测试结果 -->
      <div
        v-if="testResult"
        class="test-result"
        :class="{ success: testResult.success }"
      >
        {{ testResult.message }}
      </div>
    </div>

    <!-- 提供商说明 -->
    <div class="providers-info card">
      <h3>支持的AI提供商</h3>
      <div class="provider-list">
        <div
          v-for="provider in providers.filter((p) => p.id !== 'none')"
          :key="provider.id"
          class="provider-item"
        >
          <h4>{{ provider.name }}</h4>
          <p>{{ provider.description }}</p>
          <div class="model-tags">
            <span
              v-for="model in provider.models"
              :key="model"
              class="model-tag"
              >{{ model }}</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions card" v-if="config.is_configured">
      <button class="btn btn-danger" @click="resetConfig" :disabled="resetting">
        {{ resetting ? "重置中..." : "重置配置" }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { configApi } from "../services/api.js";

const config = reactive({
  provider: "none",
  model: "",
  base_url: "",
  enabled: false,
  is_configured: false,
});

const form = reactive({
  provider: "none",
  api_key: "",
  model: "",
  base_url: "",
  enabled: false,
});

const providers = ref([]);
const saving = ref(false);
const testing = ref(false);
const resetting = ref(false);
const testResult = ref(null);

const selectedProvider = computed(() => {
  return providers.value.find((p) => p.id === form.provider);
});

const availableModels = computed(() => {
  return selectedProvider.value?.models || [];
});

const canTest = computed(() => {
  if (form.provider === "none") return true;
  return form.api_key && form.model;
});

const loadConfig = async () => {
  try {
    const response = await configApi.getAIConfig();
    const data = response.data;

    Object.assign(config, data);
    Object.assign(form, {
      provider: data.provider,
      api_key: "", // 不显示已保存的API密钥
      model: data.model,
      base_url: data.base_url,
      enabled: data.enabled,
    });
  } catch (error) {
    console.error("加载配置失败:", error);
    alert("加载配置失败: " + error.message);
  }
};

const loadProviders = async () => {
  try {
    const response = await configApi.getAIProviders();
    providers.value = response.data.providers;
  } catch (error) {
    console.error("加载提供商列表失败:", error);
  }
};

const onProviderChange = () => {
  // 切换提供商时，自动选择第一个模型
  if (availableModels.value.length > 0) {
    form.model = availableModels.value[0];
  } else {
    form.model = "";
  }
  form.base_url = "";
  testResult.value = null;
};

const testConfig = async () => {
  testing.value = true;
  testResult.value = null;

  try {
    const response = await configApi.testAIConfig({
      provider: form.provider,
      api_key: form.api_key,
      model: form.model,
      base_url: form.base_url,
      enabled: form.provider !== "none",
    });

    testResult.value = response.data;
  } catch (error) {
    testResult.value = {
      success: false,
      message: "测试失败: " + error.message,
    };
  } finally {
    testing.value = false;
  }
};

const saveConfig = async () => {
  saving.value = true;

  try {
    const response = await configApi.updateAIConfig({
      provider: form.provider,
      api_key: form.api_key,
      model: form.model,
      base_url: form.base_url,
      enabled: form.provider !== "none",
    });

    const data = response.data;
    Object.assign(config, data);

    alert("配置保存成功！");
    testResult.value = null;
  } catch (error) {
    console.error("保存配置失败:", error);
    alert("保存配置失败: " + error.message);
  } finally {
    saving.value = false;
  }
};

const resetConfig = async () => {
  if (!confirm("确定要重置AI配置吗？这将清除所有AI设置。")) {
    return;
  }

  resetting.value = true;

  try {
    await configApi.resetAIConfig();
    await loadConfig();
    alert("配置已重置");
  } catch (error) {
    console.error("重置配置失败:", error);
    alert("重置配置失败: " + error.message);
  } finally {
    resetting.value = false;
  }
};

onMounted(() => {
  loadConfig();
  loadProviders();
});
</script>

<style scoped>
.ai-settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid #ffc107;
}

.status-card.configured {
  border-left-color: #28a745;
}

.status-icon {
  font-size: 2rem;
}

.status-content h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.status-content p {
  margin: 0;
  color: #666;
}

.config-form {
  margin-bottom: 1.5rem;
}

.config-form h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.help-text {
  margin: 0.5rem 0 0 0;
  color: #999;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.test-result {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
  background: #f8d7da;
  color: #721c24;
}

.test-result.success {
  background: #d4edda;
  color: #155724;
}

.providers-info {
  margin-bottom: 1.5rem;
}

.providers-info h3 {
  margin-bottom: 1rem;
  color: #333;
}

.provider-list {
  display: grid;
  gap: 1rem;
}

.provider-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.provider-item h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.provider-item p {
  margin: 0 0 0.5rem 0;
  color: #666;
  font-size: 0.9rem;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.model-tag {
  padding: 0.25rem 0.5rem;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #666;
}

.actions {
  text-align: center;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}
</style>
