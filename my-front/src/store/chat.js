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
  
  // 更新消息的思考过程（用于结构化流式响应）
  function updateMessageThinking(messageId, content, append = true) {
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      if (!message.thinking) {
        message.thinking = content
      } else if (append) {
        message.thinking += content
      } else {
        message.thinking = content
      }
    }
  }
  
  // 更新消息的搜索结果（用于结构化流式响应）
  function updateMessageSearchResults(messageId, searchResults) {
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      message.searchResults = searchResults
    }
  }
  
  // 更新消息的搜索查询（用于结构化流式响应）
  function updateMessageSearchQueries(messageId, query, append = true) {
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      if (!message.searchQueries) {
        message.searchQueries = [query]
      } else if (append) {
        message.searchQueries.push(query)
      }
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
  
  // 发送流式消息 - 更新为支持结构化JSON流式响应
  async function sendStreamingMessage(content, mode, knowledgeBases, messageId, onChunk) {
    try {
      loading.value = true
      error.value = null
      
      // 初始化消息的额外字段
      const message = messages.value.find(msg => msg.id === messageId)
      if (message) {
        message.thinking = ''
        message.searchResults = []
        message.searchQueries = []
        message.inferenceSteps = []
      }
      
      // 调用API发送流式消息，传递结构化处理回调
      await chatApi.sendStreamingMessage(
        content,
        mode,
        knowledgeBases,
        (chunkContent, metadata) => {
          // 根据消息类型处理不同的内容
          if (!metadata || !metadata.type) {
            // 兼容旧版纯文本流
            if (onChunk && typeof onChunk === 'function') {
              onChunk(chunkContent)
            }
            return
          }
          
          switch (metadata.type) {
            case 'thinking':
              // 更新思考过程
              updateMessageThinking(messageId, chunkContent, true)
              // 同时更新推理步骤（用于模式3）
              if (metadata.turn && message) {
                if (!message.inferenceSteps) {
                  message.inferenceSteps = []
                }
                
                if (message.inferenceSteps.length < metadata.turn) {
                  message.inferenceSteps.push(chunkContent)
                } else {
                  message.inferenceSteps[metadata.turn - 1] += chunkContent
                }
              }
              break
              
            case 'answer':
              // 更新回答内容
              if (onChunk && typeof onChunk === 'function') {
                onChunk(chunkContent)
              }
              break
              
            case 'system':
              // 系统消息，可以选择性显示
              console.log('系统消息:', chunkContent)
              break
              
            case 'search_results':
              // 更新搜索结果
              if (metadata.documents) {
                updateMessageSearchResults(messageId, metadata.documents)
              }
              break
              
            case 'search_query':
              // 更新搜索查询
              updateMessageSearchQueries(messageId, chunkContent)
              break
              
            case 'final_answer':
              // 最终答案
              if (onChunk && typeof onChunk === 'function') {
                onChunk(chunkContent)
              }
              
              // 更新额外信息
              if (metadata.search_queries) {
                message.searchQueries = metadata.search_queries
              }
              
              if (metadata.search_results) {
                message.searchResults = metadata.search_results
              }
              break
              
            case 'error':
              // 错误信息
              error.value = chunkContent
              console.error('流式响应错误:', chunkContent)
              break
              
            default:
              // 未知类型，直接传递
              if (onChunk && typeof onChunk === 'function') {
                onChunk(chunkContent)
              }
          }
        }
      )
      
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
    // 清空选中的知识库
    clearSelectedKnowledgeBases()
    // 重置推理模式为默认值
    setInferenceMode("1")
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
    updateMessageThinking,
    updateMessageSearchResults,
    updateMessageSearchQueries,
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
