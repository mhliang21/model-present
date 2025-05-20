import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    return Promise.reject(error)
  }
)

// 聊天相关API
export const chatApi = {
  // 发送消息
  sendMessage(content, mode = "1", kb_names = []) {
    return api.post('/chat/message', { content, mode, kb_names })
  },
  
  // 获取知识库列表
  getKnowledgeBaseNames() {
    return api.get('/get_knowledge_base_names')
  }
}
