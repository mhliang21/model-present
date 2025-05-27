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
  
  // 发送流式消息 - 更新为支持结构化JSON流式输出
  async sendStreamingMessage(content, mode = "1", knowledgeBases = [], onChunk) {
    // 使用fetch API进行流式请求
    const response = await fetch(`${apiClient.defaults.baseURL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/x-ndjson' // 指定接受NDJSON格式
      },
      body: JSON.stringify({
        content,
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
    
    // 用于处理不完整行的缓冲区
    let buffer = '';
    
    // 读取流数据
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        // 处理缓冲区中可能剩余的数据
        if (buffer.trim()) {
          try {
            const jsonData = JSON.parse(buffer.trim());
            processStreamChunk(jsonData, onChunk);
          } catch (e) {
            console.error('解析最终缓冲区数据失败:', e);
            // 作为纯文本处理
            if (onChunk && typeof onChunk === 'function') {
              onChunk(buffer);
            }
          }
        }
        break;
      }
      
      // 解码数据块并添加到缓冲区
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      
      // 按行分割并处理完整的行
      const lines = buffer.split('\n');
      
      // 保留最后一个可能不完整的行到缓冲区
      buffer = lines.pop() || '';
      
      // 处理所有完整的行
      for (const line of lines) {
        if (line.trim()) {
          try {
            const jsonData = JSON.parse(line.trim());
            processStreamChunk(jsonData, onChunk);
          } catch (e) {
            console.error('解析JSON行失败:', e, line);
            // 作为纯文本处理
            if (onChunk && typeof onChunk === 'function') {
              onChunk(line);
            }
          }
        }
      }
    }
    
    return true;
  }
}

// 处理流式数据块的辅助函数
function processStreamChunk(jsonData, onChunk) {
  if (!jsonData || !onChunk || typeof onChunk !== 'function') {
    return;
  }
  
  // 根据类型处理不同的消息
  switch (jsonData.type) {
    case 'thinking':
      // 思考过程
      onChunk(jsonData.content, {
        type: 'thinking',
        turn: jsonData.turn // 可能为undefined，模式3才有
      });
      break;
      
    case 'answer':
      // 回答内容
      onChunk(jsonData.content, {
        type: 'answer',
        turn: jsonData.turn // 可能为undefined，模式3才有
      });
      break;
      
    case 'system':
      // 系统消息（如分隔符）
      onChunk(jsonData.content, {
        type: 'system',
        turn: jsonData.turn // 可能为undefined，模式3才有
      });
      break;
      
    case 'search_results':
      // 搜索结果
      onChunk('', {
        type: 'search_results',
        documents: jsonData.documents,
        turn: jsonData.turn // 可能为undefined，模式3才有
      });
      break;
      
    case 'search_query':
      // 搜索查询
      onChunk(jsonData.content, {
        type: 'search_query',
        turn: jsonData.turn // 可能为undefined，模式3才有
      });
      break;
      
    case 'final_answer':
      // 最终答案（主要用于模式3）
      onChunk(jsonData.content, {
        type: 'final_answer',
        search_queries: jsonData.search_queries,
        search_results: jsonData.search_results
      });
      break;
      
    case 'error':
      // 错误信息
      onChunk(jsonData.content, {
        type: 'error'
      });
      break;
      
    default:
      // 未知类型，直接传递原始数据
      console.warn('未知消息类型:', jsonData.type);
      onChunk(jsonData.content || JSON.stringify(jsonData), {
        type: 'unknown'
      });
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
