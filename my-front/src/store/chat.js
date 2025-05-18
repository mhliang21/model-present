import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi } from '@/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 获取消息列表
  const getMessages = computed(() => messages.value)
  
  // 发送消息
  async function sendMessage(content) {
    try {
      loading.value = true
      error.value = null
      
      // 添加用户消息到列表
      messages.value.push({
        id: Date.now(),
        content,
        isUser: true,
        timestamp: new Date()
      })
      
      // 调用API发送消息
      const response = await chatApi.sendMessage(content)
      
      // 添加助手回复到列表
      messages.value.push({
        id: Date.now() + 1,
        content: response.response,
        isUser: false,
        timestamp: new Date()
      })
      
      return response
    } catch (err) {
      error.value = err.message || '发送消息失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 清空消息
  function clearMessages() {
    messages.value = []
  }
  
  return {
    messages,
    loading,
    error,
    getMessages,
    sendMessage,
    clearMessages
  }
})
