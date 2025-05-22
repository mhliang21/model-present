<template>
  <div class="history-view">
    <div class="history-header">
      <h1>历史记录</h1>
      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索历史对话..."
          prefix-icon="Search"
          clearable
          @clear="clearSearch"
        />
      </div>
    </div>
    
    <div class="history-content">
      <div v-if="filteredConversations.length === 0" class="empty-state">
        <el-icon size="48"><DocumentDelete /></el-icon>
        <p>暂无历史记录</p>
      </div>
      
      <div v-else class="conversation-list">
        <div 
          v-for="conversation in filteredConversations" 
          :key="conversation.id"
          class="conversation-item"
          @click="restoreConversation(conversation.id)"
        >
          <div class="conversation-info">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-meta">
              <span class="conversation-time">{{ formatDate(conversation.timestamp) }}</span>
              <span class="conversation-count">{{ conversation.messages.length }} 条消息</span>
            </div>
            <div class="conversation-tags">
              <el-tag size="small" type="info">模式 {{ conversation.mode }}</el-tag>
              <el-tag 
                v-for="kb in conversation.knowledgeBases" 
                :key="kb" 
                size="small" 
                type="success"
                class="kb-tag"
              >
                {{ kb }}
              </el-tag>
            </div>
          </div>
          
          <div class="conversation-actions">
            <el-button 
              type="text" 
              @click.stop="deleteConversation(conversation.id)"
              class="delete-button"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="history-footer">
      <el-button 
        type="danger" 
        @click="confirmClearAll"
        :disabled="filteredConversations.length === 0"
      >
        清空历史记录
      </el-button>
    </div>
    
    <!-- 确认对话框 -->
    <el-dialog
      v-model="showClearConfirm"
      title="确认清空"
      width="30%"
    >
      <span>确定要清空所有历史记录吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showClearConfirm = false">取消</el-button>
          <el-button type="danger" @click="clearAllHistory">确认清空</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useHistoryStore } from '@/store/history';
import { DocumentDelete, Search, Delete } from '@element-plus/icons-vue';
import { ElMessageBox } from 'element-plus';

const router = useRouter();
const historyStore = useHistoryStore();

// 状态
const searchQuery = ref('');
const showClearConfirm = ref(false);

// 计算属性
const filteredConversations = computed(() => {
  if (!searchQuery.value) {
    return historyStore.conversations;
  }
  return historyStore.searchConversations(searchQuery.value);
});

// 清除搜索
function clearSearch() {
  searchQuery.value = '';
}

// 恢复对话
function restoreConversation(id) {
  historyStore.restoreConversation(id);
  router.push('/');
}

// 删除对话
async function deleteConversation(id) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条历史记录吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    historyStore.deleteConversation(id);
  } catch {
    // 用户取消删除
  }
}

// 确认清空所有历史
function confirmClearAll() {
  showClearConfirm.value = true;
}

// 清空所有历史
function clearAllHistory() {
  historyStore.clearConversations();
  showClearConfirm.value = false;
}

// 格式化日期
function formatDate(date) {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// 组件挂载时
onMounted(() => {
  historyStore.loadConversations();
});
</script>

<style scoped>
.history-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.history-header {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
}

.history-header h1 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #303133;
}

.search-container {
  max-width: 600px;
}

.history-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  text-align: center;
}

.empty-state p {
  margin-top: 16px;
  font-size: 16px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s;
}

.conversation-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.conversation-info {
  flex: 1;
}

.conversation-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.conversation-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.conversation-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.kb-tag {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-actions {
  display: flex;
  align-items: center;
}

.delete-button {
  color: #f56c6c;
}

.delete-button:hover {
  color: #f78989;
}

.history-footer {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #e6e6e6;
  display: flex;
  justify-content: center;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .conversation-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .conversation-tags {
    margin-top: 8px;
  }
}
</style>
