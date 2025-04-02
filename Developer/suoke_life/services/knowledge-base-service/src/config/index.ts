/**
 * 配置文件
 * 集中管理服务配置
 */
import dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

const config = {
  // 服务配置
  app: {
    name: 'knowledge-base-service',
    port: parseInt(process.env.PORT || '3000'),
    env: process.env.NODE_ENV || 'development',
    logLevel: process.env.LOG_LEVEL || 'info'
  },
  
  // 数据库配置
  mongo: {
    uri: process.env.MONGO_URI || 'mongodb://localhost:27017/knowledge-base',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true
    }
  },
  
  // 知识图谱服务配置
  knowledgeGraphService: {
    url: process.env.KNOWLEDGE_GRAPH_SERVICE_URL || 'http://localhost:3001/api',
    apiKey: process.env.KNOWLEDGE_GRAPH_API_KEY || 'default-kg-api-key'
  },
  
  // RAG服务配置
  ragService: {
    url: process.env.RAG_SERVICE_URL || 'http://localhost:3002/api',
    apiKey: process.env.RAG_API_KEY || 'default-rag-api-key'
  },
  
  // JWT配置
  jwt: {
    secret: process.env.JWT_SECRET || 'your-secret-key',
    expiresIn: process.env.JWT_EXPIRES_IN || '1d'
  },
  
  // 其他服务配置
  services: {
    userService: process.env.USER_SERVICE_URL || 'http://localhost:3003/api'
  }
};

export default config;