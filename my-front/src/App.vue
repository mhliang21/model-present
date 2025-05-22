<template>
  <div class="app-container">
    <div class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
        <button 
          type="button" 
          class="collapse-button"
          @click="toggleSidebar"
        >
          <!-- 优化：增大伸缩展开图标尺寸和可点击区域 -->
          <el-icon v-if="sidebarCollapsed" :size="24"><ArrowRight /></el-icon>
          <el-icon v-else :size="24"><ArrowLeft /></el-icon>
        </button>
      </div>
      
      <div class="sidebar-content">
        <!-- 新对话按钮 -->
        <el-button 
          class="new-chat-button" 
          @click="startNewChat"
        >
          <el-icon><Plus /></el-icon>
          <span v-if="!sidebarCollapsed">新对话</span>
        </el-button>
        
        <!-- 导航菜单 -->
        <div class="nav-menu">
          <router-link to="/" class="nav-item" active-class="active">
            <el-icon><ChatDotRound /></el-icon>
            <span v-if="!sidebarCollapsed">智能对话</span>
          </router-link>
          
          <router-link to="/history" class="nav-item" active-class="active">
            <el-icon><Clock /></el-icon>
            <span v-if="!sidebarCollapsed">历史记录</span>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useChatStore } from '@/store/chat';
import { ElMessageBox } from 'element-plus';
import { 
  ArrowLeft, 
  ArrowRight, 
  Plus, 
  ChatDotRound, 
  Clock 
} from '@element-plus/icons-vue';

const router = useRouter();
const chatStore = useChatStore();

// 侧边栏状态
const sidebarCollapsed = ref(false);

// 切换侧边栏展开/收起
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  // 保存状态到本地存储
  localStorage.setItem('sidebar-collapsed', sidebarCollapsed.value);
}

// 开始新对话
async function startNewChat() {
  // 如果当前有对话，显示确认对话框
  if (chatStore.messages.length > 0) {
    try {
      await ElMessageBox.confirm(
        '开始新对话将清空当前对话内容，确定继续吗？',
        '确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      );
      
      // 用户确认，清空当前对话
      chatStore.clearMessages();
      
      // 导航到聊天页面
      router.push('/');
    } catch {
      // 用户取消，不执行任何操作
    }
  } else {
    // 没有对话，直接导航到聊天页面
    router.push('/');
  }
}

// 组件挂载时，从本地存储读取侧边栏状态
if (typeof localStorage !== 'undefined') {
  const savedState = localStorage.getItem('sidebar-collapsed');
  if (savedState !== null) {
    sidebarCollapsed.value = savedState === 'true';
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background-color: #304156;
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  position: relative;
  z-index: 10;
  overflow: visible !important; /* 强制显示溢出内容 */
}

.sidebar.collapsed {
  width: 128px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  height: 32px;
  width: auto;
}

/* 优化：增大伸缩按钮的可点击区域和视觉效果 */
.collapse-button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.collapse-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  overflow-y: auto;
}

.new-chat-button {
  margin: 0 16px 16px;
  background-color: #409eff;
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.new-chat-button:hover {
  background-color: #66b1ff;
}

.nav-menu {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #e0e0e0;
  text-decoration: none;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background-color: rgba(64, 158, 255, 0.2);
  color: #409eff;
}

.main-content {
  flex: 1;
  overflow: hidden;
  transition: margin-left 0.3s;
}

.main-content.sidebar-collapsed {
  margin-left: -176px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100%;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
}
</style>
