import { SessionService } from '../../../src/services/session-service';
import { RedisService } from '../../../src/services/redis-service';
import { RedisError } from '../../../src/errors/redis-error';
import { SessionStatus } from '../../../src/models/session';

// 模拟Redis服务
jest.mock('../../../src/services/redis-service', () => {
  return {
    getRedisClient: jest.fn(),
  };
});

// 模拟logger
jest.mock('../../../src/utils/logger', () => ({
  __esModule: true,
  default: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  }
}));

// 模拟config-loader
jest.mock('../../../src/utils/config-loader', () => ({
  loadConfig: jest.fn().mockReturnValue({
    agents: [
      { id: 'default-agent-id', isDefault: true },
      { id: 'another-agent-id', isDefault: false }
    ]
  }),
}));

describe('会话服务', () => {
  // 模拟数据
  const mockSession = {
    id: 'session-123',
    userId: 'user-456',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    status: SessionStatus.ACTIVE,
    currentAgentId: 'agent-789',
    context: { lastMessageId: 'msg-123' },
  };

  // 模拟Redis客户端
  const mockRedisClient = {
    get: jest.fn(),
    set: jest.fn().mockImplementation(() => Promise.resolve()),
    sadd: jest.fn().mockImplementation(() => Promise.resolve()),
    lrange: jest.fn(),
    rpush: jest.fn().mockImplementation(() => Promise.resolve()),
  };

  // 测试前准备
  beforeEach(() => {
    jest.clearAllMocks();
    require('../../../src/services/redis-service').getRedisClient.mockReturnValue(mockRedisClient);
  });

  describe('createSession', () => {
    it('应正确创建会话', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const preferredAgentId = 'agent-456';
      const initialContext = { source: 'web' };
      
      // 准备Redis返回值
      mockRedisClient.set.mockImplementation(() => Promise.resolve());
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.createSession(userId, preferredAgentId, initialContext);
      
      // 断言结果
      expect(result).toBeDefined();
      expect(result.userId).toBe(userId);
      expect(result.currentAgentId).toBe(preferredAgentId);
      expect(result.context).toEqual(initialContext);
      expect(result.status).toBe(SessionStatus.ACTIVE);
      expect(mockRedisClient.set).toHaveBeenCalled();
      expect(mockRedisClient.sadd).toHaveBeenCalled();
    });

    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.set.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.createSession('user-123', 'agent-456')
      ).rejects.toThrow(Error);
    });
  });

  describe('getSession', () => {
    it('应正确获取存在的会话', async () => {
      // 模拟Redis返回会话
      mockRedisClient.get.mockImplementation(() => Promise.resolve(JSON.stringify(mockSession)));
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.getSession('session-123');
      
      // 断言结果
      expect(result).toEqual(mockSession);
      expect(mockRedisClient.get).toHaveBeenCalledWith('session:session-123');
    });

    it('会话不存在时应返回null', async () => {
      // 模拟Redis返回null
      mockRedisClient.get.mockImplementation(() => Promise.resolve(null));
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.getSession('not-exist');
      
      // 断言结果
      expect(result).toBeNull();
    });
    
    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.get.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.getSession('session-123')
      ).rejects.toThrow(Error);
    });
  });

  describe('updateSession', () => {
    it('应正确更新会话', async () => {
      // 准备现有会话与更新数据
      mockRedisClient.get.mockImplementation(() => Promise.resolve(JSON.stringify(mockSession)));
      mockRedisClient.set.mockImplementation(() => Promise.resolve());
      
      const updates = {
        status: SessionStatus.PAUSED,
        currentAgentId: 'new-agent-id',
        context: { lastMessageId: 'msg-456' }
      };
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.updateSession('session-123', updates);
      
      // 断言结果
      expect(result).toBeDefined();
      expect(result.id).toBe(mockSession.id);
      expect(result.status).toBe(updates.status);
      expect(result.currentAgentId).toBe(updates.currentAgentId);
      expect(result.context).toEqual(updates.context);
      expect(mockRedisClient.set).toHaveBeenCalled();
    });
    
    it('会话不存在时应返回null', async () => {
      // 模拟Redis返回null
      mockRedisClient.get.mockImplementation(() => Promise.resolve(null));
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.updateSession('not-exist', { status: SessionStatus.PAUSED });
      
      // 断言结果
      expect(result).toBeNull();
    });
    
    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.get.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.updateSession('session-123', { status: SessionStatus.PAUSED })
      ).rejects.toThrow(Error);
    });
  });

  describe('endSession', () => {
    it('应正确结束会话', async () => {
      // 模拟Redis返回会话
      mockRedisClient.get.mockImplementation(() => Promise.resolve(JSON.stringify(mockSession)));
      mockRedisClient.set.mockImplementation(() => Promise.resolve());
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.endSession('session-123');
      
      // 断言结果
      expect(result).toBe(true);
      expect(mockRedisClient.set).toHaveBeenCalled();
    });
    
    it('会话不存在时应返回false', async () => {
      // 模拟Redis返回null
      mockRedisClient.get.mockImplementation(() => Promise.resolve(null));
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.endSession('not-exist');
      
      // 断言结果
      expect(result).toBe(false);
    });
    
    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.get.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.endSession('session-123')
      ).rejects.toThrow(Error);
    });
  });

  describe('getSessionMessages', () => {
    it('应正确获取会话消息', async () => {
      // 准备模拟数据
      const messages = [
        JSON.stringify({ id: 'msg-1', sessionId: 'session-123', content: '你好' }),
        JSON.stringify({ id: 'msg-2', sessionId: 'session-123', content: '你好，有什么可以帮助你的？' })
      ];
      
      // 模拟Redis返回
      mockRedisClient.lrange.mockImplementation(() => Promise.resolve(messages));
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.getSessionMessages('session-123', 10, 0);
      
      // 断言结果
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe('msg-1');
      expect(result[1].id).toBe('msg-2');
      expect(mockRedisClient.lrange).toHaveBeenCalledWith('session:session-123:messages', 0, 9);
    });
    
    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.lrange.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.getSessionMessages('session-123')
      ).rejects.toThrow(Error);
    });
  });

  describe('addSessionMessage', () => {
    it('应正确添加会话消息', async () => {
      // 准备模拟数据
      const message = {
        id: 'msg-123',
        sessionId: 'session-123',
        content: '您好，有什么可以帮助您的？',
        role: 'agent' as const,
        timestamp: new Date().toISOString()
      };
      
      // 模拟Redis返回
      mockRedisClient.get.mockImplementation(() => Promise.resolve(JSON.stringify(mockSession)));
      mockRedisClient.set.mockImplementation(() => Promise.resolve());
      mockRedisClient.rpush.mockImplementation(() => Promise.resolve());
      
      // 初始化服务并调用方法
      const sessionService = new SessionService();
      const result = await sessionService.addSessionMessage(message);
      
      // 断言结果
      expect(result).toBe(true);
      expect(mockRedisClient.rpush).toHaveBeenCalledWith(
        'session:session-123:messages',
        JSON.stringify(message)
      );
    });
    
    it('Redis错误时应抛出异常', async () => {
      // 模拟Redis错误
      mockRedisClient.rpush.mockImplementation(() => Promise.reject(new Error('Redis连接失败')));
      
      // 准备消息
      const message = {
        id: 'msg-123',
        sessionId: 'session-123',
        content: '您好，有什么可以帮助您的？',
        role: 'agent' as const,
        timestamp: new Date().toISOString()
      };
      
      // 初始化服务
      const sessionService = new SessionService();
      
      // 断言异常
      await expect(
        sessionService.addSessionMessage(message)
      ).rejects.toThrow(Error);
    });
  });
});