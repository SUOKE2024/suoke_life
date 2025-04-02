/**
 * 索克生活共享模块类型定义
 * 为微服务架构提供共享的TypeScript类型定义
 */

// 用户类型定义
export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  createdAt: Date;
  updatedAt: Date;
}

// 配置文件类型定义
export interface Config {
  env: string;
  server: {
    port: number;
    host: string;
    baseUrl: string;
    apiPrefix: string;
  };
  jwt: {
    secret: string;
    expiresIn: string;
    refreshExpiresIn: string;
  };
  database: {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
  };
  security: {
    encryptionKey: string;
    bcryptSaltRounds: number;
    corsOptions: {
      origin: string | string[];
      methods: string[];
      allowedHeaders: string[];
      credentials: boolean;
    };
  };
  logging: {
    level: string;
    directory: string;
  };
  upload: {
    maxSize: number;
    allowedMimeTypes: string[];
    destination: string;
  };
  cache: {
    ttl: number;
    checkPeriod: number;
  };
  services: {
    smtp: {
      host: string;
      port: number;
      secure: boolean;
      auth: {
        user: string;
        pass: string;
      };
      from: string;
    };
    sms: {
      provider: string;
      accessKeyId: string;
      accessKeySecret: string;
      signName: string;
    };
  };
}

// 知识节点类型定义
export interface KnowledgeNode {
  id: string;
  title: string;
  content: string;
  type: string;
  tags: string[];
  vector?: number[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// 知识关系类型定义
export interface KnowledgeRelation {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
  weight: number;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// 体质类型定义
export interface Constitution {
  id: string;
  userId: string;
  type: string;
  score: number;
  characteristics: string[];
  recommendations: {
    diet: string[];
    exercise: string[];
    lifestyle: string[];
  };
  createdAt: Date;
  updatedAt: Date;
}

// 健康记录类型定义
export interface HealthRecord {
  id: string;
  userId: string;
  type: string;
  recordDate: Date;
  data: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// HTTP响应类型定义
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
} 