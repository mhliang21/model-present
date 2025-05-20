<template>
  <div class="chat-view">
    <div class="chat-header">
      <div class="chat-title">
        <h1>{{ pageTitle }}</h1>
      </div>
    </div>
    
    <div class="main-container" :class="{ 'chat-started': hasStartedChat }">
      <!-- 主对话区域 -->
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
              <!-- 思考过程和推理步骤（如果有）- 先显示 -->
              <div v-if="!message.isUser && message.inferenceSteps && message.inferenceSteps.length > 0" class="inference-steps">
                <div class="inference-steps-header">思考过程：</div>
                <div 
                  v-for="(step, index) in message.inferenceSteps" 
                  :key="index"
                  class="inference-step-item"
                >
                  <div class="inference-step-title">步骤 {{ index + 1 }}</div>
                  <div class="inference-step-content">{{ step }}</div>
                  
                  <!-- 显示对应的搜索查询（如果有） -->
                  <div v-if="message.searchQueries && message.searchQueries[index]" class="search-query">
                    <div class="search-query-title">搜索查询：</div>
                    <div class="search-query-content">{{ message.searchQueries[index] }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 消息内容 - 后显示 -->
              <div class="message-content" v-html="formatMessage(message.content)"></div>
              
              <!-- 复制按钮 - 仅在助手消息上显示 -->
              <div v-if="!message.isUser" class="message-actions">
                <el-button 
                  type="text" 
                  size="small" 
                  @click="copyMessageContent(message.content)"
                  class="copy-button"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
              
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </template>
          
          <div v-if="loading" class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在思考...</span>
          </div>
        </div>
        
        <div class="chat-input-container">
          <!-- 已选知识库展示区域 -->
          <div v-if="selectedKnowledgeBases.length > 0" class="selected-kb-container">
            <div class="selected-kb-title">已选知识库</div>
            <div class="selected-kb-list">
              <el-tag
                v-for="kb in selectedKnowledgeBases"
                :key="kb"
                closable
                @close="removeKnowledgeBase(kb)"
                class="selected-kb-tag"
              >
                {{ kb }}
              </el-tag>
            </div>
          </div>
          
          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              :placeholder="inputPlaceholder"
              resize="none"
              @keydown="handleKeyDown"
            >
            </el-input>
            
            <div class="input-actions">
              <div class="input-tools">
                <!-- 知识库选择 -->
                <el-popover
                  placement="top"
                  :width="300"
                  trigger="click"
                  popper-class="kb-popover"
                >
                  <template #reference>
                    <el-button class="tool-button">
                      <span>知识库</span>
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                  </template>
                  <div class="kb-list">
                    <div 
                      v-for="kb in knowledgeBases" 
                      :key="kb"
                      :class="['kb-item', { active: isKnowledgeBaseSelected(kb) }]"
                      @click="toggleKnowledgeBase(kb)"
                    >
                      {{ kb }}
                    </div>
                  </div>
                </el-popover>
                
                <!-- 推理模式选择 -->
                <el-popover
                  placement="top"
                  :width="300"
                  trigger="click"
                  popper-class="mode-popover"
                >
                  <template #reference>
                    <el-button class="tool-button">
                      <el-icon><Setting /></el-icon>
                      <span>推理模式</span>
                    </el-button>
                  </template>
                  <div class="mode-list">
                    <div 
                      v-for="mode in inferenceModes" 
                      :key="mode.value"
                      :class="['mode-item', { active: inferenceMode === mode.value }]"
                      @click="setInferenceMode(mode.value)"
                    >
                      <div class="mode-title">{{ mode.label }}</div>
                      <div class="mode-desc">{{ mode.description }}</div>
                    </div>
                  </div>
                </el-popover>
                
                <!-- 其他工具按钮 -->
                <el-button class="tool-button">
                  <el-icon><Paperclip /></el-icon>
                </el-button>
              </div>
              
              <el-button 
                type="primary" 
                :disabled="!inputMessage.trim() || loading" 
                @click="sendMessage"
                class="send-button"
              >
                <el-icon><Position /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧搜索结果区域 -->
      <div v-if="showSearchResults" class="search-results-sidebar">
        <div class="search-results-header">
          <h3>检索结果</h3>
          <el-button 
            type="text" 
            class="close-button"
            @click="closeSearchResults"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="search-results-content">
          <div 
            v-for="(result, resultIndex) in currentSearchResults" 
            :key="resultIndex"
            class="search-result-item"
          >
            <div class="search-result-index">{{ resultIndex }}</div>
            <div v-for="(content, title) in result" :key="title" class="search-result-entry">
              <div class="search-result-title">{{ title }}</div>
              <div class="search-result-content">{{ content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useChatStore } from '@/store/chat';
import { 
  Loading, 
  ChatDotRound, 
  Setting, 
  ArrowDown, 
  Paperclip, 
  Position,
  CopyDocument,
  Close
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 初始化store
const chatStore = useChatStore();

// 页面状态
const inputMessage = ref('');
const messagesContainer = ref(null);
const hasStartedChat = computed(() => messages.value.length > 0);
const showSearchResults = ref(false);

// 计算属性
const messages = computed(() => chatStore.messages);
const loading = computed(() => chatStore.loading);
const knowledgeBases = computed(() => chatStore.knowledgeBases);
const selectedKnowledgeBases = computed(() => chatStore.selectedKnowledgeBases);
const inferenceMode = computed(() => chatStore.inferenceMode);

// 获取当前显示的搜索结果
const currentSearchResults = computed(() => {
  if (messages.value.length === 0) return [];
  
  // 获取最后一条助手消息
  const lastAssistantMessage = [...messages.value].reverse().find(msg => !msg.isUser);
  return lastAssistantMessage?.searchResults || [];
});

// 监听搜索结果变化，有结果时自动显示侧边栏
watch(currentSearchResults, (newResults) => {
  if (newResults.length > 0) {
    showSearchResults.value = true;
  }
});

// 更新后的文本常量
const pageTitle = '智能研究助手';
const welcomeMessage = '欢迎使用智能研究助手';
const welcomeDescription = '您可以询问任何问题...';
const inputPlaceholder = '请输入您的问题，例如"请介绍蛋白质结构预测的研究方法"';

// 推理模式选项
const inferenceModes = [
  { 
    value: "1", 
    label: "直接推理", 
    description: "不使用知识库，直接使用大模型进行推理" 
  },
  { 
    value: "2", 
    label: "知识库增强", 
    description: "使用知识库，进行一次性推理" 
  },
  { 
    value: "3", 
    label: "迭代推理", 
    description: "使用知识库，进行边推理边检索" 
  }
];

// 发送消息
async function sendMessage() {
  if (!inputMessage.value.trim() || loading.value) return;
  
  // 检查推理模式2和3是否选择了知识库
  if ((inferenceMode.value === "2" || inferenceMode.value === "3") && selectedKnowledgeBases.value.length === 0) {
    ElMessage.warning('当前推理模式需要至少选择一个知识库');
    return;
  }
  
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

// 设置推理模式
function setInferenceMode(mode) {
  chatStore.setInferenceMode(mode);
}

// 切换知识库选择
function toggleKnowledgeBase(kb) {
  chatStore.toggleKnowledgeBase(kb);
}

// 移除已选知识库
function removeKnowledgeBase(kb) {
  chatStore.toggleKnowledgeBase(kb);
}

// 检查知识库是否已选择
function isKnowledgeBaseSelected(kb) {
  return selectedKnowledgeBases.value.includes(kb);
}

// 复制消息内容
function copyMessageContent(content) {
  // 使用Clipboard API复制文本
  navigator.clipboard.writeText(content)
    .then(() => {
      ElMessage.success('已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动选择文本复制');
    });
}

// 关闭搜索结果侧边栏
function closeSearchResults() {
  showSearchResults.value = false;
}

// 处理键盘事件
function handleKeyDown(e) {
  // Enter发送消息，Alt+Enter换行
  if (e.key === 'Enter') {
    if (e.altKey) {
      // Alt+Enter换行，不阻止默认行为
      return;
    } else {
      // Enter发送消息
      e.preventDefault();
      sendMessage();
    }
  }
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

// 组件挂载时
onMounted(async () => {
  try {
    // 获取知识库列表
    await chatStore.fetchKnowledgeBases();
  } catch (error) {
    console.error('获取知识库列表失败:', error);
  }
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

.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  transition: all 0.5s ease;
}

/* 初始状态：对话框居中 */
.main-container:not(.chat-started) {
  justify-content: center;
  align-items: center;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  transition: all 0.5s ease;
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #f5f7fa;
  width: 100%;
  max-width: 100%;
  transition: all 0.5s ease;
}

/* 初始状态：消息容器居中 */
.main-container:not(.chat-started) .chat-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

.message-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.copy-button {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.copy-button:hover {
  color: #409eff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.chat-input-container {
  background-color: #fff;
  border-top: 1px solid #e6e6e6;
  padding: 16px 24px;
  transition: all 0.3s ease;
}

.selected-kb-container {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.selected-kb-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.selected-kb-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selected-kb-tag {
  margin-right: 0;
}

.chat-input {
  width: 100%;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-tools {
  display: flex;
  gap: 8px;
}

.tool-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  text-align: center;
  padding: 20px;
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

.kb-list, .mode-list {
  max-height: 300px;
  overflow-y: auto;
}

.kb-item, .mode-item {
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 4px;
  transition: background-color 0.3s;
}

.kb-item:hover, .mode-item:hover {
  background-color: #f5f7fa;
}

.kb-item.active, .mode-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.mode-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 12px;
  color: #909399;
}

/* 右侧搜索结果侧边栏 */
.search-results-sidebar {
  width: 300px;
  border-left: 1px solid #e6e6e6;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease;
}

.search-results-header {
  padding: 16px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-results-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.close-button {
  padding: 4px;
  color: #909399;
}

.close-button:hover {
  color: #409eff;
}

.search-results-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.search-result-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  position: relative;
}

.search-result-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.search-result-index {
  position: absolute;
  top: -8px;
  left: -8px;
  background-color: #409eff;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.search-result-entry {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
}

.search-result-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
  border-bottom: 1px dashed #e0e0e0;
  padding-bottom: 4px;
}

.search-result-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 思考过程和推理步骤 */
.inference-steps {
  margin-bottom: 12px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
}

.inference-steps-header {
  font-weight: bold;
  margin-bottom: 8px;
  color: #606266;
}

.inference-step-item {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e0e0e0;
}

.inference-step-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
}

.search-query {
  margin-top: 8px;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 13px;
}

.search-query-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #606266;
}

/* 发送按钮样式优化 */
.send-button {
  background-color: #409eff;
  border-color: #409eff;
  font-weight: bold;
  padding: 10px 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.send-button:hover {
  background-color: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.send-button:active {
  transform: translateY(0);
}

.send-button .el-icon {
  font-size: 16px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  
  .search-results-sidebar {
    width: 100%;
    height: 300px;
    border-left: none;
    border-top: 1px solid #e6e6e6;
  }
  
  .message {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 12px;
  }
  
  .input-tools {
    flex-wrap: wrap;
  }
}
</style>
