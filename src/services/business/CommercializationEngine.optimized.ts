/**
 * 商业化引擎 - 优化版本
 * 提供个性化推荐、订阅管理、支付处理等核心商业功能
 */

import { Product, Subscription, Customer, PricingTier } from '../../types/business';

// 订阅类型枚举
export enum SubscriptionTier {
  FREE = 'free',
  BASIC = 'basic',
  PREMIUM = 'premium',
  ENTERPRISE = 'enterprise'
}

// 产品类型枚举
export enum ProductCategory {
  TCM_FORMULA = 'tcm_formula',
  SMART_DEVICE = 'smart_device',
  NUTRITION = 'nutrition',
  WELLNESS_EXPERIENCE = 'wellness_experience'
}

// 商业化引擎接口
export interface CommercializationEngine {
  recommendProducts(customerId: string, limit?: number): Promise<Product[]>;
  getSubscriptionOptions(): Promise<Subscription[]>;
  processPayment(customerId: string, amount: number, productId: string): Promise<boolean>;
  upgradeSubscription(customerId: string, tier: SubscriptionTier): Promise<boolean>;
  getRevenueMetrics(period: string): Promise<Record<string, number>>;
  calculateLifetimeValue(customerId: string): Promise<number>;
}

// 商业化引擎实现
export class CommercializationEngineImpl implements CommercializationEngine {
  private productRecommender: RecommendationEngine;
  private subscriptionManager: SubscriptionManager;
  private paymentProcessor: PaymentProcessor;
  private analyticsService: AnalyticsService;

  constructor(
    recommender: RecommendationEngine,
    subscriptionMgr: SubscriptionManager,
    paymentProc: PaymentProcessor,
    analytics: AnalyticsService
  ) {
    this.productRecommender = recommender;
    this.subscriptionManager = subscriptionMgr;
    this.paymentProcessor = paymentProc;
    this.analyticsService = analytics;
  }

  // 获取个性化产品推荐
  async recommendProducts(customerId: string, limit = 5): Promise<Product[]> {
    try {
      // 获取客户数据
      const customerData = await this.analyticsService.getCustomerProfile(customerId);
      
      // 使用ML模型生成推荐
      const recommendations = await this.productRecommender.generateRecommendations(
        customerData,
        limit
      );
      
      return recommendations;
    } catch (error) {
      console.error('Error generating product recommendations:', error);
      return [];
    }
  }

  // 获取可用的订阅选项
  async getSubscriptionOptions(): Promise<Subscription[]> {
    return this.subscriptionManager.getAvailableSubscriptions();
  }

  // 处理支付
  async processPayment(customerId: string, amount: number, productId: string): Promise<boolean> {
    try {
      const paymentResult = await this.paymentProcessor.processTransaction({
        customerId,
        amount,
        productId,
        timestamp: new Date().toISOString()
      });
      
      // 记录交易
      if (paymentResult.success) {
        await this.analyticsService.trackPurchase(customerId, productId, amount);
      }
      
      return paymentResult.success;
    } catch (error) {
      console.error('Payment processing error:', error);
      return false;
    }
  }

  // 升级订阅
  async upgradeSubscription(customerId: string, tier: SubscriptionTier): Promise<boolean> {
    try {
      // 获取新的订阅计划
      const subscriptionPlan = await this.subscriptionManager.getSubscriptionByTier(tier);
      
      if (!subscriptionPlan) {
        throw new Error(`Subscription tier ${tier} not found`);
      }
      
      // 执行升级
      const upgradeResult = await this.subscriptionManager.changeSubscription(
        customerId, 
        subscriptionPlan.id
      );
      
      // 记录升级事件
      if (upgradeResult) {
        await this.analyticsService.trackSubscriptionChange(
          customerId, 
          tier, 
          subscriptionPlan.price
        );
      }
      
      return upgradeResult;
    } catch (error) {
      console.error('Subscription upgrade error:', error);
      return false;
    }
  }

  // 获取收入指标
  async getRevenueMetrics(period: string): Promise<Record<string, number>> {
    return this.analyticsService.getRevenueMetrics(period);
  }

  // 计算客户终身价值
  async calculateLifetimeValue(customerId: string): Promise<number> {
    const purchaseHistory = await this.analyticsService.getCustomerPurchases(customerId);
    const subscriptionData = await this.subscriptionManager.getCustomerSubscription(customerId);
    
    // 计算LTV (可以根据需要实现更复杂的逻辑)
    let ltv = purchaseHistory.reduce((total, purchase) => total + purchase.amount, 0);
    
    // 考虑订阅的预期收入
    if (subscriptionData && subscriptionData.isActive) {
      const monthlyValue = subscriptionData.monthlyFee;
      const expectedMonths = 24; // 假设平均订阅时长
      ltv += monthlyValue * expectedMonths;
    }
    
    return ltv;
  }
}

// 这些接口可以在其他文件中实现
interface RecommendationEngine {
  generateRecommendations(customerData: any, limit: number): Promise<Product[]>;
}

interface SubscriptionManager {
  getAvailableSubscriptions(): Promise<Subscription[]>;
  getSubscriptionByTier(tier: SubscriptionTier): Promise<Subscription | null>;
  changeSubscription(customerId: string, subscriptionId: string): Promise<boolean>;
  getCustomerSubscription(customerId: string): Promise<any>;
}

interface PaymentProcessor {
  processTransaction(transactionData: any): Promise<{success: boolean; transactionId?: string}>;
}

interface AnalyticsService {
  getCustomerProfile(customerId: string): Promise<any>;
  trackPurchase(customerId: string, productId: string, amount: number): Promise<void>;
  trackSubscriptionChange(customerId: string, tier: SubscriptionTier, price: number): Promise<void>;
  getRevenueMetrics(period: string): Promise<Record<string, number>>;
  getCustomerPurchases(customerId: string): Promise<any[]>;
}

// 工厂函数，用于创建商业化引擎实例
export function createCommercializationEngine(
  recommender: RecommendationEngine,
  subscriptionMgr: SubscriptionManager,
  paymentProc: PaymentProcessor,
  analytics: AnalyticsService
): CommercializationEngine {
  return new CommercializationEngineImpl(
    recommender,
    subscriptionMgr,
    paymentProc,
    analytics
  );
}
