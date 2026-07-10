<template>
  <div class="settings-container">
    <el-card title="AI配置" class="settings-card">
      <el-form :model="aiConfig" label-width="120px">
        <el-form-item label="API Key">
          <el-input v-model="aiConfig.api_key" type="password" placeholder="请输入AI API Key" />
        </el-form-item>
        <el-form-item label="API Base URL">
          <el-input v-model="aiConfig.api_base_url" placeholder="如: https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="aiConfig.model" placeholder="如: gpt-3.5-turbo" />
        </el-form-item>
        <el-form-item>
          <el-button @click="saveAIConfig" type="primary" :loading="saving">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card title="系统状态" class="settings-card">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="微信登录状态">
          <el-tag :type="authStatus === 'logged_in' ? 'success' : 'warning'">
            {{ authStatus === 'logged_in' ? '已登录' : '未登录' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="同步间隔">
          {{ syncInterval }} 分钟
        </el-descriptions-item>
        <el-descriptions-item label="公众号数量">
          {{ subscriptionCount }} 个
        </el-descriptions-item>
        <el-descriptions-item label="文章数量">
          {{ articleCount }} 篇
        </el-descriptions-item>
      </el-descriptions>
      <el-button @click="refreshStatus" style="margin-top: 20px;">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </el-card>

    <el-card title="使用说明" class="settings-card">
      <div class="guide-content">
        <h4>1. 登录微信公众号</h4>
        <p>运行后端目录下的 get_cookie.py 文件，在弹出的浏览器中扫码登录微信公众号后台。</p>
        <h4>2. 添加公众号</h4>
        <p>在公众号管理页面添加需要监控的公众号，需要提供公众号名称和FakeID。</p>
        <h4>3. 获取FakeID</h4>
        <p>可以使用 test_wechat_api.py 搜索公众号名称获取对应的FakeID。</p>
        <h4>4. 同步文章</h4>
        <p>系统会自动定时同步文章，也可以手动点击同步按钮触发。</p>
        <h4>5. AI摘要</h4>
        <p>在文章列表中点击"查看AI摘要"可以查看或生成文章的AI摘要。</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import axios from '../utils/axios'

const aiConfig = reactive({
  api_key: '',
  api_base_url: '',
  model: ''
})

const saving = ref(false)
const authStatus = ref('unknown')
const syncInterval = ref(60)
const subscriptionCount = ref(0)
const articleCount = ref(0)

const fetchAIConfig = async () => {
  try {
    const res = await axios.get('/settings/ai')
    aiConfig.api_key = res.data.ai_api_key || ''
    aiConfig.api_base_url = res.data.ai_api_base_url || ''
    aiConfig.model = res.data.ai_model || ''
  } catch (error) {
    console.error('获取配置失败:', error)
  }
}

const saveAIConfig = async () => {
  saving.value = true
  try {
    await axios.post('/settings/ai', {
      api_key: aiConfig.api_key,
      api_base_url: aiConfig.api_base_url,
      model: aiConfig.model
    })
    alert('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}

const refreshStatus = async () => {
  try {
    const [authRes, subsRes] = await Promise.all([
      axios.get('/auth/status'),
      axios.get('/subscriptions')
    ])
    authStatus.value = authRes.data.status
    subscriptionCount.value = subsRes.data.length
  } catch (error) {
    console.error('刷新状态失败:', error)
  }
}

onMounted(() => {
  fetchAIConfig()
  refreshStatus()
})
</script>

<style>
.settings-container {
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.guide-content {
  line-height: 1.8;
}

.guide-content h4 {
  margin-top: 16px;
  margin-bottom: 8px;
  color: #333;
}

.guide-content p {
  margin: 0;
  color: #666;
}
</style>