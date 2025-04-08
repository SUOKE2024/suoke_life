import { config } from 'dotenv';
import { join } from 'path';

// 加载环境变量
config();

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  poolMin: number;
  poolMax: number;
}

export interface RedisConfig {
  host: string;
  port: number;
  password: string;
}

export interface VectorDBConfig {
  host: string;
  port: number;
  username: string;
  password: string;
}

export interface Config {
  env: string;
  port: number;
  logLevel: string;
  graphDB: DatabaseConfig;
  redis: RedisConfig;
  vectorDB: VectorDBConfig;
  ragServiceUrl: string;
  encryptionKey: string;
}

const configuration: Config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3006', 10),
  logLevel: process.env.LOG_LEVEL || 'info',
  
  graphDB: {
    host: process.env.GRAPH_DB_HOST || 'localhost',
    port: parseInt(process.env.GRAPH_DB_PORT || '7687', 10),
    database: process.env.GRAPH_DB_NAME || 'suoke_knowledge_graph',
    username: process.env.GRAPH_DB_USER || 'neo4j',
    password: process.env.GRAPH_DB_PASSWORD || 'password',
    poolMin: parseInt(process.env.GRAPH_DB_POOL_MIN || '5', 10),
    poolMax: parseInt(process.env.GRAPH_DB_POOL_MAX || '30', 10),
  },

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || '',
  },

  vectorDB: {
    host: process.env.VECTOR_DB_HOST || 'localhost',
    port: parseInt(process.env.VECTOR_DB_PORT || '19530', 10),
    username: process.env.VECTOR_DB_USER || 'root',
    password: process.env.VECTOR_DB_PASSWORD || '',
  },

  ragServiceUrl: process.env.RAG_SERVICE_URL || 'http://localhost:3007',
  encryptionKey: process.env.ENCRYPTION_KEY || 'default-encryption-key',
};

export default configuration;