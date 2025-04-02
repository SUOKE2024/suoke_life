/**
 * XiaoAi控制器单元测试
 */
import { Request, Response } from 'express';
import { XiaoAiController } from '../../../src/controllers/xiaoAi.controller';
import { container } from '../../../src/di/providers'; 

// 模拟Express请求和响应对象
const mockRequest = () => {
  const req = {} as Request;
  req.body = {};
  req.params = {};
  req.query = {};
  return req;
};

const mockResponse = () => {
  const res = {} as Response;
  res.status = jest.fn().mockReturnThis();
  res.json = jest.fn().mockReturnThis();
  res.send = jest.fn().mockReturnThis();
  return res;
};

// 模拟服务和仓库
jest.mock('../../../src/di/providers', () => ({
  container: {
    resolve: jest.fn((name) => {
      // 根据名称返回不同的模拟实例
      if (name === 'xiaoAiAgentRepository') {
        return {
          findAll: jest.fn().mockResolvedValue([
            { _id: 'agent1', name: '小艾健康顾问', activeStatus: true },
            { _id: 'agent2', name: '小艾营养师', activeStatus: true }
          ]),
          findById: jest.fn().mockResolvedValue({ 
            _id: 'agent1', 
            name: '小艾健康顾问', 
            activeStatus: true 
          }),
          countAgents: jest.fn().mockResolvedValue(2)
        };
      }
      if (name === 'conversationRepository') {
        return {
          findByUserId: jest.fn().mockResolvedValue([
            { _id: 'conv1', title: '健康咨询', userId: 'user1' }
          ]),
          findById: jest.fn().mockResolvedValue({
            _id: 'conv1',
            title: '健康咨询',
            userId: 'user1',
            messages: []
          }),
          create: jest.fn().mockResolvedValue({
            _id: 'new-conv',
            title: '新会话',
            userId: 'user1'
          }),
          addMessage: jest.fn().mockResolvedValue(true)
        };
      }
      if (name === 'userRepository') {
        return {
          findByUserId: jest.fn().mockResolvedValue({
            _id: 'user-id',
            userId: 'user1',
            username: 'testuser'
          }),
          updateLastLogin: jest.fn().mockResolvedValue(true)
        };
      }
      if (name === 'cacheService') {
        return {
          get: jest.fn().mockResolvedValue(null),
          set: jest.fn().mockResolvedValue('OK'),
          del: jest.fn().mockResolvedValue(1)
        };
      }
      return {};
    })
  }
}));

describe('XiaoAiController', () => {
  let controller: XiaoAiController;
  let req: Request;
  let res: Response;
  
  beforeEach(() => {
    jest.clearAllMocks();
    controller = new XiaoAiController();
    req = mockRequest();
    res = mockResponse();
  });
  
  describe('getHealth', () => {
    it('应该返回健康状态', async () => {
      await controller.getHealth(req, res);
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        status: 'ok',
        service: 'xiaoai-service'
      }));
    });
  });
  
  describe('getAgents', () => {
    it('应该返回所有代理', async () => {
      await controller.getAgents(req, res);
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({ _id: 'agent1' }),
          expect.objectContaining({ _id: 'agent2' })
        ])
      }));
    });
    
    it('应该处理错误情况', async () => {
      // 模拟findAll方法抛出错误
      container.resolve('xiaoAiAgentRepository').findAll = 
        jest.fn().mockRejectedValue(new Error('测试错误'));
      
      await controller.getAgents(req, res);
      
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false
      }));
    });
  });
  
  describe('getAgentById', () => {
    it('应该返回指定ID的代理', async () => {
      req.params.id = 'agent1';
      
      await controller.getAgentById(req, res);
      
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.objectContaining({ _id: 'agent1' })
      }));
    });
    
    it('找不到代理时应该返回404', async () => {
      req.params.id = 'non-existent';
      container.resolve('xiaoAiAgentRepository').findById = 
        jest.fn().mockResolvedValue(null);
      
      await controller.getAgentById(req, res);
      
      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: expect.stringContaining('找不到')
      }));
    });
  });
  
  describe('getUserConversations', () => {
    it('应该返回用户的会话列表', async () => {
      req.params.userId = 'user1';
      
      await controller.getUserConversations(req, res);
      
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.arrayContaining([
          expect.objectContaining({ _id: 'conv1' })
        ])
      }));
    });
    
    it('应该处理分页参数', async () => {
      req.params.userId = 'user1';
      req.query.page = '2';
      req.query.limit = '10';
      
      await controller.getUserConversations(req, res);
      
      const conversationRepo = container.resolve('conversationRepository');
      expect(conversationRepo.findByUserId).toHaveBeenCalledWith(
        'user1',
        expect.objectContaining({
          skip: 10,
          limit: 10
        })
      );
    });
  });
  
  describe('createConversation', () => {
    it('应该创建新会话', async () => {
      req.body = {
        userId: 'user1',
        title: '新会话',
        agentId: 'agent1'
      };
      
      await controller.createConversation(req, res);
      
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.objectContaining({ _id: 'new-conv' })
      }));
    });
    
    it('缺少必要参数时应该返回400', async () => {
      req.body = { userId: 'user1' }; // 缺少title和agentId
      
      await controller.createConversation(req, res);
      
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false
      }));
    });
  });
  
  describe('sendMessage', () => {
    it('应该发送消息并获取回复', async () => {
      req.params.conversationId = 'conv1';
      req.body = {
        message: '我感觉很疲劳，有什么调理建议吗？',
        userId: 'user1'
      };
      
      // 模拟AI处理和回复
      controller.processAIResponse = jest.fn().mockResolvedValue({
        content: '请保持良好的休息和饮食习惯...',
        role: 'assistant'
      });
      
      await controller.sendMessage(req, res);
      
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: true,
        data: expect.objectContaining({
          message: expect.objectContaining({
            content: expect.stringContaining('请保持良好的休息')
          })
        })
      }));
      
      const conversationRepo = container.resolve('conversationRepository');
      expect(conversationRepo.addMessage).toHaveBeenCalledTimes(2); // 用户消息和AI回复
    });
    
    it('消息处理失败时应该返回错误', async () => {
      req.params.conversationId = 'conv1';
      req.body = {
        message: '有什么建议？',
        userId: 'user1'
      };
      
      // 模拟AI处理失败
      controller.processAIResponse = jest.fn().mockRejectedValue(
        new Error('AI处理失败')
      );
      
      await controller.sendMessage(req, res);
      
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: expect.stringContaining('处理消息时出错')
      }));
    });
  });
}); 