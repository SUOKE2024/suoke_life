/**
 * 参数化测试 - 知识控制器
 */
import { Request, Response } from 'express';
import { jest } from '@jest/globals';
import { KnowledgeController } from '../../../src/controllers/knowledge-controller';
import { KnowledgeService, KnowledgeQueryParams, KnowledgeSearchResult } from '../../../src/services/knowledge-service';
import { createMockResponse, mockResponseAsResponse } from '../../utils/mock-response';

// 模拟知识服务
jest.mock('../../../src/services/knowledge-service');

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

// 模拟domain-classifier
jest.mock('../../../src/utils/domain-classifier', () => ({
  domainClassifier: {
    classifyQuery: jest.fn().mockReturnValue([
      { domain: 'health', confidence: 0.85 },
      { domain: 'nutrition', confidence: 0.65 }
    ])
  }
}));

// 定义MockedKnowledgeService类型
const MockedKnowledgeService = KnowledgeService as jest.MockedClass<typeof KnowledgeService>;

// 参数化测试用例类型定义
interface SearchTestCase {
  name: string;
  params: {
    query?: string;
    domains?: string;
    types?: string;
    page?: string;
    limit?: string;
    semanticSearch?: string;
    hybridSearch?: string;
    minConfidence?: string;
  };
  expected: {
    status: number;
    success: boolean;
    errorMessage?: string;
  };
}

// 知识服务搜索模拟实现的返回类型
type MockedResponse = {
  results?: any[];
  meta?: {
    page: number;
    limit: number;
    domainClassifications?: any[];
  };
  error?: string;
  message?: string;
  response?: string;
  sources?: any[];
};

describe('知识控制器参数化测试', () => {
  let knowledgeController: KnowledgeController;
  let mockSearchKnowledge: jest.Mock;
  let mockGenerateRAGResponse: jest.Mock;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // 创建模拟结果
    const mockResults = [
      {
        id: 'knowledge1',
        title: '健康知识1',
        content: '测试内容1',
        domain: 'health',
        type: 'article',
        tags: ['健康', '养生'],
        confidence: 0.85,
        source: 'test-source'
      }
    ];
    
    // 创建模拟方法
    mockSearchKnowledge = jest.fn().mockImplementation((params: any) => {
      // @ts-ignore - 忽略类型检查
      if (!params.query || params.query.trim() === '') {
        throw new Error('搜索查询不能为空');
      }
      return Promise.resolve(mockResults);
    });
    
    mockGenerateRAGResponse = jest.fn().mockImplementation((query: any, options: any) => {
      // @ts-ignore - 忽略类型检查
      if (!query || query.trim() === '') {
        throw new Error('查询不能为空');
      }
      return Promise.resolve({
        response: '这是基于知识库生成的回答',
        sources: [{ id: 'knowledge1', title: '健康知识1', relevance: 0.92 }],
        metadata: { processingTime: '123ms' }
      });
    });
    
    // 使用mockImplementation而不是mockImplementationOnce确保可以多次调用
    // @ts-ignore - 忽略类型检查
    MockedKnowledgeService.prototype.searchKnowledge = mockSearchKnowledge;
    // @ts-ignore - 忽略类型检查
    MockedKnowledgeService.prototype.generateRAGResponse = mockGenerateRAGResponse;
    
    // 创建知识控制器实例
    knowledgeController = new KnowledgeController();
  });
  
  describe('searchKnowledge - 参数化测试', () => {
    // 定义测试用例集合
    const testCases: SearchTestCase[] = [
      // 成功情况
      {
        name: '基本查询',
        params: { query: '健康知识' },
        expected: { status: 200, success: true }
      },
      {
        name: '带域过滤的查询',
        params: { query: '健康知识', domains: 'health,nutrition' },
        expected: { status: 200, success: true }
      },
      {
        name: '带类型过滤的查询',
        params: { query: '健康知识', types: 'article,video' },
        expected: { status: 200, success: true }
      },
      {
        name: '带分页的查询',
        params: { query: '健康知识', page: '2', limit: '20' },
        expected: { status: 200, success: true }
      },
      {
        name: '启用语义搜索的查询',
        params: { query: '健康知识', semanticSearch: 'true' },
        expected: { status: 200, success: true }
      },
      {
        name: '带最小置信度的查询',
        params: { query: '健康知识', minConfidence: '0.7' },
        expected: { status: 200, success: true }
      },
      
      // 错误情况
      {
        name: '缺少查询参数',
        params: {},
        expected: { status: 400, success: false, errorMessage: '搜索查询不能为空' }
      },
      {
        name: '空查询参数',
        params: { query: '' },
        expected: { status: 400, success: false, errorMessage: '搜索查询不能为空' }
      }
    ];
    
    // 为每个测试用例运行测试
    testCases.forEach((tc) => {
      it(tc.name, async () => {
        // 创建模拟请求和响应对象
        const mockRequest = {
          query: tc.params,
          body: { userId: 'user123' }
        } as unknown as Request;
        
        const mockResponse = createMockResponse();
        const res = mockResponseAsResponse(mockResponse);
        
        // 调用控制器方法
        await knowledgeController.searchKnowledge(mockRequest, res);
        
        // 验证状态码
        expect(mockResponse.status).toHaveBeenCalledWith(tc.expected.status);
        
        // 验证响应
        const jsonCall = mockResponse.json.mock.calls[0][0] as MockedResponse;
        expect(jsonCall).toBeDefined();
        
        if (tc.expected.success) {
          // 成功响应应包含结果
          expect(jsonCall.results).toBeDefined();
          expect(jsonCall.meta).toBeDefined();
        } else {
          // 错误响应应包含错误信息
          expect(jsonCall.error).toBeDefined();
          
          if (tc.expected.errorMessage) {
            expect(jsonCall.error).toContain(tc.expected.errorMessage);
          }
        }
      });
    });
  });

  describe('RAG生成 - 参数化测试', () => {
    // 定义测试用例
    interface RAGTestCase {
      name: string;
      body: {
        query?: string;
        context?: string;
        domainFilters?: string[];
        typeFilters?: string[];
        useSpecialized?: boolean;
        sessionId?: string;
      };
      expected: {
        status: number;
        success: boolean;
        errorMessage?: string;
      };
    }

    const ragTestCases: RAGTestCase[] = [
      // 成功情况
      {
        name: '基本RAG生成',
        body: { 
          query: '健康知识问题'
        },
        expected: { status: 200, success: true }
      },
      {
        name: '带会话上下文的RAG生成',
        body: { 
          query: '健康知识问题', 
          sessionId: 'session123',
          domainFilters: ['health']
        },
        expected: { status: 200, success: true }
      },
      
      // 错误情况
      {
        name: '缺少查询参数',
        body: {},
        expected: { 
          status: 400, 
          success: false, 
          errorMessage: 'RAG查询不能为空' 
        }
      }
    ];

    // 运行RAG测试用例
    ragTestCases.forEach(tc => {
      it(tc.name, async () => {
        // 创建模拟请求和响应对象
        const mockRequest = {
          body: tc.body
        } as Request;
        
        const mockResponse = createMockResponse();
        const res = mockResponseAsResponse(mockResponse);
        
        // 调用控制器方法
        await knowledgeController.generateRAGResponse(mockRequest, res);
        
        // 验证状态码
        expect(mockResponse.status).toHaveBeenCalledWith(tc.expected.status);
        
        // 验证响应
        const jsonCall = mockResponse.json.mock.calls[0][0] as MockedResponse;
        expect(jsonCall).toBeDefined();
        
        if (tc.expected.success) {
          expect(jsonCall.response).toBeDefined();
          expect(jsonCall.sources).toBeDefined();
        } else {
          expect(jsonCall.error).toBeDefined();
          
          if (tc.expected.errorMessage) {
            expect(jsonCall.error).toContain(tc.expected.errorMessage);
          }
        }
      });
    });
  });
}); 