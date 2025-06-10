/**
 * 索克生活商业化模块类型定义
 */

// 产品接口
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl?: string;
  inStock: boolean;
  rating?: number;
  tags: string[];
  details: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// 订阅接口
export interface Subscription {
  id: string;
  name: string;
  description: string;
  tier: string;
  price: number;
  billingCycle: 'monthly' | 'quarterly' | 'yearly';
  features: string[];
  discountPercentage?: number;
  trialDays?: number;
  isPopular?: boolean;
}

// 客户接口
export interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  subscriptionId?: string;
  subscriptionStatus?: 'active' | 'canceled' | 'paused' | 'trialing';
  subscriptionStartDate?: string;
  subscriptionEndDate?: string;
  paymentMethods: PaymentMethod[];
  address?: Address;
  preferences: Record<string, any>;
  healthProfile: HealthProfile;
  createdAt: string;
  updatedAt: string;
}

// 付款方式接口
export interface PaymentMethod {
  id: string;
  type: 'credit_card' | 'alipay' | 'wechat_pay' | 'bank_transfer';
  isDefault: boolean;
  lastFour?: string; // 信用卡后四位
  expiryDate?: string; // 信用卡到期日期
  cardholderName?: string;
}

// 地址接口
export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

// 健康档案接口
export interface HealthProfile {
  age: number;
  gender: string;
  height?: number; // cm
  weight?: number; // kg
  conditions?: string[];
  allergies?: string[];
  medications?: string[];
  lifestyleFactors?: Record<string, any>;
  tcmConstitution?: string; // 中医体质类型
}

// 定价层级
export interface PricingTier {
  id: string;
  name: string;
  monthlyPrice: number;
  yearlyPrice: number;
  features: string[];
  isRecommended?: boolean;
}

// 订单接口
export interface Order {
  id: string;
  customerId: string;
  products: OrderItem[];
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'canceled';
  totalAmount: number;
  paymentStatus: 'unpaid' | 'paid' | 'refunded' | 'partially_refunded';
  paymentMethod: string;
  shippingAddress: Address;
  trackingNumber?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// 订单项接口
export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

// 收入报告接口
export interface RevenueReport {
  period: string;
  totalRevenue: number;
  subscriptionRevenue: number;
  productRevenue: number;
  serviceRevenue: number;
  newCustomers: number;
  churnRate: number;
  averageOrderValue: number;
  lifetimeValue: number;
}

// 推荐结果接口
export interface Recommendation {
  productId: string;
  score: number;
  reason: string;
}

// 导出所有商业模块相关类型
export type BusinessModuleTypes = {
  Product: Product;
  Subscription: Subscription;
  Customer: Customer;
  PaymentMethod: PaymentMethod;
  Address: Address;
  HealthProfile: HealthProfile;
  PricingTier: PricingTier;
  Order: Order;
  OrderItem: OrderItem;
  RevenueReport: RevenueReport;
  Recommendation: Recommendation;
};