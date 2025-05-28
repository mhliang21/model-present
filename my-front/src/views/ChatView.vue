<template>
  <div class="chat-view">
    <div class="main-container" :class="{ 'chat-started': hasStartedChat }">
      <!-- 主对话区域 -->
      <div class="chat-container">
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="welcome-message">
              <el-icon size="48"><ChatDotRound /></el-icon>
              <h2>{{ welcomeMessage }}</h2>
              <p>{{ welcomeDescription }}</p>
              
              <!-- 初始状态下将输入框置于中部，优化：扩大输入框尺寸 -->
              <div class="initial-input-container">
                <el-input
                  v-model="inputMessage"
                  type="textarea"
                  :rows="5"
                  :placeholder="inputPlaceholder"
                  resize="none"
                  @keydown="handleKeyDown"
                  class="initial-input"
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

                    <!-- 上传文件工具按钮 -->
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
        
        <!-- 对话开始后的输入框区域 -->
        <div v-if="hasStartedChat" class="chat-input-container">
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
                
                <!-- 上传文件工具按钮 -->
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
      <div v-if="showSearchResults && currentSearchResults.length > 0" class="search-results-sidebar">
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
            <div class="search-result-index">{{ resultIndex + 1 }}</div>
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
import { useHistoryStore } from '@/store/history';
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
const historyStore = useHistoryStore();

// 页面状态
const inputMessage = ref('');
const messagesContainer = ref(null);
const hasStartedChat = computed(() => messages.value.length > 0);
const showSearchResults = ref(false);
const streamingResponse = ref(false);
const currentStreamingMessage = ref('');

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
  
  if (lastAssistantMessage?.searchResults && Array.isArray(lastAssistantMessage.searchResults)) {
    return lastAssistantMessage.searchResults;
  }
  
  return [];
});


// 监听搜索结果变化，有结果时自动显示侧边栏
watch(currentSearchResults, (newResults) => {
  if (newResults && newResults.length > 0) {
    showSearchResults.value = true;
  }
});

// 更新后的文本常量
const welcomeMessage = '下午好，张博士';
const welcomeDescription = '欢迎使用智能研究助手';
const inputPlaceholder = '尽管提问...';
const userManuallyClosed = ref(false);

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
  userManuallyClosed.value = false; // 重置手动关闭标记
  if (!inputMessage.value.trim() || loading.value) return;
  
  // 检查推理模式2和3是否选择了知识库
  if ((inferenceMode.value === "2" || inferenceMode.value === "3") && selectedKnowledgeBases.value.length === 0) {
    ElMessage.warning('当前推理模式需要至少选择一个知识库');
    return;
  }
  
  try {
    const userMessage = inputMessage.value;
    inputMessage.value = '';
    
    // 添加用户消息到列表
    const userMessageObj = {
      id: Date.now(),
      content: userMessage,
      isUser: true,
      timestamp: new Date()
    };
    
    chatStore.addMessage(userMessageObj);
    
    // 准备接收流式响应
    streamingResponse.value = true;
    currentStreamingMessage.value = '';
    
    // 添加一个空的助手消息，用于流式更新
    const assistantMessageId = Date.now() + 1;
    const assistantMessageObj = {
      id: assistantMessageId,
      content: '',
      isUser: false,
      timestamp: new Date(),
      searchResults: [],
      inferenceSteps: [],
      searchQueries: []
    };
    
    chatStore.addMessage(assistantMessageObj);
    
    // 滚动到底部
    await nextTick();
    scrollToBottom();
    
    // 调用API发送消息，传递推理模式和选中的知识库
    await chatStore.sendStreamingMessage(
      userMessage, 
      inferenceMode.value, 
      selectedKnowledgeBases.value,
      assistantMessageId,
      (chunk) => {
        // 更新流式响应
        currentStreamingMessage.value += chunk;
        chatStore.updateMessageContent(assistantMessageId, currentStreamingMessage.value);
        
        // 滚动到底部
        nextTick(() => scrollToBottom());
      }
    );
    
    // 流式响应结束
    streamingResponse.value = false;
    
    // 保存对话历史到本地存储
    historyStore.saveConversation({
      id: Date.now().toString(),
      title: userMessage.slice(0, 30) + (userMessage.length > 30 ? '...' : ''),
      messages: chatStore.messages,
      timestamp: new Date(),
      mode: inferenceMode.value,
      knowledgeBases: [...selectedKnowledgeBases.value]
    });
    
  } catch (error) {
    ElMessage.error('发送消息失败，请重试');
    console.error(error);
    streamingResponse.value = false;
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
  userManuallyClosed.value = true; // 标记用户手动关闭
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
    
    // 恢复历史对话（如果有）
    if (historyStore.restoredConversation) {
      const conversation = historyStore.restoredConversation;
      chatStore.setMessages(conversation.messages);
      chatStore.setInferenceMode(conversation.mode || "1");
      
      // 恢复选中的知识库
      chatStore.clearSelectedKnowledgeBases();
      if (conversation.knowledgeBases && conversation.knowledgeBases.length > 0) {
        conversation.knowledgeBases.forEach(kb => {
          chatStore.toggleKnowledgeBase(kb);
        });
      }
      
      // 清除恢复标记
      historyStore.clearRestoredConversation();
    }
  } catch (error) {
    console.error('初始化失败:', error);
    ElMessage.error('初始化失败，请刷新页面重试');
  }
});
</script>

<style scoped>
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 空状态容器高度 */
.empty-state {
  min-height: 400px;
  height: 70vh;
}

.welcome-message {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.welcome-message h2 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 24px;
  color: #303133;
}

.welcome-message p {
  margin-bottom: 30px;
  color: #606266;
}

/* 优化：扩大初始输入框尺寸和样式 */
.initial-input-container {
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
}

.initial-input {
  margin-bottom: 10px;
}

.initial-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  font-size: 16px;
  padding: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
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

.send-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.message {
  margin-bottom: 20px;
  max-width: 85%;
  position: relative;
}

.message-user {
  margin-left: auto;
  text-align: right;
}

.message-assistant {
  margin-right: auto;
  text-align: left;
}

.message-content {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 4px;
  display: inline-block;
  max-width: 100%;
  text-align: left;
  word-break: break-word;
}

.message-user .message-content {
  background-color: #409eff;
  color: white;
}

.message-assistant .message-content {
  background-color: #f4f4f5;
  color: #303133;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.message-actions {
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
}

.copy-button {
  font-size: 12px;
  padding: 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  margin: 10px 0;
}

.chat-input-container {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background-color: white;
}

.chat-input {
  display: flex;
  flex-direction: column;
}

.selected-kb-container {
  margin-bottom: 10px;
}

.selected-kb-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.selected-kb-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.selected-kb-tag {
  margin-right: 4px;
}

/* 推理模式弹出框样式 */
:deep(.mode-popover) {
  padding: 0;
}

.mode-list {
  max-height: 300px;
  overflow-y: auto;
}

.mode-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ebeef5;
}

.mode-item:last-child {
  border-bottom: none;
}

.mode-item:hover {
  background-color: #f5f7fa;
}

.mode-item.active {
  background-color: #ecf5ff;
}

.mode-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 12px;
  color: #909399;
}

/* 知识库弹出框样式 */
:deep(.kb-popover) {
  padding: 0;
}

.kb-list {
  max-height: 300px;
  overflow-y: auto;
}

.kb-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ebeef5;
}

.kb-item:last-child {
  border-bottom: none;
}

.kb-item:hover {
  background-color: #f5f7fa;
}

.kb-item.active {
  background-color: #ecf5ff;
}

/* 推理步骤样式 */
.inference-steps {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.inference-steps-header {
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
}

.inference-step-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #dcdfe6;
}

.inference-step-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.inference-step-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #409eff;
}

.inference-step-content {
  margin-bottom: 8px;
}

.search-query {
  background-color: #f0f9eb;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
}

.search-query-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #67c23a;
}

/* 搜索结果侧边栏样式 */
.search-results-sidebar {
  width: 300px;
  border-left: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.search-results-header {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-results-header h3 {
  margin: 0;
  font-size: 16px;
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
}

.search-result-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.search-result-index {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  margin-bottom: 8px;
}

.search-result-entry {
  margin-bottom: 8px;
}

.search-result-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.search-result-content {
  color: #606266;
  font-size: 14px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .search-results-sidebar {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15);
  }
  
  .message {
    max-width: 90%;
  }
}
</style>