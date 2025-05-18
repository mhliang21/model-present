# model-present
模型问答展示网站
# 智能问答系统简化版技术架构设计

## 整体架构

本系统采用前后端分离架构，主要由两个核心部分组成：

1. **前端**：基于Vue3和JavaScript开发的用户界面
2. **后端**：基于FastAPI开发的RESTful API服务，集成MockModel

系统数据流如下：
- 用户在Vue3前端界面输入问题
- 前端通过HTTP请求将问题发送到FastAPI后端
- 后端接收请求，调用MockModel处理问题
- MockModel生成回答，返回给后端
- 后端将回答通过JSON响应返回给前端
- 前端展示回答结果给用户

## 技术栈选择

### 前端技术栈
- **框架**：Vue 3
- **构建工具**：Vite
- **状态管理**：Pinia（简化版，仅保留聊天状态）
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **路由管理**：Vue Router（简化版，无需认证）

### 后端技术栈
- **框架**：FastAPI
- **ASGI服务器**：Uvicorn
- **数据验证**：Pydantic
- **模拟模型**：自定义MockModel类

## 前端架构设计

### 组件结构
```
src/
├── assets/            # 静态资源
├── components/        # 通用组件
│   ├── AppHeader.vue  # 应用头部
│   ├── AppSidebar.vue # 侧边栏
│   ├── ChatInput.vue  # 聊天输入框
│   ├── ChatMessage.vue # 聊天消息
│   └── KnowledgeCard.vue # 知识卡片
├── views/             # 页面视图
│   ├── ChatView.vue   # 聊天主页面
│   └── KnowledgeBaseView.vue # 知识库页面
├── store/             # 状态管理
│   └── chat.js        # 聊天相关状态
├── api/               # API调用
│   └── index.js       # API封装
├── router/            # 路由配置
├── utils/             # 工具函数
└── App.vue            # 根组件
```

### 状态管理
使用Pinia进行状态管理，仅保留聊天相关状态：

**chatStore**：管理聊天消息、会话状态等
- 消息列表存储在内存中
- 发送消息和接收回复
- 清空聊天记录

### 路由设计
简化后的路由结构：
```javascript
const routes = [
  {
    path: '/',
    name: 'chat',
    component: ChatView
  },
  {
    path: '/knowledge',
    name: 'knowledge',
    component: KnowledgeBaseView
  }
]
```

## 后端架构设计

### 目录结构
```
backend/
├── app/
│   ├── api/           # API路由
│   │   └── chat.py    # 聊天相关接口
│   ├── core/          # 核心配置
│   │   └── config.py  # 应用配置
│   ├── models/        # 模拟模型
│   │   └── mock_model.py # 模拟模型实现
│   └── schemas/       # 数据模式
│       └── chat.py    # 聊天相关模式
├── main.py            # 应用入口
└── requirements.txt   # 依赖管理
```

### API接口设计

#### 聊天相关接口
- `POST /api/chat/message`：发送聊天消息并获取回复
  - 请求体：`{ "content": "用户问题" }`
  - 响应：`{ "response": "模型回复" }`

### MockModel设计

```python
class MockModel:
    """模拟模型服务，用于开发和测试"""
    
    def predict(self, query: str) -> str:
        """
        模拟模型推理，根据问题返回预设回复
        
        Args:
            query: 用户输入的查询文本
            
        Returns:
            模拟的回复文本
        """
        # 根据不同的查询返回不同的模拟回复
        if "蛋白质" in query:
            return "蛋白质结构预测是生物信息学中的重要问题，深度学习方法在这一领域取得了显著进展。特别是AlphaFold2等模型的出现，大大提高了预测精度。"
        elif "研究方法" in query:
            return "在蛋白质结构预测研究中，主要方法包括：\n1. 卷积神经网络(CNN)在二级结构预测中的应用\n2. 循环神经网络(RNN)处理序列信息\n3. 注意力机制在结构预测中的创新应用\n4. AlphaFold2的技术突破与影响"
        else:
            return "您好！我是一个专注于蛋白质结构预测研究的AI助手。我可以回答相关的科学问题，提供研究方法介绍，以及分享最新的研究进展。请问有什么可以帮助您的？"
```

## 数据流转过程

1. **用户输入**：用户在前端输入问题
2. **前端处理**：
   - 将问题添加到聊天历史（内存中）
   - 显示等待状态
   - 通过Axios发送POST请求到后端
3. **后端处理**：
   - 接收请求并验证
   - 调用MockModel服务
   - 将模型响应格式化为JSON
   - 返回响应给前端
4. **前端展示**：
   - 接收后端响应
   - 更新聊天历史（内存中）
   - 渲染回答内容

## 无状态设计考虑

1. **会话管理**：
   - 所有聊天记录仅保存在前端内存中
   - 页面刷新后聊天记录将丢失
   - 无需服务器端会话管理

2. **知识库展示**：
   - 知识库内容可以是静态预设的
   - 或通过API从后端获取预设内容

3. **错误处理**：
   - 前端实现基本的错误提示
   - 后端返回标准化的错误响应

## 部署简化

由于移除了数据库和认证，部署流程大大简化：

1. **后端部署**：
   - 安装Python依赖
   - 启动FastAPI服务

2. **前端部署**：
   - 构建静态文件
   - 通过任何Web服务器提供服务

## 扩展性考虑

尽管是简化版，系统设计仍考虑了未来可能的扩展：

1. **真实模型集成**：MockModel接口设计与真实模型一致，便于未来替换
2. **状态持久化**：前端状态设计便于未来添加持久化功能
3. **功能模块化**：组件和API设计保持模块化，便于添加新功能
