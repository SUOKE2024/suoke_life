/**
 * 应用程序配置
 */

/**
 * 应用程序配置接口
 */
export interface AppConfig {
  /**
   * 应用名称
   */
  name: string;
  
  /**
   * 应用版本
   */
  version: string;
  
  /**
   * 环境
   */
  env: 'development' | 'test' | 'production';
  
  /**
   * 主机
   */
  host: string;
  
  /**
   * 端口
   */
  port: number;
  
  /**
   * API前缀
   */
  apiPrefix: string;
  
  /**
   * 跨域配置
   */
  cors: {
    /**
     * 允许的源
     */
    origin: string | string[];
    
    /**
     * 是否允许凭据
     */
    credentials: boolean;
  };
  
  /**
   * 日志级别
   */
  logLevel: 'error' | 'warn' | 'info' | 'debug';
  
  /**
   * 服务端点配置
   */
  services: {
    /**
     * 小爱服务URL
     */
    xiaoaiServiceUrl: string;
    
    /**
     * 知识库服务URL
     */
    knowledgeBaseServiceUrl: string;
    
    /**
     * 知识图谱服务URL
     */
    knowledgeGraphServiceUrl: string;
    
    /**
     * TCM分析服务URL
     */
    tcmAnalysisServiceUrl: string;
  };
}

/**
 * 获取应用程序配置
 * @returns 应用程序配置对象
 */
export function getAppConfig(): AppConfig {
  return {
    name: 'inquiry-diagnosis-service',
    version: '1.0.0',
    env: (process.env.NODE_ENV as 'development' | 'test' | 'production') || 'development',
    host: process.env.HOST || 'localhost',
    port: parseInt(process.env.PORT || '3007', 10),
    apiPrefix: '/api',
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      credentials: process.env.CORS_CREDENTIALS === 'true'
    },
    logLevel: (process.env.LOG_LEVEL as 'error' | 'warn' | 'info' | 'debug') || 'info',
    services: {
      xiaoaiServiceUrl: process.env.XIAOAI_SERVICE_URL || 'http://localhost:3000',
      knowledgeBaseServiceUrl: process.env.KNOWLEDGE_BASE_SERVICE_URL || 'http://localhost:3001',
      knowledgeGraphServiceUrl: process.env.KNOWLEDGE_GRAPH_SERVICE_URL || 'http://localhost:3002',
      tcmAnalysisServiceUrl: process.env.TCM_ANALYSIS_SERVICE_URL || 'http://localhost:3003'
    }
  };
}