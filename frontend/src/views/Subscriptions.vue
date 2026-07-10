<template>
  <div class="subscriptions-container">
    <div class="header-bar">
      <el-button @click="showAddDialog = true" type="primary">
        <el-icon><Plus /></el-icon>
        添加公众号
      </el-button>
    </div>

    <el-table :data="subscriptions" border class="subscriptions-table">
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column prop="fakeid" label="FakeID" width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
            {{ scope.row.status === 'active' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="added_at" label="添加时间" width="180" />
      <el-table-column prop="last_sync_at" label="最后同步" width="180" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button @click="syncSingle(scope.row)" size="small">同步</el-button>
          <el-button @click="toggleStatus(scope.row)" size="small">
            {{ scope.row.status === 'active' ? '停用' : '启用' }}
          </el-button>
          <el-button @click="deleteSubscription(scope.row.id)" size="small" type="danger">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAddDialog" title="添加公众号" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="公众号名称">
          <el-input v-model="form.name" placeholder="请输入公众号名称" />
        </el-form-item>
        <el-form-item label="FakeID">
          <el-input v-model="form.fakeid" placeholder="请输入公众号FakeID" />
          <el-link type="primary" @click="searchFakeID" style="font-size: 12px;">搜索获取FakeID</el-link>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button @click="addSubscription" type="primary" :loading="adding">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="searchDialogVisible" title="搜索公众号" width="400px">
      <el-form :model="searchForm" label-width="80px">
        <el-form-item label="公众号名称">
          <el-input v-model="searchForm.name" placeholder="请输入公众号名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="searchDialogVisible = false">取消</el-button>
        <el-button @click="doSearchFakeID" type="primary" :loading="searching">搜索</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import axios from '../utils/axios'

const subscriptions = ref([])
const showAddDialog = ref(false)
const searchDialogVisible = ref(false)
const adding = ref(false)
const searching = ref(false)

const form = reactive({
  name: '',
  fakeid: ''
})

const searchForm = reactive({
  name: ''
})

const fetchSubscriptions = async () => {
  try {
    const res = await axios.get('/subscriptions')
    subscriptions.value = res.data
  } catch (error) {
    console.error('获取公众号列表失败:', error)
  }
}

const addSubscription = async () => {
  if (!form.name || !form.fakeid) {
    alert('请填写完整信息')
    return
  }
  
  adding.value = true
  try {
    await axios.post('/subscriptions', { name: form.name, fakeid: form.fakeid })
    fetchSubscriptions()
    showAddDialog.value = false
    form.name = ''
    form.fakeid = ''
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    adding.value = false
  }
}

const deleteSubscription = async (id) => {
  if (!confirm('确定要删除这个公众号吗？')) return
  
  try {
    await axios.delete(`/subscriptions/${id}`)
    fetchSubscriptions()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const toggleStatus = async (subscription) => {
  const newStatus = subscription.status === 'active' ? 'inactive' : 'active'
  
  try {
    await axios.put(`/subscriptions/${subscription.id}`, { status: newStatus })
    fetchSubscriptions()
  } catch (error) {
    console.error('更新状态失败:', error)
  }
}

const syncSingle = async (subscription) => {
  try {
    const res = await axios.post(`/subscriptions/${subscription.id}/sync`)
    alert(res.data.message)
    fetchSubscriptions()
  } catch (error) {
    console.error('同步失败:', error)
  }
}

const searchFakeID = () => {
  searchDialogVisible.value = true
}

const doSearchFakeID = async () => {
  if (!searchForm.name) {
    alert('请输入公众号名称')
    return
  }
  
  searching.value = true
  try {
    const res = await axios.get('/auth/status')
    if (res.data.status !== 'logged_in') {
      alert('请先登录微信公众号')
      return
    }
    alert('请在后端使用 test_wechat_api.py 搜索公众号FakeID')
    searchDialogVisible.value = false
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    searching.value = false
  }
}

fetchSubscriptions()
</script>

<style>
.subscriptions-container {
  padding: 20px;
}

.header-bar {
  margin-bottom: 20px;
}
</style>