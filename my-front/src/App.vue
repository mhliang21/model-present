<template>
  <div class="app-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 左侧导航栏 -->
    <div class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="logo">
        <span v-show="!sidebarCollapsed" class="logo-text"></span>
      </div>
      
      <!-- 新对话按钮 -->
      <div class="new-chat-button" @click="startNewChat">
        <el-icon><Plus /></el-icon>
        <span v-show="!sidebarCollapsed" class="nav-item-text">开启新对话</span>
      </div>
      
      <div class="nav-items">
        <!-- <div class="nav-item active">
          <el-icon><ChatDotRound /></el-icon>
          <span v-show="!sidebarCollapsed" class="nav-item-text">智能对话</span>
        </div>
        <div class="nav-item">
          <el-icon><Document /></el-icon>
          <span v-show="!sidebarCollapsed" class="nav-item-text">文献检索</span>
        </div>
        <div class="nav-item">
          <el-icon><DataAnalysis /></el-icon>
          <span v-show="!sidebarCollapsed" class="nav-item-text">数据分析</span>
        </div> -->
        <div class="nav-item">
          <el-icon><Clock /></el-icon>
          <span v-show="!sidebarCollapsed" class="nav-item-text">历史记录</span>
        </div>
      </div>
      
      <!-- 收缩/展开按钮 -->
      <div class="collapse-button" @click="toggleSidebar">
        <el-icon v-if="!sidebarCollapsed"><ArrowLeft /></el-icon>
        <el-icon v-else><ArrowRight /></el-icon>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useChatStore } from '@/store/chat';
import { 
  ChatDotRound, 
  Document, 
  DataAnalysis, 
  Clock, 
  ArrowLeft, 
  ArrowRight,
  Plus
} from '@element-plus/icons-vue';
import { ElMessageBox } from 'element-plus';

// 初始化store
const chatStore = useChatStore();

// 导航栏收缩状态
const sidebarCollapsed = ref(false);

// 切换导航栏收缩状态
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  // 保存状态到localStorage
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
}

// 开启新对话
function startNewChat() {
  // 如果有现有对话，先确认是否清空
  if (chatStore.messages.length > 0) {
    ElMessageBox.confirm(
      '开启新对话将清空当前对话内容，是否继续？',
      '确认操作',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
      .then(() => {
        // 用户确认后，清空对话
        chatStore.clearMessages();
        chatStore.clearSelectedKnowledgeBases();
        chatStore.setInferenceMode("1"); // 重置为默认推理模式
      })
      .catch(() => {
        // 用户取消，不执行任何操作
      });
  } else {
    // 如果没有现有对话，直接重置状态
    chatStore.clearMessages();
    chatStore.clearSelectedKnowledgeBases();
    chatStore.setInferenceMode("1");
  }
}

// 初始化时从localStorage读取状态
if (localStorage.getItem('sidebarCollapsed') === 'true') {
  sidebarCollapsed.value = true;
}
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  height: 100%;
  background-color: #f5f7fa;
  border-right: 1px solid #e6e6e6;
  transition: width 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 64px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
}

.logo .el-icon {
  font-size: 24px;
  color: #409eff;
}

.logo-text {
  margin-left: 12px;
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 0.2s ease;
}

/* 新对话按钮样式 */
.new-chat-button {
  margin: 16px;
  padding: 10px;
  background-color: #409eff;
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.new-chat-button:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.new-chat-button .el-icon {
  font-size: 18px;
}

.new-chat-button .nav-item-text {
  margin-left: 8px;
  white-space: nowrap;
  overflow: hidden;
}

.nav-items {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
  margin: 0 8px 8px 8px;
}

.nav-item:hover {
  background-color: #ecf5ff;
}

.nav-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.nav-item .el-icon {
  font-size: 18px;
}

.nav-item-text {
  margin-left: 12px;
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 0.2s ease;
}

.collapse-button {
  position: absolute;
  right: -12px;
  top: 20px;
  width: 24px;
  height: 24px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.main-content {
  flex: 1;
  overflow: hidden;
  transition: margin-left 0.3s ease;
}

.sidebar-collapsed .main-content {
  margin-left: 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;
    left: 0;
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 220px;
  }
  
  .collapse-button {
    right: 12px;
  }
}
</style>
