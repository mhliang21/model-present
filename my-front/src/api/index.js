import axios from 'axios'

// 创建API客户端实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 聊天相关API
export const chatApi = {
  // 获取知识库名称列表
  async getKnowledgeBaseNames() {
    const response = await apiClient.get('/api/knowledge/list')
    return response.data
  },
  
  // 发送消息
  async sendMessage(content, mode = "1", knowledgeBases = []) {
    const response = await apiClient.post('/api/chat', {
      content, // 修改：使用content作为参数名，与后端一致
      mode,
      kb_names: knowledgeBases
    })
    return response.data
  },
  
  // 发送流式消息
  async sendStreamingMessage(content, mode = "1", knowledgeBases = [], onChunk) {
    // 使用fetch API进行流式请求
    const response = await fetch(`${apiClient.defaults.baseURL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content, // 修改：使用content作为参数名，与后端一致
        mode,
        kb_names: knowledgeBases
      }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // 获取响应的可读流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    // 读取流数据
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        break
      }
      
      // 解码并处理数据块
      const chunk = decoder.decode(value, { stream: true })
      
      // 调用回调函数处理数据块
      if (onChunk && typeof onChunk === 'function') {
        onChunk(chunk)
      }
    }
    
    return true
  }
}

// 知识库相关API
export const knowledgeApi = {
  // 获取知识库列表
  async getKnowledgeBases() {
    const response = await apiClient.get('/api/knowledge')
    return response.data
  },
  
  // 获取知识库详情
  async getKnowledgeBase(id) {
    const response = await apiClient.get(`/api/knowledge/${id}`)
    return response.data
  }
}

export default {
  chatApi,
  knowledgeApi
}
