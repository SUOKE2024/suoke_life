import path from 'path';
import { Pact } from '@pact-foundation/pact';
import { LogLevel } from '@pact-foundation/pact/src/common/logger';

// Pact模拟服务器配置
export const pactServerOptions = {
  port: 8080,
  host: 'localhost',
  log: path.resolve(process.cwd(), 'logs', 'pact.log'),
  dir: path.resolve(process.cwd(), 'pacts'),
  logLevel: 'info' as LogLevel,
  spec: 2
};

// 设置一个代理服务的Pact提供者
export const agentServiceProvider = new Pact({
  ...pactServerOptions,
  consumer: 'AgentCoordinatorService',
  provider: 'TCMAgentService',
});

// 设置一个知识服务的Pact提供者
export const knowledgeServiceProvider = new Pact({
  ...pactServerOptions,
  port: 8081, // 使用不同的端口避免冲突
  consumer: 'AgentCoordinatorService',
  provider: 'KnowledgeBaseService',
});

/**
 * 创建标准的Pact交互预期
 * @param provider Pact提供者实例
 * @param interaction 交互定义
 */
export function setupPactInteraction(provider: Pact, interaction: any) {
  return provider.addInteraction(interaction);
}

/**
 * 创建标准的API响应格式
 * @param data 响应数据
 * @param success 成功标志
 */
export function createStandardResponse(data: any, success = true) {
  return {
    success,
    data,
    timestamp: new Date().toISOString()
  };
} 