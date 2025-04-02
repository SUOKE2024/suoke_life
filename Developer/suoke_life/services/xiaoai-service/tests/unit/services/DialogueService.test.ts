/**
 * 对话服务单元测试
 */
import { DialogueService } from '../../../src/services/DialogueService';
import { CacheService } from '../../../src/services/CacheService';
import { createMockRedisClient } from '../helpers/mockRedis';

// 模拟OpenAI客户端
jest.mock('openai', () => {
  return {
    OpenAI: jest.fn().mockImplementation(() => {
      return {
        chat: {
          completions: {
            create: jest.fn().mockResolvedValue({
              choices: [
                {
                  message: {
                    role: 'assistant',
                    content: '这是测试的AI回复内容，针对您的健康问题，我建议保持规律作息。'
                  },
                  finish_reason: 'stop'
                }
              ],
              usage: {
                total_tokens: 100,
                prompt_tokens: 50,
                completion_tokens: 50
              }
            })
          }
        }
      };
    })
  };
});

// 模拟日志记录器
jest.mock('../../../src/index', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
  }
}));

// 模拟缓存服务
jest.mock('../../../src/services/CacheService');
const MockCacheService = CacheService as jest.MockedClass<typeof CacheService>;
MockCacheService.prototype.get.mockImplementation((key: string) => {
  if (key === 'ai-context:user123') {
    return Promise.resolve([
      { role: 'user', content: '我最近感觉很疲劳' },
      { role: 'assistant', content: '请详细描述您的症状' }
    ]);
  }
  return Promise.resolve(null);
});
MockCacheService.prototype.set.mockResolvedValue('OK');

// 导入模拟的模块
import { OpenAI } from 'openai';
import { logger } from '../../../src/index';

describe('DialogueService', () => {
  let dialogueService: DialogueService;
  let cacheService: CacheService;
  
  beforeEach(() => {
    jest.clearAllMocks();
    cacheService = new CacheService();
    dialogueService = new DialogueService(cacheService);
  });
  
  describe('generateResponse', () => {
    it('应该生成AI回复', async () => {
      const userMessage = '我晚上睡不好，怎么办？';
      const userId = 'user123';
      const agentId = 'health-advisor';
      
      const response = await dialogueService.generateResponse(
        userMessage,
        userId,
        agentId
      );
      
      // 验证结果
      expect(response).toEqual({
        role: 'assistant',
        content: expect.stringContaining('我建议保持规律作息')
      });
      
      // 验证OpenAI API调用
      const openaiInstance = new OpenAI({});
      expect(openaiInstance.chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          messages: expect.arrayContaining([
            expect.objectContaining({ role: 'user', content: userMessage })
          ])
        })
      );
      
      // 验证上下文管理
      expect(cacheService.get).toHaveBeenCalledWith(`ai-context:${userId}`);
      expect(cacheService.set).toHaveBeenCalled();
    });
    
    it('应该处理AI服务错误', async () => {
      // 模拟OpenAI API错误
      const openaiInstance = new OpenAI({});
      (openaiInstance.chat.completions.create as jest.Mock).mockRejectedValueOnce(
        new Error('API错误')
      );
      
      const userMessage = '我有什么问题？';
      const userId = 'user123';
      const agentId = 'health-advisor';
      
      await expect(
        dialogueService.generateResponse(userMessage, userId, agentId)
      ).rejects.toThrow('生成AI回复失败');
      
      expect(logger.error).toHaveBeenCalledWith(
        expect.stringContaining('AI对话生成错误'),
        expect.any(Error)
      );
    });
  });
  
  describe('processMessage', () => {
    it('应该处理特殊命令', async () => {
      const userMessage = '/clear';
      const userId = 'user123';
      
      const result = await dialogueService.processMessage(
        userMessage,
        userId,
        'health-advisor'
      );
      
      expect(result).toEqual({
        role: 'system',
        content: expect.stringContaining('已清除对话历史')
      });
      expect(cacheService.del).toHaveBeenCalledWith(`ai-context:${userId}`);
    });
    
    it('应该处理正常消息', async () => {
      const userMessage = '我该怎么改善睡眠？';
      const userId = 'user123';
      
      const result = await dialogueService.processMessage(
        userMessage,
        userId,
        'health-advisor'
      );
      
      expect(result).toEqual({
        role: 'assistant',
        content: expect.stringContaining('我建议保持规律作息')
      });
    });
    
    it('应该进行内容过滤', async () => {
      // 假设服务有内容过滤功能，测试不合规内容
      const userMessage = 'NSFW内容或违规内容';
      const userId = 'user123';
      
      // 模拟内容过滤方法
      dialogueService.filterContent = jest.fn().mockReturnValue({
        isAllowed: false,
        reason: '内容违规'
      });
      
      const result = await dialogueService.processMessage(
        userMessage,
        userId,
        'health-advisor'
      );
      
      expect(result).toEqual({
        role: 'system',
        content: expect.stringContaining('不允许的内容')
      });
      
      // 恢复正常实现以避响其他测试
      dialogueService.filterContent = jest.fn().mockReturnValue({
        isAllowed: true
      });
    });
  });
  
  describe('formatPrompt', () => {
    it('应该格式化系统提示', () => {
      const userId = 'user123';
      const agentProfile = {
        name: '小艾健康顾问',
        description: '专注健康咨询的AI助手',
        personalityTraits: ['专业', '友善', '耐心']
      };
      
      const formattedPrompt = dialogueService.formatPrompt(
        userId,
        agentProfile as any
      );
      
      expect(formattedPrompt).toContainEqual(
        expect.objectContaining({
          role: 'system',
          content: expect.stringContaining('小艾健康顾问')
        })
      );
      
      // 验证包含人格特征
      expect(formattedPrompt[0].content).toMatch(/专业.*友善.*耐心/);
    });
    
    it('应该合并历史上下文', async () => {
      const userId = 'user123';
      const agentProfile = {
        name: '小艾健康顾问',
        description: '专注健康咨询的AI助手',
        personalityTraits: ['专业', '友善']
      };
      
      // 使用已模拟的缓存服务返回历史记录
      const formattedPrompt = await dialogueService.formatPromptWithHistory(
        userId,
        agentProfile as any,
        '我睡眠不好'
      );
      
      // 验证包含系统提示
      expect(formattedPrompt[0]).toEqual(
        expect.objectContaining({ role: 'system' })
      );
      
      // 验证包含历史对话
      expect(formattedPrompt).toContainEqual(
        expect.objectContaining({
          role: 'user',
          content: '我最近感觉很疲劳'
        })
      );
      
      // 验证包含当前用户消息
      expect(formattedPrompt).toContainEqual(
        expect.objectContaining({
          role: 'user',
          content: '我睡眠不好'
        })
      );
    });
  });
}); 