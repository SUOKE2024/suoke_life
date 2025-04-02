import { AppError, ErrorCode, handleError, SessionNotFoundError, AgentNotFoundError } from '../../../src/utils/error-handler';

// 模拟Express Response对象
const mockResponse = () => {
  const res: any = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

describe('错误处理工具', () => {
  
  describe('AppError', () => {
    it('应正确创建基础应用错误', () => {
      const error = new AppError('测试错误', ErrorCode.INVALID_REQUEST, 400);
      
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe('测试错误');
      expect(error.errorCode).toBe(ErrorCode.INVALID_REQUEST);
      expect(error.statusCode).toBe(400);
    });
    
    it('应使用默认错误码和状态码', () => {
      const error = new AppError('未指定错误码的错误');
      
      expect(error.errorCode).toBe(ErrorCode.UNKNOWN_ERROR);
      expect(error.statusCode).toBe(500);
    });
    
    it('应支持附加详细信息', () => {
      const details = { requestId: '123', context: { user: 'test' } };
      const error = new AppError('带详情的错误', ErrorCode.INVALID_REQUEST, 400, details);
      
      expect(error.details).toEqual(details);
    });
  });
  
  describe('SessionNotFoundError', () => {
    it('应正确创建会话未找到错误', () => {
      const sessionId = 'test-session-id';
      const error = new SessionNotFoundError(sessionId);
      
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe(`未找到会话: ${sessionId}`);
      expect(error.errorCode).toBe(ErrorCode.SESSION_NOT_FOUND);
      expect(error.statusCode).toBe(404);
    });
  });
  
  describe('AgentNotFoundError', () => {
    it('应正确创建代理未找到错误', () => {
      const agentId = 'test-agent-id';
      const error = new AgentNotFoundError(agentId);
      
      expect(error).toBeInstanceOf(AppError);
      expect(error.message).toBe(`未找到代理: ${agentId}`);
      expect(error.errorCode).toBe(ErrorCode.AGENT_NOT_FOUND);
      expect(error.statusCode).toBe(404);
    });
  });
  
  describe('handleError', () => {
    it('应以正确的格式处理AppError', () => {
      const res = mockResponse();
      const error = new AppError('测试错误', ErrorCode.INVALID_REQUEST, 400, { test: true });
      
      handleError(error, res);
      
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: {
          code: ErrorCode.INVALID_REQUEST,
          message: '测试错误',
          details: { test: true }
        }
      });
    });
    
    it('应以通用错误格式处理未知错误', () => {
      const res = mockResponse();
      const error = new Error('未知错误');
      
      handleError(error, res);
      
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: {
          code: ErrorCode.UNKNOWN_ERROR,
          message: '服务器内部错误'
        }
      });
    });
  });
}); 