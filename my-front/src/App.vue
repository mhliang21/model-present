<template>
  <div class="container">
    <div class="sidebar">
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
      </div>
      <div class="nav-menu">
        <div 
          v-for="item in navItems" 
          :key="item.id" 
          :class="['nav-item', { active: activeNav === item.id }]"
          @click="navigateTo(item.id)"
        >
          <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </div>
      </div>
    </div>
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activeNav = ref('chat');

const navItems = [
  { id: 'chat', name: '智能对话', icon: 'ChatDotRound', route: '/' },
  { id: 'knowledge', name: '知识库', icon: 'Document', route: '/knowledge' }
];

function navigateTo(id) {
  activeNav.value = id;
  const item = navItems.find(item => item.id === id);
  if (item && item.route) {
    router.push(item.route);
  }
}
</script>

<style scoped>
.logo-container {
  padding: 20px;
  text-align: center;
}

.logo {
  width: 40px;
  height: 40px;
}

.nav-menu {
  margin-top: 20px;
}

.nav-icon {
  margin-right: 8px;
}
</style>
