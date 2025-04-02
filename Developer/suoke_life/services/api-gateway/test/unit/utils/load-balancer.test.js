/**
 * 负载均衡器单元测试
 */
const { expect } = require('chai');
const sinon = require('sinon');
const LoadBalancer = require('../../../src/utils/load-balancer');

describe('LoadBalancer', () => {
  let loadBalancer;
  const urls = ['http://service1:3000', 'http://service2:3000', 'http://service3:3000'];

  beforeEach(() => {
    loadBalancer = new LoadBalancer('test-service', urls);
  });

  afterEach(() => {
    sinon.restore();
  });

  describe('初始化', () => {
    it('应正确初始化服务名称和URL列表', () => {
      expect(loadBalancer.serviceName).to.equal('test-service');
      expect(loadBalancer.urls).to.deep.equal(urls);
    });

    it('默认策略应为轮询', () => {
      expect(loadBalancer.strategy).to.equal('round-robin');
    });
  });

  describe('轮询策略', () => {
    it('应按顺序返回URL', () => {
      expect(loadBalancer.getNextUrl()).to.equal('http://service1:3000');
      expect(loadBalancer.getNextUrl()).to.equal('http://service2:3000');
      expect(loadBalancer.getNextUrl()).to.equal('http://service3:3000');
      // 循环返回
      expect(loadBalancer.getNextUrl()).to.equal('http://service1:3000');
    });
  });

  describe('随机策略', () => {
    it('应随机返回URL', () => {
      loadBalancer.setStrategy('random');
      
      // 使用sinon来模拟Math.random返回值
      const stub = sinon.stub(Math, 'random');
      
      stub.returns(0.1); // 第一次调用返回0.1
      expect(loadBalancer.getNextUrl()).to.equal('http://service1:3000');
      
      stub.returns(0.4); // 第二次调用返回0.4
      expect(loadBalancer.getNextUrl()).to.equal('http://service2:3000');
      
      stub.returns(0.8); // 第三次调用返回0.8
      expect(loadBalancer.getNextUrl()).to.equal('http://service3:3000');
    });
  });

  describe('加权轮询策略', () => {
    it('应根据权重返回URL', () => {
      loadBalancer.setStrategy('weighted');
      loadBalancer.setWeights({
        'http://service1:3000': 5,
        'http://service2:3000': 3,
        'http://service3:3000': 2
      });

      // 模拟随机数生成
      const stub = sinon.stub(Math, 'random');
      
      // 总权重是10，所以:
      // 0-0.5 (权重5) 返回service1
      // 0.5-0.8 (权重3) 返回service2
      // 0.8-1.0 (权重2) 返回service3
      
      stub.returns(0.1);
      expect(loadBalancer.getNextUrl()).to.equal('http://service1:3000');
      
      stub.returns(0.6);
      expect(loadBalancer.getNextUrl()).to.equal('http://service2:3000');
      
      stub.returns(0.9);
      expect(loadBalancer.getNextUrl()).to.equal('http://service3:3000');
    });
  });

  describe('主动健康检查', () => {
    it('应标记健康状态并排除不健康的URL', async () => {
      // 模拟健康检查函数
      const healthCheck = sinon.stub();
      healthCheck.withArgs('http://service1:3000').resolves(true);
      healthCheck.withArgs('http://service2:3000').resolves(false);
      healthCheck.withArgs('http://service3:3000').resolves(true);
      
      await loadBalancer.checkHealth(healthCheck);
      
      // 验证健康状态
      expect(loadBalancer.healthStatus.get('http://service1:3000')).to.be.true;
      expect(loadBalancer.healthStatus.get('http://service2:3000')).to.be.false;
      expect(loadBalancer.healthStatus.get('http://service3:3000')).to.be.true;
      
      // 验证只返回健康的URL
      const healthyUrls = [];
      for (let i = 0; i < 4; i++) {
        healthyUrls.push(loadBalancer.getNextUrl());
      }
      
      expect(healthyUrls).to.not.include('http://service2:3000');
      expect(healthyUrls).to.include('http://service1:3000');
      expect(healthyUrls).to.include('http://service3:3000');
    });
  });

  describe('URL管理', () => {
    it('应能添加新的URL', () => {
      loadBalancer.addUrl('http://service4:3000');
      expect(loadBalancer.urls).to.include('http://service4:3000');
    });

    it('应能移除URL', () => {
      loadBalancer.removeUrl('http://service2:3000');
      expect(loadBalancer.urls).to.not.include('http://service2:3000');
    });

    it('应在没有可用URL时抛出错误', () => {
      loadBalancer.urls = [];
      expect(() => loadBalancer.getNextUrl()).to.throw('没有可用的服务URL');
    });
  });

  describe('性能监控', () => {
    it('应跟踪请求计数', () => {
      loadBalancer.getNextUrl();
      loadBalancer.getNextUrl();
      loadBalancer.getNextUrl();
      
      expect(loadBalancer.getTotalRequests()).to.equal(3);
    });

    it('应记录每个URL的请求数', () => {
      // 完全重新初始化一个干净的负载均衡器，避免之前测试的影响
      const testLb = new LoadBalancer('test-lb', [
        'http://service1:3000', 
        'http://service2:3000', 
        'http://service3:3000'
      ]);
      
      // 使用固定轮询防止随机结果
      testLb.strategy = 'round-robin';
      testLb.currentIndex = 0;
      
      // 依次获取服务
      testLb.getNextUrl(); // service1
      testLb.getNextUrl(); // service2 
      testLb.getNextUrl(); // service3
      testLb.getNextUrl(); // service1 (第二次)
      
      // 检查统计结果
      const stats = testLb.getUrlStats();
      expect(stats).to.have.property('http://service1:3000', 2);
      expect(stats).to.have.property('http://service2:3000', 1);
      expect(stats).to.have.property('http://service3:3000', 1);
    });
  });
});