/**
 * 商业化引擎单元测试
 */

import { Product, Subscription } from '../../../types/business';
import {
    CommercializationEngine,
    createCommercializationEngine,
    SubscriptionTier
} from '../CommercializationEngine';

// 模拟服务
const mockRecommender = {
  generateRecommendations: jest.fn()
};

const mockSubscriptionManager = {
  getAvailableSubscriptions: jest.fn(),
  getSubscriptionByTier: jest.fn(),
  changeSubscription: jest.fn(),
  getCustomerSubscription: jest.fn()
};

const mockPaymentProcessor = {
  processTransaction: jest.fn()
};

const mockAnalyticsService = {
  getCustomerProfile: jest.fn(),
  trackPurchase: jest.fn(),
  trackSubscriptionChange: jest.fn(),
  getRevenueMetrics: jest.fn(),
  getCustomerPurchases: jest.fn()
};

// 测试数据
const mockProducts: Product[] = [
  {
    id: 'prod-1',
    name: '冬虫夏草胶囊',
    description: '提高免疫力，补肺益肾',
    price: 299.99,
    category: 'tcm_formula',
    imageUrl: 'https://example.com/images/dongchongxiacao.jpg',
    inStock: true,
    rating: 4.8,
    tags: ['补肾', '益肺', '增强免疫力', '冬季'],
    details: {
      usage: '每日2次，每次2粒',
      ingredients: ['冬虫夏草提取物', '蜂蜜', '人参提取物']
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z'
  },
  {
    id: 'prod-2',
    name: '智能脉诊仪',
    description: '高精度脉象检测设备，配合APP使用',
    price: 1299.99,
    category: 'smart_device',
    imageUrl: 'https://example.com/images/pulse-device.jpg',
    inStock: true,
    rating: 4.5,
    tags: ['设备', '脉诊', '智能', '便携'],
    details: {
      battery: '锂电池，续航30天',
      connectivity: 'Bluetooth 5.0',
      compatibility: 'iOS 14+, Android 10+'
    },
    createdAt: '2025-02-15T00:00:00Z',
    updatedAt: '2025-05-20T00:00:00Z'
  }
];

const mockSubscriptions: Subscription[] = [
  {
    id: 'sub-free',
    name: '免费版',
    description: '基础健康管理功能',
    tier: 'free',
    price: 0,
    billingCycle: 'monthly',
    features: ['基础健康记录', '健康资讯', '限量中医知识']
  },
  {
    id: 'sub-premium',
    name: '高级会员',
    description: '全方位健康管理与个性化服务',
    tier: 'premium',
    price: 99.99,
    billingCycle: 'monthly',
    features: ['专业健康分析', '个性化推荐', '无限中医知识库', '专家咨询'],
    discountPercentage: 15,
    trialDays: 14,
    isPopular: true
  }
];

describe('商业化引擎测试', () => {
  let commercializationEngine: CommercializationEngine;
  
  beforeEach(() => {
    // 重置所有模拟函数
    jest.clearAllMocks();
    
    // 创建引擎实例
    commercializationEngine = createCommercializationEngine(
      mockRecommender,
      mockSubscriptionManager,
      mockPaymentProcessor,
      mockAnalyticsService
    );
  });
  
  describe('推荐产品功能', () => {
    it('应该返回推荐的产品列表', async () => {
      // 设置模拟
      mockRecommender.generateRecommendations.mockResolvedValue(mockProducts);
      
      // 执行测试
      const result = await commercializationEngine.recommendProducts('customer-123', 2);
      
      // 验证结果
      expect(result).toEqual(mockProducts);
      expect(mockRecommender.generateRecommendations).toHaveBeenCalledWith(
        expect.any(Object),
        2
      );
    });
    
    it('应该在发生错误时返回空数组', async () => {
      // 设置模拟
      mockRecommender.generateRecommendations.mockRejectedValue(new Error('推荐失败'));
      
      // 执行测试
      const result = await commercializationEngine.recommendProducts('customer-123');
      
      // 验证结果
      expect(result).toEqual([]);
      expect(mockRecommender.generateRecommendations).toHaveBeenCalled();
    });
  });
  
  describe('获取订阅选项功能', () => {
    it('应该返回可用的订阅选项', async () => {
      // 设置模拟
      mockSubscriptionManager.getAvailableSubscriptions.mockResolvedValue(mockSubscriptions);
      
      // 执行测试
      const result = await commercializationEngine.getSubscriptionOptions();
      
      // 验证结果
      expect(result).toEqual(mockSubscriptions);
      expect(mockSubscriptionManager.getAvailableSubscriptions).toHaveBeenCalled();
    });
  });
  
  describe('处理支付功能', () => {
    it('成功支付应该返回true并记录交易', async () => {
      // 设置模拟
      mockPaymentProcessor.processTransaction.mockResolvedValue({
        success: true,
        transactionId: 'tx-12345'
      });
      
      // 执行测试
      const result = await commercializationEngine.processPayment(
        'customer-123',
        299.99,
        'prod-1'
      );
      
      // 验证结果
      expect(result).toBe(true);
      expect(mockPaymentProcessor.processTransaction).toHaveBeenCalledWith(
        expect.objectContaining({
          customerId: 'customer-123',
          amount: 299.99,
          productId: 'prod-1'
        })
      );
      expect(mockAnalyticsService.trackPurchase).toHaveBeenCalledWith(
        'customer-123',
        'prod-1',
        299.99
      );
    });
    
    it('支付失败应该返回false且不记录交易', async () => {
      // 设置模拟
      mockPaymentProcessor.processTransaction.mockResolvedValue({
        success: false
      });
      
      // 执行测试
      const result = await commercializationEngine.processPayment(
        'customer-123',
        299.99,
        'prod-1'
      );
      
      // 验证结果
      expect(result).toBe(false);
      expect(mockPaymentProcessor.processTransaction).toHaveBeenCalled();
      expect(mockAnalyticsService.trackPurchase).not.toHaveBeenCalled();
    });
    
    it('处理支付出错应该返回false', async () => {
      // 设置模拟
      mockPaymentProcessor.processTransaction.mockRejectedValue(new Error('支付处理失败'));
      
      // 执行测试
      const result = await commercializationEngine.processPayment(
        'customer-123',
        299.99,
        'prod-1'
      );
      
      // 验证结果
      expect(result).toBe(false);
      expect(mockPaymentProcessor.processTransaction).toHaveBeenCalled();
      expect(mockAnalyticsService.trackPurchase).not.toHaveBeenCalled();
    });
  });
  
  describe('升级订阅功能', () => {
    it('应该成功升级订阅并记录变更', async () => {
      // 设置模拟
      const premiumSubscription = mockSubscriptions[1];
      mockSubscriptionManager.getSubscriptionByTier.mockResolvedValue(premiumSubscription);
      mockSubscriptionManager.changeSubscription.mockResolvedValue(true);
      
      // 执行测试
      const result = await commercializationEngine.upgradeSubscription(
        'customer-123',
        SubscriptionTier.PREMIUM
      );
      
      // 验证结果
      expect(result).toBe(true);
      expect(mockSubscriptionManager.getSubscriptionByTier).toHaveBeenCalledWith(
        SubscriptionTier.PREMIUM
      );
      expect(mockSubscriptionManager.changeSubscription).toHaveBeenCalledWith(
        'customer-123',
        premiumSubscription.id
      );
      expect(mockAnalyticsService.trackSubscriptionChange).toHaveBeenCalledWith(
        'customer-123',
        SubscriptionTier.PREMIUM,
        premiumSubscription.price
      );
    });
    
    it('当找不到订阅计划时应该抛出错误', async () => {
      // 设置模拟
      mockSubscriptionManager.getSubscriptionByTier.mockResolvedValue(null);
      
      // 执行测试
      const result = await commercializationEngine.upgradeSubscription(
        'customer-123',
        SubscriptionTier.ENTERPRISE
      );
      
      // 验证结果
      expect(result).toBe(false);
      expect(mockSubscriptionManager.getSubscriptionByTier).toHaveBeenCalledWith(
        SubscriptionTier.ENTERPRISE
      );
      expect(mockSubscriptionManager.changeSubscription).not.toHaveBeenCalled();
      expect(mockAnalyticsService.trackSubscriptionChange).not.toHaveBeenCalled();
    });
  });
  
  describe('获取收入指标功能', () => {
    it('应该返回指定期间的收入指标', async () => {
      // 设置模拟数据
      const mockMetrics = {
        totalRevenue: 125000,
        subscriptionRevenue: 75000,
        productRevenue: 50000,
        newCustomers: 150,
        churnRate: 0.03
      };
      mockAnalyticsService.getRevenueMetrics.mockResolvedValue(mockMetrics);
      
      // 执行测试
      const result = await commercializationEngine.getRevenueMetrics('2025-Q2');
      
      // 验证结果
      expect(result).toEqual(mockMetrics);
      expect(mockAnalyticsService.getRevenueMetrics).toHaveBeenCalledWith('2025-Q2');
    });
  });
  
  describe('计算客户终身价值功能', () => {
    it('应该正确计算包含订阅和购买历史的终身价值', async () => {
      // 设置模拟数据
      const purchaseHistory = [
        { productId: 'prod-1', amount: 299.99 },
        { productId: 'prod-2', amount: 1299.99 }
      ];
      
      const subscriptionData = {
        isActive: true,
        monthlyFee: 99.99
      };
      
      mockAnalyticsService.getCustomerPurchases.mockResolvedValue(purchaseHistory);
      mockSubscriptionManager.getCustomerSubscription.mockResolvedValue(subscriptionData);
      
      // 执行测试
      const result = await commercializationEngine.calculateLifetimeValue('customer-123');
      
      // 验证结果 
      // LTV = 购买总额 + 月费 * 预期月数
      // LTV = (299.99 + 1299.99) + (99.99 * 24)
      const expectedLTV = 1599.98 + (99.99 * 24);
      
      expect(result).toBeCloseTo(expectedLTV, 2);
      expect(mockAnalyticsService.getCustomerPurchases).toHaveBeenCalledWith('customer-123');
      expect(mockSubscriptionManager.getCustomerSubscription).toHaveBeenCalledWith('customer-123');
    });
    
    it('应该正确计算没有活跃订阅的客户终身价值', async () => {
      // 设置模拟数据
      const purchaseHistory = [
        { productId: 'prod-1', amount: 299.99 }
      ];
      
      const subscriptionData = {
        isActive: false
      };
      
      mockAnalyticsService.getCustomerPurchases.mockResolvedValue(purchaseHistory);
      mockSubscriptionManager.getCustomerSubscription.mockResolvedValue(subscriptionData);
      
      // 执行测试
      const result = await commercializationEngine.calculateLifetimeValue('customer-123');
      
      // 验证结果
      expect(result).toBeCloseTo(299.99, 2);
      expect(mockAnalyticsService.getCustomerPurchases).toHaveBeenCalledWith('customer-123');
      expect(mockSubscriptionManager.getCustomerSubscription).toHaveBeenCalledWith('customer-123');
    });
  });
}); 