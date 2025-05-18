# 智能问答系统部署指南

## 系统要求

### 后端要求
- Python 3.8+
- 足够的磁盘空间用于存储模型（根据选择的模型大小而定）
- 对于GPU加速：CUDA兼容的GPU（推荐用于生产环境）

### 前端要求
- Node.js 14+
- npm 6+ 或 yarn 1.22+

## 后端部署

### 1. 安装依赖

```bash
# 克隆代码或解压缩源码包
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

根据需要修改 `app/core/config.py` 文件中的配置：

```python
# 修改密钥（生产环境必须修改）
SECRET_KEY: str = "your-secret-key-for-jwt"

# 配置数据库（默认使用SQLite）
DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

# 配置模型路径
MODEL_PATH: str = "./app/models/model_weights"

# 配置CORS（生产环境应限制来源）
CORS_ORIGINS: List[str] = ["http://your-frontend-domain.com"]
```

### 3. 启动服务

```bash
# 开发环境
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 验证后端服务

访问 `http://your-server-ip:8000/docs` 查看API文档并测试接口。

## 前端部署

### 1. 安装依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或
yarn install
```

### 2. 配置

修改 `vite.config.js` 文件中的代理配置，指向后端服务：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-server:8000',
      changeOrigin: true
    }
  }
}
```

### 3. 开发环境运行

```bash
npm run dev
# 或
yarn dev
```

### 4. 生产环境构建

```bash
npm run build
# 或
yarn build
```

构建完成后，`dist` 目录中包含所有静态文件，可以通过任何Web服务器（如Nginx、Apache）提供服务。

### 5. Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://your-backend-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 本地模型配置

### 1. 模型选择

系统默认使用ChatGLM3-6B模型，您也可以替换为其他支持的模型：

- ChatGLM3-6B（默认）
- Llama-2-7b-chat
- Baichuan2-7B-Chat
- 其他支持Hugging Face Transformers的模型

### 2. 模型下载

修改 `app/models/model_service.py` 文件中的模型名称：

```python
model_name = "THUDM/chatglm3-6b"  # 替换为您选择的模型
```

首次运行时，系统会自动下载模型文件。您也可以手动下载并放置在指定目录。

### 3. 性能优化

对于资源受限的环境，可以考虑以下优化：

- 使用量化版本的模型减少内存占用
- 调整批处理大小和生成参数
- 使用模型并行或模型分片技术

## 常见问题

### 1. 模型加载失败

检查：
- 磁盘空间是否充足
- Python版本是否兼容
- CUDA环境是否正确配置（如使用GPU）

### 2. 前端无法连接后端

检查：
- 后端服务是否正常运行
- 代理配置是否正确
- 网络防火墙设置

### 3. 认证问题

检查：
- JWT密钥配置
- 令牌过期时间设置
- 前端存储令牌的方式

## 系统维护

### 1. 数据库备份

定期备份SQLite数据库文件：

```bash
cp app.db app.db.backup-$(date +%Y%m%d)
```

### 2. 日志管理

配置适当的日志级别和轮转策略，避免日志文件过大。

### 3. 模型更新

当需要更新模型时：

1. 备份当前模型（如有自定义修改）
2. 修改模型名称或路径
3. 重启服务

## 联系与支持

如有任何问题或需要技术支持，请联系：

- 邮箱：support@example.com
- 项目仓库：https://github.com/example/ai-research-assistant
