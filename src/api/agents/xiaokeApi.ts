import axios from 'axios';
import { AGENT_SERVICE_PORTS } from '../../config/constants';

// 创建专门的小克服务客户端
const xiaokeClient = axios.create({
  baseURL: `http://localhost:${AGENT_SERVICE_PORTS.XIAOKE}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 资源调度请求类型
export interface ResourceScheduleRequest {
  userId: string;
  resourceType: 'doctor' | 'hospital' | 'medicine' | 'therapy';
  requirements: {
    specialty?: string;
    location?: string;
    timeSlot?: string;
    urgency?: 'low' | 'medium' | 'high';
  };
  userProfile: {
    constitution?: string;
    symptoms?: string[];
    medicalHistory?: string;
  };
}

// 产品定制请求类型
export interface ProductCustomizationRequest {
  userId: string;
  productType: 'agricultural' | 'medicine' | 'food' | 'supplement';
  constitution: string;
  preferences: {
    organic?: boolean;
    dietary_restrictions?: string[];
    budget_range?: string;
    delivery_region?: string;
  };
  customization: {
    quantity?: number;
    packaging?: string;
    special_requirements?: string;
  };
}

// 食疗方案请求类型
export interface DietPlanRequest {
  userId: string;
  constitution: string;
  currentSymptoms?: string[];
  season: string;
  preferences: {
    cuisine_style?: string[];
    allergies?: string[];
    dietary_restrictions?: string[];
  };
  goals: string[];
}

// 订阅管理请求类型
export interface SubscriptionRequest {
  userId: string;
  planType: 'basic' | 'premium' | 'professional';
  duration: 'monthly' | 'yearly';
  features?: string[];
  autoRenewal?: boolean;
}

// 支付处理请求类型
export interface PaymentRequest {
  userId: string;
  amount: number;
  currency: string;
  paymentMethod: 'alipay' | 'wechat' | 'card';
  orderType: 'product' | 'subscription' | 'service';
  orderId: string;
}

// 小克智能体API服务
const xiaokeApi = {
  /**
   * 调度医疗资源
   * @param data 资源调度请求数据
   * @returns 调度结果
   */
  scheduleResources: async (data: ResourceScheduleRequest) => {
    try {
      const response = await xiaokeClient.post('/api/v1/resources/schedule', {
        user_id: data.userId,
        resource_type: data.resourceType,
        requirements: data.requirements,
        user_profile: data.userProfile
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '资源调度失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 管理预约
   * @param appointmentId 预约ID
   * @param action 操作类型
   * @returns 操作结果
   */
  manageAppointment: async (appointmentId: string, action: 'confirm' | 'cancel' | 'reschedule', newTime?: string) => {
    try {
      const response = await xiaokeClient.post(`/api/v1/appointments/${appointmentId}/${action}`, {
        new_time: newTime
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '预约管理失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 定制农产品
   * @param data 产品定制请求数据
   * @returns 定制结果
   */
  customizeProducts: async (data: ProductCustomizationRequest) => {
    try {
      const response = await xiaokeClient.post('/api/v1/products/customize', {
        user_id: data.userId,
        product_type: data.productType,
        constitution: data.constitution,
        preferences: data.preferences,
        customization: data.customization
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '产品定制失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 产品溯源
   * @param productId 产品ID
   * @returns 溯源信息
   */
  traceProduct: async (productId: string) => {
    try {
      const response = await xiaokeClient.get(`/api/v1/products/${productId}/trace`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '产品溯源查询失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 推荐产品
   * @param userId 用户ID
   * @param constitution 体质类型
   * @param category 产品类别
   * @returns 推荐产品列表
   */
  recommendProducts: async (userId: string, constitution: string, category?: string) => {
    try {
      const response = await xiaokeClient.get('/api/v1/products/recommend', {
        params: {
          user_id: userId,
          constitution: constitution,
          category: category
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '产品推荐失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 生成食疗方案
   * @param data 食疗方案请求数据
   * @returns 食疗方案
   */
  generateDietPlan: async (data: DietPlanRequest) => {
    try {
      const response = await xiaokeClient.post('/api/v1/diet/plan', {
        user_id: data.userId,
        constitution: data.constitution,
        current_symptoms: data.currentSymptoms,
        season: data.season,
        preferences: data.preferences,
        goals: data.goals
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '生成食疗方案失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 检查食物药物配伍
   * @param foods 食物列表
   * @param medicines 药物列表
   * @returns 配伍检查结果
   */
  checkFoodMedicinePairing: async (foods: string[], medicines: string[]) => {
    try {
      const response = await xiaokeClient.post('/api/v1/diet/check-pairing', {
        foods: foods,
        medicines: medicines
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '配伍检查失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 推荐食谱
   * @param constitution 体质类型
   * @param preferences 偏好设置
   * @returns 推荐食谱
   */
  recommendRecipes: async (constitution: string, preferences: any) => {
    try {
      const response = await xiaokeClient.get('/api/v1/diet/recipes', {
        params: {
          constitution: constitution,
          preferences: JSON.stringify(preferences)
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '食谱推荐失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 管理订阅
   * @param data 订阅请求数据
   * @returns 订阅结果
   */
  manageSubscription: async (data: SubscriptionRequest) => {
    try {
      const response = await xiaokeClient.post('/api/v1/subscription/manage', {
        user_id: data.userId,
        plan_type: data.planType,
        duration: data.duration,
        features: data.features,
        auto_renewal: data.autoRenewal
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '订阅管理失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 处理支付
   * @param data 支付请求数据
   * @returns 支付结果
   */
  processPayment: async (data: PaymentRequest) => {
    try {
      const response = await xiaokeClient.post('/api/v1/payment/process', {
        user_id: data.userId,
        amount: data.amount,
        currency: data.currency,
        payment_method: data.paymentMethod,
        order_type: data.orderType,
        order_id: data.orderId
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '支付处理失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 处理订阅支付
   * @param subscriptionId 订阅ID
   * @param paymentData 支付数据
   * @returns 支付结果
   */
  processSubscriptionPayment: async (subscriptionId: string, paymentData: Partial<PaymentRequest>) => {
    try {
      const response = await xiaokeClient.post(`/api/v1/subscription/${subscriptionId}/payment`, paymentData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '订阅支付失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取用户订单历史
   * @param userId 用户ID
   * @param limit 限制数量
   * @param offset 偏移量
   * @returns 订单历史
   */
  getUserOrders: async (userId: string, limit: number = 20, offset: number = 0) => {
    try {
      const response = await xiaokeClient.get('/api/v1/orders', {
        params: {
          user_id: userId,
          limit: limit,
          offset: offset
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取订单历史失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 健康检查
   * @returns 健康状态
   */
  healthCheck: async () => {
    try {
      const response = await xiaokeClient.get('/health');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '健康检查失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },
};

export default xiaokeApi;