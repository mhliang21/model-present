import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
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
  
  // 添加消息
  function addMessage(message) {
    messages.value.push(message)
  }
  
  // 更新消息内容（用于流式响应）
  function updateMessageContent(messageId, content) {
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      message.content = content
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
      
      // 检查是否有错误
      if (response.error) {
        error.value = response.error
        throw new Error(response.error)
      }
      
      // 添加助手回复到列表
      messages.value.push({
        id: Date.now() + 1,
        content: response.response,
        isUser: false,
        timestamp: new Date(),
        // 根据不同推理模式，可能包含额外信息
        searchResults: response.search_results || [],
        inferenceSteps: response.inference_steps || [],
        searchQueries: response.search_queries || []
      })
      
      return response
    } catch (err) {
      error.value = err.message || '发送消息失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 发送流式消息
  async function sendStreamingMessage(content, mode, knowledgeBases, messageId, onChunk) {
    try {
      loading.value = true
      error.value = null
      
      // 调用API发送流式消息
      await chatApi.sendStreamingMessage(
        content,
        mode,
        knowledgeBases,
        onChunk
      )
      
      // 流式响应结束后，更新消息的额外信息（如检索结果）
      // 这里模拟一些检索结果，实际应该从后端获取
      if (mode === "2" || mode === "3") {
        const message = messages.value.find(msg => msg.id === messageId)
        if (message) {
          // 模拟检索结果
          message.searchResults = [
            {"文档1": "内容1-----------------------------------"},
            {"文档2": "内容2-----------------------------------"},
            {"文档3": "内容3-----------------------------------"}
          ]
          
          // 模式3还需要添加推理步骤和搜索查询
          if (mode === "3") {
            message.inferenceSteps = [
              "推理结果1-----------------------------------",
              "推理结果2-----------------------------------",
              "推理结果3-----------------------------------"
            ]
            message.searchQueries = [
              "检索的query1-----------------------------------",
              "检索的query2-----------------------------------",
              "检索的query3-----------------------------------"
            ]
          }
        }
      }
      
      return true
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
  
  // 设置消息列表（用于恢复历史对话）
  function setMessages(newMessages) {
    messages.value = newMessages
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
  
  // 开启新对话
  function startNewChat() {
    // 清空消息
    clearMessages()
    // 关闭检索结果
    return true
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
    addMessage,
    updateMessageContent,
    sendMessage,
    sendStreamingMessage,
    clearMessages,
    setMessages,
    setInferenceMode,
    toggleKnowledgeBase,
    clearSelectedKnowledgeBases,
    startNewChat
  }
})
