<template>
  <el-container class="app-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><Message /></el-icon>
        <span>公众号监控</span>
      </div>
      <el-menu :default-active="activeMenu" class="sidebar-menu" router>
        <el-menu-item index="/">
          <el-icon><Document /></el-icon>
          <span>文章列表</span>
        </el-menu-item>
        <el-menu-item index="/subscriptions">
          <el-icon><User /></el-icon>
          <span>公众号管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="title">微信公众号文章监控系统</span>
        </div>
        <div class="header-right">
          <el-button @click="checkAuth" type="primary" :loading="checkingAuth">
            <el-icon><Key /></el-icon>
            {{ authStatus === 'logged_in' ? '已登录' : '点击登录' }}
          </el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Document, User, Setting, Key } from '@element-plus/icons-vue'
import axios from './utils/axios'

const router = useRouter()
const authStatus = ref('unknown')
const checkingAuth = ref(false)

const activeMenu = computed(() => router.currentRoute.value.path)

const checkAuth = async () => {
  checkingAuth.value = true
  try {
    const res = await axios.get('/auth/status')
    authStatus.value = res.data.status
    if (authStatus.value !== 'logged_in') {
      alert('请先运行后端的 get_cookie.py 进行扫码登录')
    }
  } catch (error) {
    authStatus.value = 'not_logged_in'
    alert('请先启动后端服务')
  } finally {
    checkingAuth.value = false
  }
}

checkAuth()
</script>

<style>
.app-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.main-content {
  background: #f5f5f5;
}
</style>