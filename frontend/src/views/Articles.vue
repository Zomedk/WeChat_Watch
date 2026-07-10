<template>
  <div class="articles-container">
    <div class="filter-bar">
      <el-select v-model="filter.subscription_id" placeholder="选择公众号" class="filter-select">
        <el-option label="全部" :value="null" />
        <el-option v-for="sub in subscriptions" :key="sub.id" :label="sub.name" :value="sub.id" />
      </el-select>
      <el-date-picker v-model="filter.publish_date" type="date" placeholder="选择日期" class="filter-date" />
      <el-select v-model="filter.is_read" placeholder="阅读状态" class="filter-select">
        <el-option label="全部" :value="null" />
        <el-option label="已读" :value="true" />
        <el-option label="未读" :value="false" />
      </el-select>
      <el-button @click="fetchArticles" type="primary">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <el-button @click="syncAll">
        <el-icon><Refresh /></el-icon>
        同步全部
      </el-button>
    </div>

    <el-table :data="articles" border class="articles-table">
      <el-table-column prop="title" label="标题" min-width="300">
        <template #default="scope">
          <a :href="scope.row.url" target="_blank" class="title-link">{{ scope.row.title }}</a>
        </template>
      </el-table-column>
      <el-table-column prop="subscription_name" label="公众号" width="150" />
      <el-table-column prop="publish_date" label="发布日期" width="120" />
      <el-table-column prop="digest" label="摘要" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_read" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_read ? 'success' : 'warning'">
            {{ scope.row.is_read ? '已读' : '未读' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button @click="markRead(scope.row.id)" size="small">标记已读</el-button>
          <el-button @click="showSummary(scope.row)" size="small" type="primary">查看AI摘要</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="summaryDialogVisible" title="AI摘要" width="600px">
      <div v-if="currentSummary" class="summary-content">
        <p>{{ currentSummary }}</p>
      </div>
      <div v-else-if="!articleWithSummary" class="empty-summary">
        暂无摘要
      </div>
      <template #footer>
        <el-button @click="summaryDialogVisible = false">关闭</el-button>
        <el-button v-if="!currentSummary" @click="generateSummary" type="primary" :loading="generatingSummary">
          生成摘要
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from '../utils/axios'

const articles = ref([])
const subscriptions = ref([])
const filter = reactive({
  subscription_id: null,
  publish_date: null,
  is_read: null
})
const summaryDialogVisible = ref(false)
const articleWithSummary = ref(null)
const currentSummary = ref('')
const generatingSummary = ref(false)

const fetchArticles = async () => {
  const params = {}
  if (filter.subscription_id !== null) params.subscription_id = filter.subscription_id
  if (filter.publish_date) params.publish_date = filter.publish_date
  if (filter.is_read !== null) params.is_read = filter.is_read
  
  try {
    const res = await axios.get('/articles', { params })
    articles.value = res.data
  } catch (error) {
    console.error('获取文章失败:', error)
  }
}

const fetchSubscriptions = async () => {
  try {
    const res = await axios.get('/subscriptions')
    subscriptions.value = res.data
  } catch (error) {
    console.error('获取公众号失败:', error)
  }
}

const markRead = async (id) => {
  try {
    await axios.put(`/articles/${id}/read`)
    fetchArticles()
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const showSummary = (article) => {
  articleWithSummary.value = article
  currentSummary.value = article.summary || ''
  summaryDialogVisible.value = true
}

const generateSummary = async () => {
  if (!articleWithSummary.value) return
  
  generatingSummary.value = true
  try {
    const res = await axios.post(`/articles/${articleWithSummary.value.id}/summary`)
    currentSummary.value = res.data.summary
    fetchArticles()
  } catch (error) {
    console.error('生成摘要失败:', error)
  } finally {
    generatingSummary.value = false
  }
}

const syncAll = async () => {
  try {
    for (const sub of subscriptions.value) {
      await axios.post(`/subscriptions/${sub.id}/sync`)
    }
    fetchArticles()
    alert('同步完成')
  } catch (error) {
    console.error('同步失败:', error)
  }
}

fetchSubscriptions()
fetchArticles()
</script>

<style>
.articles-container {
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-select {
  width: 180px;
}

.filter-date {
  width: 180px;
}

.title-link {
  color: #409eff;
  text-decoration: none;
}

.title-link:hover {
  text-decoration: underline;
}

.summary-content {
  line-height: 1.8;
  color: #333;
}

.empty-summary {
  color: #999;
  text-align: center;
  padding: 40px;
}
</style>