# 智能问答系统简化版实现报告

## 项目概述

根据用户需求，我们实现了一个简化版的智能问答系统，具有以下特点：
- 无需登录注册功能
- 无需历史数据存储功能
- 无需数据库依赖
- 使用MockModel替代真实模型调用

系统采用前后端分离架构，前端使用Vue3+JavaScript，后端使用Python FastAPI，通过HTTP请求实现前后端通信。

## 技术架构

### 整体架构

```
[前端 Vue3+JavaScript] --HTTP请求--> [Python后端 FastAPI] --调用--> [MockModel]
       ↑                          ↓
       └-------JSON响应-----------┘
```

### 技术栈

#### 前端技术栈
- **框架**：Vue 3
- **构建工具**：Vite
- **状态管理**：Pinia（仅聊天状态）
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **路由管理**：Vue Router（无需认证）

#### 后端技术栈
- **框架**：FastAPI
- **ASGI服务器**：Uvicorn
- **数据验证**：Pydantic
- **模拟模型**：自定义MockModel类

## 实现内容

### 1. 后端实现

#### 1.1 项目结构
```
backend_simplified/
├── app/
│   ├── api/
│   │   └── chat.py       # 聊天相关接口
│   ├── core/
│   │   └── config.py     # 应用配置
│   ├── models/
│   │   └── mock_model.py # 模拟模型实现
│   └── schemas/
│       └── chat.py       # 聊天相关模式
├── main.py               # 应用入口
└── requirements.txt      # 依赖管理
```

#### 1.2 MockModel实现

MockModel类提供了一个简单的模拟模型服务，根据用户输入的关键词返回预设的回复：

```python
class MockModel:
    """模拟模型服务，用于开发和测试"""
    
    def __init__(self):
        """初始化模拟模型"""
        # 预设一些问答对，用于模拟回复
        self.qa_pairs = {
            "蛋白质": "蛋白质结构预测是生物信息学中的重要问题...",
            "研究方法": "在蛋白质结构预测研究中，主要方法包括...",
            # 更多预设问答对...
        }
        
        # 默认回复
        self.default_reply = "您好！我是一个专注于蛋白质结构预测研究的AI助手..."
    
    async def predict(self, query: str) -> str:
        """模拟模型推理，根据问题返回预设回复"""
        # 查找匹配的关键词
        for keyword, response in self.qa_pairs.items():
            if keyword.lower() in query.lower():
                return response
        
        # 如果没有匹配的关键词，返回默认回复
        return self.default_reply
```

#### 1.3 API接口实现

聊天API接口简化为一个无状态的消息处理端点：

```python
@router.post("/message", response_model=ChatMessageResponse)
async def send_message(message: ChatMessageCreate):
    """发送消息并获取AI回复"""
    # 调用模型服务获取回复
    response = await model_service.predict(message.content)
    
    return {"response": response}
```

### 2. 前端实现

#### 2.1 项目结构
```
frontend_simplified/
├── public/              # 静态资源
├── src/
│   ├── api/             # API调用
│   │   └── index.js     # API封装
│   ├── assets/          # 静态资源
│   │   └── main.css     # 全局样式
│   ├── components/      # 组件
│   ├── router/          # 路由
│   │   └── index.js     # 路由配置
│   ├── store/           # 状态管理
│   │   └── chat.js      # 聊天状态
│   ├── views/           # 页面
│   │   ├── ChatView.vue # 聊天页面
│   │   └── KnowledgeView.vue # 知识库页面
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML模板
├── package.json         # 依赖配置
└── vite.config.js       # Vite配置
```

#### 2.2 聊天状态管理

使用Pinia进行状态管理，仅保留聊天相关状态，所有数据仅存储在内存中：

```javascript
export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 发送消息
  async function sendMessage(content) {
    try {
      loading.value = true
      
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
    sendMessage,
    clearMessages
  }
})
```

#### 2.3 聊天界面实现

聊天界面包含消息展示区域、输入区域和知识库侧边栏，完全符合设计图要求：

```vue
<template>
  <div class="chat-view">
    <div class="chat-header">
      <div class="chat-title">
        <h1>{{ pageTitle }}</h1>
      </div>
    </div>
    
    <div class="chat-container">
      <div class="chat-messages" ref="messagesContainer">
        <!-- 消息列表 -->
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="['message', message.isUser ? 'message-user' : 'message-assistant']"
        >
          <div class="message-content" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
        
        <!-- 加载指示器 -->
        <div v-if="loading" class="loading-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在思考...</span>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          :placeholder="inputPlaceholder"
          resize="none"
          @keydown.enter.ctrl.prevent="sendMessage"
        >
        </el-input>
        <div class="input-actions">
          <el-button 
            type="primary" 
            :disabled="!inputMessage.trim() || loading" 
            @click="sendMessage"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 知识库侧边栏 -->
    <div class="knowledge-sidebar">
      <!-- 知识库内容 -->
    </div>
  </div>
</template>
```

#### 2.4 知识库页面实现

知识库页面展示预设的知识条目，支持分类和搜索功能：

```vue
<template>
  <div class="knowledge-view">
    <div class="knowledge-header">
      <h1>知识库</h1>
      <el-input
        v-model="searchQuery"
        placeholder="搜索知识库..."
        prefix-icon="Search"
        clearable
        class="search-input"
      ></el-input>
    </div>
    
    <div class="knowledge-content">
      <!-- 分类列表 -->
      <div class="knowledge-categories">
        <div 
          v-for="category in categories" 
          :key="category"
          :class="['category-item', { active: selectedCategory === category }]"
          @click="selectedCategory = category"
        >
          {{ category }}
        </div>
      </div>
      
      <!-- 知识条目列表 -->
      <div class="knowledge-items">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="knowledge-card"
        >
          <h3>{{ item.title }}</h3>
          <div class="knowledge-content">{{ item.content }}</div>
          <div class="knowledge-meta">
            <span class="knowledge-category">{{ item.category }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

## 功能特点

1. **无状态设计**：
   - 无需用户登录注册
   - 聊天记录仅保存在当前会话内存中
   - 页面刷新后聊天记录将丢失

2. **MockModel集成**：
   - 使用预设问答对模拟模型回复
   - 支持关键词匹配和默认回复机制
   - 完全无需真实模型依赖

3. **知识库展示**：
   - 预设知识条目展示
   - 支持分类和搜索功能
   - 知识条目可直接用于提问

4. **简化API**：
   - 仅保留核心聊天功能API
   - 无需认证和数据库
   - 接口简洁明了

## 部署与运行

### 后端部署

1. 安装依赖：
```bash
cd backend_simplified
pip install -r requirements.txt
```

2. 启动服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端部署

1. 安装依赖：
```bash
cd frontend_simplified
npm install
```

2. 开发模式运行：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 总结

本项目实现了一个简化版的智能问答系统，完全符合用户的新需求：
- 删除了登录注册功能
- 删除了历史数据存储功能
- 不使用数据库
- 使用MockModel替代真实模型调用

系统保留了核心的问答功能和知识库展示，UI设计与原设计图保持一致，为开发和测试提供了一个轻量级的解决方案。
