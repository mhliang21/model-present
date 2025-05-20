import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { chatApi } from '@/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)
  const knowledgeBases = ref([])
  const selectedKnowledgeBases = ref([])
  const inferenceMode = ref("1") // 默认使用模式1
  
  // 获取消息列表
  const getMessages = computed(() => messages.value)
  
  // 获取知识库列表
  async function fetchKnowledgeBases() {
    try {
      const response = await chatApi.getKnowledgeBaseNames()
      knowledgeBases.value = response.message || []
      return knowledgeBases.value
    } catch (err) {
      error.value = err.message || '获取知识库列表失败'
      throw err
    }
  }
  
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
      
      // 调用API发送消息，传递推理模式和选中的知识库
      const response = await chatApi.sendMessage(
        content, 
        inferenceMode.value, 
        selectedKnowledgeBases.value
      )
      
      // 添加助手回复到列表
      messages.value.push({
        id: Date.now() + 1,
        content: response.response,
        isUser: false,
        timestamp: new Date(),
        // 根据不同推理模式，可能包含额外信息
        searchResults: response.search_results,
        inferenceSteps: response.inference_steps,
        searchQueries: response.search_queries
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
  
  // 设置推理模式
  function setInferenceMode(mode) {
    inferenceMode.value = mode
  }
  
  // 选择知识库
  function toggleKnowledgeBase(kbName) {
    const index = selectedKnowledgeBases.value.indexOf(kbName)
    if (index === -1) {
      selectedKnowledgeBases.value.push(kbName)
    } else {
      selectedKnowledgeBases.value.splice(index, 1)
    }
  }
  
  // 清空选中的知识库
  function clearSelectedKnowledgeBases() {
    selectedKnowledgeBases.value = []
  }
  
  return {
    messages,
    loading,
    error,
    knowledgeBases,
    selectedKnowledgeBases,
    inferenceMode,
    getMessages,
    fetchKnowledgeBases,
    sendMessage,
    clearMessages,
    setInferenceMode,
    toggleKnowledgeBase,
    clearSelectedKnowledgeBases
  }
})
