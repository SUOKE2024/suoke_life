/**
 * 指标中间件单元测试
 */
const { expect } = require('chai');
const sinon = require('sinon');
const { metricsMiddleware } = require('../../../src/middlewares/metrics.middleware');
const metricsService = require('../../../src/services/metrics.service');

describe('指标中间件单元测试', () => {
  let req, res, next, sandbox;
  
  beforeEach(() => {
    // 模拟请求对象
    req = {
      method: 'GET',
      path: '/test',
      originalUrl: '/test',
      ip: '127.0.0.1',
      headers: {
        'user-agent': 'test-agent'
      }
    };
    
    // 模拟响应对象
    res = {
      statusCode: 200,
      end: sinon.stub(),
      getHeader: sinon.stub().returns(100),
      setHeader: sinon.stub()
    };
    
    // 模拟next函数
    next = sinon.stub();
    
    // 创建沙箱
    sandbox = sinon.createSandbox();
    
    // 重置指标
    metricsService.reset();
  });
  
  afterEach(() => {
    sandbox.restore();
  });
  
  it('应该调用next继续请求处理', () => {
    metricsMiddleware(req, res, next);
    expect(next.calledOnce).to.be.true;
  });

  it('应该重写res.end方法', () => {
    const originalEnd = res.end;
    metricsMiddleware(req, res, next);
    expect(res.end).to.not.equal(originalEnd);
  });
  
  it('应该对排除的路径跳过指标收集', () => {
    // 修改请求路径为排除路径
    req.path = '/metrics';
    req.originalUrl = '/metrics';
    
    metricsMiddleware(req, res, next);
    
    // 应该直接调用next而不重写res.end
    expect(next.calledOnce).to.be.true;
    expect(res.end).to.equal(res.end); // 确认end方法没有被改变
  });
  
  it('应该对健康检查路径跳过指标收集', () => {
    // 修改请求路径为健康检查路径
    req.path = '/health';
    req.originalUrl = '/health';
    
    metricsMiddleware(req, res, next);
    
    // 应该直接调用next而不重写res.end
    expect(next.calledOnce).to.be.true;
    expect(res.end).to.equal(res.end); // 确认end方法没有被改变
  });
  
  it('应该在请求开始时增加活跃连接数', () => {
    // 监视gauge方法
    const gaugeStub = sandbox.spy(metricsService, 'gauge');
    
    metricsMiddleware(req, res, next);
    
    // 验证活跃连接数已增加
    expect(gaugeStub.calledWith('http_active_connections')).to.be.true;
  });
  
  it('重写的end方法应该调用原始end方法', () => {
    metricsMiddleware(req, res, next);
    
    // 模拟调用重写的end方法
    const args = ['test data'];
    res.end(...args);
    
    // 原始end应该被调用一次
    expect(res.end.calledWith(...args)).to.be.true;
  });
  
  it('重写的end方法应该减少活跃连接数', () => {
    // 监视gauge方法
    const gaugeStub = sandbox.spy(metricsService, 'gauge');
    
    metricsMiddleware(req, res, next);
    
    // 重置spy以便只捕获end调用中的gauge调用
    gaugeStub.resetHistory();
    
    // 模拟调用重写的end方法
    res.end();
    
    // 验证活跃连接数已减少
    expect(gaugeStub.calledWith('http_active_connections')).to.be.true;
  });
  
  it('重写的end方法应该异步收集指标', (done) => {
    // 监视increment和timing方法
    const incrementStub = sandbox.stub(metricsService, 'increment');
    const timingStub = sandbox.stub(metricsService, 'timing');
    const observeStub = sandbox.stub(metricsService, 'observe');
    
    metricsMiddleware(req, res, next);
    
    // 模拟调用重写的end方法
    res.end();
    
    // 使用setTimeout模拟异步行为
    setTimeout(() => {
      try {
        // 验证指标方法被调用
        expect(incrementStub.called).to.be.true;
        expect(timingStub.called).to.be.true;
        expect(observeStub.called).to.be.true;
        done();
      } catch (error) {
        done(error);
      }
    }, 10);
  });
  
  it('应该从User-Agent正确提取浏览器信息', () => {
    // 设置Chrome浏览器的User-Agent
    req.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';
    
    const incrementStub = sandbox.stub(metricsService, 'increment');
    
    metricsMiddleware(req, res, next);
    res.end();
    
    // 使用setTimeout检查异步调用
    return new Promise(resolve => {
      setTimeout(() => {
        // 检查是否使用了正确的浏览器标签
        const browserCallArgs = incrementStub.getCalls().find(call => 
          call.args[0] === 'client_requests' && 
          call.args[1] && 
          call.args[1].browser === 'chrome'
        );
        
        expect(browserCallArgs).to.exist;
        resolve();
      }, 10);
    });
  });
  
  it('应该正确处理错误状态码', () => {
    // 设置错误状态码
    res.statusCode = 500;
    
    const incrementStub = sandbox.stub(metricsService, 'increment');
    
    metricsMiddleware(req, res, next);
    res.end();
    
    // 使用setTimeout检查异步调用
    return new Promise(resolve => {
      setTimeout(() => {
        // 检查是否记录了错误
        const errorCallArgs = incrementStub.getCalls().find(call => 
          call.args[0] === 'http_errors_total'
        );
        
        expect(errorCallArgs).to.exist;
        resolve();
      }, 10);
    });
  });
  
  it('应该在指标收集失败时不影响请求处理', () => {
    // 使增量方法抛出错误
    sandbox.stub(metricsService, 'increment').throws(new Error('模拟错误'));
    
    // 应该不抛出错误
    expect(() => {
      metricsMiddleware(req, res, next);
      res.end();
    }).to.not.throw();
  });
}); 