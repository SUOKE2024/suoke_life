/**
 * 依赖注入提供者
 * 管理应用程序中的依赖关系
 */
import { UserRepository, IUserRepository } from '../repositories/UserRepository';
import { ConversationRepository, IConversationRepository } from '../repositories/ConversationRepository';
import { XiaoAiAgentRepository, IXiaoAiAgentRepository } from '../repositories/XiaoAiAgentRepository';
import { CacheService, ICacheService } from '../services/CacheService';

// 存储库提供者
const userRepository: IUserRepository = new UserRepository();
const conversationRepository: IConversationRepository = new ConversationRepository();
const xiaoAiAgentRepository: IXiaoAiAgentRepository = new XiaoAiAgentRepository();

// 服务提供者
const cacheService: ICacheService = new CacheService();

// 导出存储库
export const repositories = {
  userRepository,
  conversationRepository,
  xiaoAiAgentRepository
};

// 导出服务
export const services = {
  cacheService
};

// 初始化函数
export const initializeServices = async (): Promise<void> => {
  try {
    // 连接到Redis缓存
    await cacheService.connect();
  } catch (error) {
    console.error('初始化服务失败:', error);
    throw error;
  }
};

// 关闭函数
export const shutdownServices = async (): Promise<void> => {
  try {
    // 断开Redis连接
    await cacheService.disconnect();
  } catch (error) {
    console.error('关闭服务失败:', error);
  }
}; 