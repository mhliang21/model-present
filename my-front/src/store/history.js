import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useHistoryStore = defineStore('history', () => {
  // 状态
  const conversations = ref([])
  const restoredConversation = ref(null)
  
  // 本地存储键名
  const STORAGE_KEY = 'ai-research-assistant-history'
  
  // 加载所有对话历史
  function loadConversations() {
    try {
      const storedData = localStorage.getItem(STORAGE_KEY)
      if (storedData) {
        conversations.value = JSON.parse(storedData)
        
        // 修复日期对象（JSON.parse不会自动转换日期字符串为Date对象）
        conversations.value.forEach(conv => {
          conv.timestamp = new Date(conv.timestamp)
          conv.messages.forEach(msg => {
            msg.timestamp = new Date(msg.timestamp)
          })
        })
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
      // 如果加载失败，初始化为空数组
      conversations.value = []
    }
  }
  
  // 保存对话历史到本地存储
  function saveConversations() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.value))
    } catch (error) {
      console.error('保存历史记录失败:', error)
    }
  }
  
  // 添加新对话
  function saveConversation(conversation) {
    // 检查是否已存在相同ID的对话
    const existingIndex = conversations.value.findIndex(c => c.id === conversation.id)
    
    if (existingIndex !== -1) {
      // 更新已有对话
      conversations.value[existingIndex] = conversation
    } else {
      // 添加新对话
      conversations.value.unshift(conversation)
    }
    
    // 限制历史记录数量，最多保存50条
    if (conversations.value.length > 50) {
      conversations.value = conversations.value.slice(0, 50)
    }
    
    // 保存到本地存储
    saveConversations()
  }
  
  // 删除对话
  function deleteConversation(id) {
    conversations.value = conversations.value.filter(c => c.id !== id)
    saveConversations()
  }
  
  // 清空所有对话历史
  function clearConversations() {
    conversations.value = []
    saveConversations()
  }
  
  // 搜索对话历史
  function searchConversations(query) {
    if (!query || query.trim() === '') {
      return conversations.value
    }
    
    const normalizedQuery = query.toLowerCase().trim()
    
    return conversations.value.filter(conv => {
      // 搜索标题
      if (conv.title.toLowerCase().includes(normalizedQuery)) {
        return true
      }
      
      // 搜索消息内容
      return conv.messages.some(msg => 
        msg.content.toLowerCase().includes(normalizedQuery)
      )
    })
  }
  
  // 恢复对话
  function restoreConversation(id) {
    const conversation = conversations.value.find(c => c.id === id)
    if (conversation) {
      restoredConversation.value = { ...conversation }
    }
  }
  
  // 清除恢复标记
  function clearRestoredConversation() {
    restoredConversation.value = null
  }
  
  return {
    conversations,
    restoredConversation,
    loadConversations,
    saveConversation,
    deleteConversation,
    clearConversations,
    searchConversations,
    restoreConversation,
    clearRestoredConversation
  }
})
