<template>
    <div class="chat-view">
      <div class="chat-header">
        <div class="chat-title">
          <h1>{{ pageTitle }}</h1>
        </div>
      </div>
      
      <div class="chat-container">
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="welcome-message">
              <el-icon size="64"><ChatDotRound /></el-icon>
              <h2>{{ welcomeMessage }}</h2>
              <p>{{ welcomeDescription }}</p>
            </div>
          </div>
          
          <template v-else>
            <div 
              v-for="message in messages" 
              :key="message.id"
              :class="['message', message.isUser ? 'message-user' : 'message-assistant']"
            >
              <div class="message-content" v-html="formatMessage(message.content)"></div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </template>
          
          <div v-if="loading" class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在思考...</span>
          </div>
        </div>
        
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            :placeholder="inputPlaceholder"
            resize="none"
            @keydown.enter.ctrl.prevent="sendMessage"
          >
          </el-input>
          <div class="input-actions">
            <el-button 
              type="primary" 
              :disabled="!inputMessage.trim() || loading" 
              @click="sendMessage"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
      
      <div class="knowledge-sidebar">
        <div class="knowledge-header">
          <h3>知识库</h3>
          <el-input
            v-model="searchQuery"
            placeholder="搜索知识库..."
            prefix-icon="Search"
            clearable
          ></el-input>
        </div>
        
        <div class="knowledge-list">
          <div 
            v-for="item in filteredKnowledgeItems" 
            :key="item.id"
            class="knowledge-card"
            @click="useKnowledgeItem(item)"
          >
            <h4>{{ item.title }}</h4>
            <p>{{ truncateText(item.content, 100) }}</p>
            <div class="knowledge-meta">
              <span class="knowledge-category">{{ item.category }}</span>
            </div>
          </div>
          
          <div v-if="filteredKnowledgeItems.length === 0" class="empty-knowledge">
            <p>暂无相关知识条目</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, nextTick, watch } from 'vue';
  import { useChatStore } from '@/store/chat';
  import { Loading, ChatDotRound, Search } from '@element-plus/icons-vue';
  import { ElMessage } from 'element-plus';
  
  // 初始化store
  const chatStore = useChatStore();
  
  // 页面状态
  const inputMessage = ref('');
  const messagesContainer = ref(null);
  const searchQuery = ref('');
  
  // 计算属性
  const messages = computed(() => chatStore.messages);
  const loading = computed(() => chatStore.loading);
  
  const pageTitle = '蛋白质结构预测研究';
  const welcomeMessage = '欢迎使用智能研究助手';
  const welcomeDescription = '您可以询问关于蛋白质结构预测的任何问题...';
  const inputPlaceholder = '请输入您的问题，例如"请介绍蛋白质结构预测的研究方法"';
  
  // 预设知识库条目
  const knowledgeItems = [
    {
      id: 1,
      title: '蛋白质结构预测概述',
      category: '基础知识',
      content: '蛋白质结构预测是生物信息学中的重要问题，深度学习方法在这一领域取得了显著进展。特别是AlphaFold2等模型的出现，大大提高了预测精度。'
    },
    {
      id: 2,
      title: '深度学习在蛋白质结构预测中的应用',
      category: '研究方法',
      content: '深度学习在蛋白质结构预测中的应用主要包括：使用CNN预测接触图谱、使用RNN处理序列信息、应用注意力机制捕捉长程依赖关系等。这些方法极大地提高了预测精度。'
    },
    {
      id: 3,
      title: 'AlphaFold2技术解析',
      category: '前沿技术',
      content: 'AlphaFold2是DeepMind开发的蛋白质结构预测模型，在CASP14比赛中取得了突破性成果。它使用注意力机制和深度学习方法，能够准确预测蛋白质的三维结构，精度接近实验方法。'
    },
    {
      id: 4,
      title: '蛋白质结构预测的应用领域',
      category: '应用',
      content: '蛋白质结构预测的应用包括：药物设计、疾病机理研究、酶工程、疫苗开发等。通过了解蛋白质的三维结构，科学家可以更好地理解其功能并设计针对性的干预方法。'
    }
  ];
  
  // 过滤知识条目
  const filteredKnowledgeItems = computed(() => {
    if (!searchQuery.value) {
      return knowledgeItems;
    }
    
    const query = searchQuery.value.toLowerCase();
    return knowledgeItems.filter(item => 
      item.title.toLowerCase().includes(query) || 
      item.content.toLowerCase().includes(query) ||
      item.category.toLowerCase().includes(query)
    );
  });
  
  // 发送消息
  async function sendMessage() {
    if (!inputMessage.value.trim() || loading.value) return;
    
    try {
      await chatStore.sendMessage(inputMessage.value);
      inputMessage.value = '';
      
      // 滚动到底部
      await nextTick();
      scrollToBottom();
    } catch (error) {
      ElMessage.error('发送消息失败，请重试');
      console.error(error);
    }
  }
  
  // 使用知识条目
  function useKnowledgeItem(item) {
    inputMessage.value = `请详细介绍${item.title}`;
  }
  
  // 格式化消息内容（支持简单的Markdown）
  function formatMessage(content) {
    // 简单的Markdown转HTML实现
    return content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  }
  
  // 格式化时间
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  // 截断文本
  function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
  
  // 滚动到底部
  function scrollToBottom() {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  }
  
  // 监听消息变化，自动滚动
  watch(messages, () => {
    nextTick(() => scrollToBottom());
  });
  </script>
  
  <style scoped>
  .chat-view {
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: relative;
  }
  
  .chat-header {
    padding: 16px 24px;
    background-color: #fff;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .chat-messages {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    background-color: #f5f7fa;
  }
  
  .message {
    margin-bottom: 16px;
    max-width: 70%;
    position: relative;
  }
  
  .message-user {
    margin-left: auto;
    background-color: #ecf5ff;
    border-radius: 8px 0 8px 8px;
    padding: 12px 16px;
  }
  
  .message-assistant {
    margin-right: auto;
    background-color: #fff;
    border-radius: 0 8px 8px 8px;
    padding: 12px 16px;
    border: 1px solid #e6e6e6;
  }
  
  .message-content {
    word-break: break-word;
  }
  
  .message-time {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
    text-align: right;
  }
  
  .chat-input {
    position: relative; /* 确保输入区域层级 */
    z-index: 100;
    padding: 16px 24px;
    background-color: #fff;
    border-top: 1px solid #e6e6e6;
    display: flex;
    flex-direction: column;
  }

  .input-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 8px;
    /* 添加间距防止被遮挡 */
    padding-bottom: 8px;
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #909399;
  }
  
  .welcome-message {
    text-align: center;
    max-width: 500px;
  }
  
  .loading-indicator {
    display: flex;
    align-items: center;
    color: #909399;
    margin: 16px 0;
  }
  
  .loading-indicator .el-icon {
    margin-right: 8px;
  }
  
  .chat-container {
    margin-right: 320px; /* 与侧边栏宽度一致 */
  }

  .knowledge-sidebar {
    position: fixed; /* 改为 fixed 定位 */
    top: 0;
    right: 0;
    width: 320px;
    height: 100vh; /* 确保高度占满整个视口 */
    /* 添加 z-index 确保层级 */
    z-index: 1000;
  }
  
  .knowledge-header {
    padding: 16px;
    border-bottom: 1px solid #e6e6e6;
  }
  
  .knowledge-header h3 {
    margin-bottom: 16px;
  }
  
  .knowledge-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
  
  .knowledge-card {
    background-color: #f5f7fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  .knowledge-card:hover {
    background-color: #ecf5ff;
    transform: translateY(-2px);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .knowledge-card h4 {
    margin-bottom: 8px;
  }
  
  .knowledge-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
  
  .empty-knowledge {
    text-align: center;
    color: #909399;
    padding: 32px 0;
  }

  
  </style>
  