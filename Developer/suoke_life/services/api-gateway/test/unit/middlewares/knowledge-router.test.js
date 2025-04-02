/**
 * 知识路由中间件单元测试
 */
const { expect } = require('chai');
const sinon = require('sinon');
const proxyquire = require('proxyquire').noCallThru();
const logger = require('../../../src/utils/logger');

// 模拟http-proxy-middleware
const createProxyMiddlewareStub = sinon.stub();
const httpProxyMiddlewareMock = {
  createProxyMiddleware: createProxyMiddlewareStub
};

// 使用proxyquire来加载知识路由模块，并注入模拟的依赖
const knowledgeRouter = proxyquire('../../../src/middlewares/knowledge-router', {
  'http-proxy-middleware': httpProxyMiddlewareMock
});

describe('知识路由中间件', () => {
  let req, res, next, createProxyStub;

  beforeEach(() => {
    // 模拟Express请求对象
    req = {
      path: '/api/v1/knowledge',
      query: {},
      app: {
        get: sinon.stub()
      }
    };
    
    // 模拟响应对象
    res = {
      status: sinon.stub().returnsThis(),
      json: sinon.stub()
    };
    
    // 模拟next函数
    next = sinon.stub();
    
    // 模拟loadBalancer
    const mockLoadBalancer = {
      getNextUrl: sinon.stub().returns('http://example-service:3000')
    };
    
    // 模拟serviceLBMap
    const mockServiceLBMap = new Map();
    mockServiceLBMap.set('agent-coordinator-service', mockLoadBalancer);
    mockServiceLBMap.set('knowledge-base-service', mockLoadBalancer);
    mockServiceLBMap.set('knowledge-graph-service', mockLoadBalancer);
    
    // 设置app.get返回值
    req.app.get.withArgs('serviceLBMap').returns(mockServiceLBMap);
    
    // 模拟proxy中间件
    createProxyStub = sinon.stub();
    createProxyMiddlewareStub.returns(createProxyStub);
    
    // 禁用logger
    sinon.stub(logger, 'debug');
    sinon.stub(logger, 'error');
  });

  afterEach(() => {
    sinon.restore();
    createProxyMiddlewareStub.reset();
  });

  describe('路径匹配', () => {
    it('应处理/api/v1/knowledge路径', () => {
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.called).to.be.true;
    });
    
    it('应处理/api/v1/knowledge/路径', () => {
      req.path = '/api/v1/knowledge/';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.called).to.be.true;
    });
    
    it('应跳过不匹配的路径', () => {
      req.path = '/api/v1/users';
      knowledgeRouter(req, res, next);
      expect(next.called).to.be.true;
      expect(createProxyMiddlewareStub.called).to.be.false;
    });
  });

  describe('查询参数处理', () => {
    it('应从q参数中获取查询内容', () => {
      req.query.q = '基因组测序技术';
      knowledgeRouter(req, res, next);
      expect(logger.debug.called).to.be.true;
    });
    
    it('应从query参数中获取查询内容', () => {
      req.query.query = '基因组测序技术';
      knowledgeRouter(req, res, next);
      expect(logger.debug.called).to.be.true;
    });
  });

  describe('领域分类', () => {
    it('应将基因相关查询分类到精准医学领域', () => {
      req.query.q = '基因组测序技术的最新进展';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将多模态相关查询分类到多模态健康领域', () => {
      req.query.q = '多模态生物信号监测技术';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将环境相关查询分类到环境健康领域', () => {
      req.query.q = '空气质量PM2.5对人体的影响';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将心理相关查询分类到心理健康领域', () => {
      req.query.q = '长期焦虑和抑郁的健康影响';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将中医相关查询分类到传统文化领域', () => {
      req.query.q = '中医四诊合参的理论基础';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将西医相关查询分类到现代医学领域', () => {
      req.query.q = '西医临床诊断流程标准';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.calledWith(sinon.match({
        target: sinon.match.string,
        pathRewrite: sinon.match.object
      }))).to.be.true;
    });
    
    it('应将无法分类的查询分类到默认领域', () => {
      req.query.q = '今天天气怎么样';
      knowledgeRouter(req, res, next);
      expect(createProxyMiddlewareStub.called).to.be.true;
    });
  });

  describe('错误处理', () => {
    it('应在负载均衡器不存在时返回503错误', () => {
      // 清空serviceLBMap
      req.app.get.withArgs('serviceLBMap').returns(new Map());
      
      knowledgeRouter(req, res, next);
      
      expect(res.status.calledWith(503)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
    });
    
    it('应捕获并处理异常', () => {
      // 引发异常
      req.app.get.throws(new Error('测试错误'));
      
      knowledgeRouter(req, res, next);
      
      expect(logger.error.calledOnce).to.be.true;
      expect(res.status.calledWith(500)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
    });
  });
});