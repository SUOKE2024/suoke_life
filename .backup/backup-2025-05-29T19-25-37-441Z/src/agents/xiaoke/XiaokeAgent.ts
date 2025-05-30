import {
  XiaokeAgent,
  ServiceRecommendation,
  DoctorMatch,
  ProductInfo,
  SupplyChainInfo,
  AppointmentInfo,
  UserProfile,
  ServiceContext,
} from './types';
import { apiClient } from '../../services/apiClient';

/**
 * 小克智能体主类
 * SUOKE频道版主，负责服务订阅、农产品预制、供应链管理等商业化服务
 */
export class XiaokeAgentImpl implements XiaokeAgent {
  private personality: any = {
    style: 'professional', // 专业型
    tone: 'efficient',     // 高效的语调
    expertise: 'business', // 商业专业
    approach: 'service-oriented', // 服务导向
  };

  private serviceEndpoint = '/api/agents/xiaoke';

  constructor() {
    // 初始化小克智能体
  }

  /**
   * 核心消息处理功能
   */
  async processMessage(
    message: string,
    context: ServiceContext,
    userId?: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/message`, {
        text: message,
        context,
        user_id: userId,
        session_id: sessionId,
      });

      // 应用个性化风格
      response.data.text = this.applyPersonalityToResponse(response.data.text, context);
      
      return response.data;
    } catch (error) {
      console.error('小克消息处理失败:', error);
      return this.generateFallbackResponse(message, context);
    }
  }

  /**
   * 推荐服务
   */
  async recommendServices(
    userProfile: UserProfile,
    healthData?: any,
    preferences?: any
  ): Promise<ServiceRecommendation[]> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/recommend-service`, {
        user_profile: userProfile,
        health_data: healthData,
        preferences: preferences,
      });

      return response.data.map((rec: any) => ({
        id: rec.id,
        name: rec.name,
        category: rec.category,
        description: rec.description,
        price: rec.price,
        rating: rec.rating,
        provider: rec.provider,
        availability: rec.availability,
        matchScore: rec.match_score,
        benefits: rec.benefits || [],
        requirements: rec.requirements || [],
        estimatedDuration: rec.estimated_duration,
        location: rec.location,
      }));
    } catch (error) {
      console.error('服务推荐失败:', error);
      return [];
    }
  }

  /**
   * 匹配医生
   */
  async matchDoctors(
    symptoms: string[],
    specialty?: string,
    location?: string,
    preferences?: any
  ): Promise<DoctorMatch[]> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/match-doctor`, {
        symptoms,
        specialty,
        location,
        preferences,
      });

      return response.data.map((match: any) => ({
        doctorId: match.doctor_id,
        name: match.name,
        specialty: match.specialty,
        hospital: match.hospital,
        rating: match.rating,
        experience: match.experience,
        availability: match.availability,
        matchScore: match.match_score,
        consultationFee: match.consultation_fee,
        languages: match.languages || [],
        certifications: match.certifications || [],
        reviews: match.reviews || [],
        location: match.location,
        distance: match.distance,
      }));
    } catch (error) {
      console.error('医生匹配失败:', error);
      return [];
    }
  }

  /**
   * 获取产品信息
   */
  async getProductInfo(productId: string): Promise<ProductInfo | null> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/products/${productId}`);
      
      return {
        id: response.data.id,
        name: response.data.name,
        category: response.data.category,
        description: response.data.description,
        price: response.data.price,
        images: response.data.images || [],
        specifications: response.data.specifications || {},
        nutritionInfo: response.data.nutrition_info,
        origin: response.data.origin,
        certifications: response.data.certifications || [],
        availability: response.data.availability,
        rating: response.data.rating,
        reviews: response.data.reviews || [],
        supplyChain: response.data.supply_chain,
      };
    } catch (error) {
      console.error('获取产品信息失败:', error);
      return null;
    }
  }

  /**
   * 搜索产品
   */
  async searchProducts(
    query: string,
    filters?: {
      category?: string;
      priceRange?: [number, number];
      location?: string;
      organic?: boolean;
      inStock?: boolean;
    }
  ): Promise<ProductInfo[]> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/products/search`, {
        query,
        filters,
      });

      return response.data.map((product: any) => ({
        id: product.id,
        name: product.name,
        category: product.category,
        description: product.description,
        price: product.price,
        images: product.images || [],
        specifications: product.specifications || {},
        nutritionInfo: product.nutrition_info,
        origin: product.origin,
        certifications: product.certifications || [],
        availability: product.availability,
        rating: product.rating,
        reviews: product.reviews || [],
        supplyChain: product.supply_chain,
      }));
    } catch (error) {
      console.error('产品搜索失败:', error);
      return [];
    }
  }

  /**
   * 获取供应链信息
   */
  async getSupplyChainInfo(productId: string): Promise<SupplyChainInfo | null> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/supply-chain/${productId}`);
      
      return {
        productId: response.data.product_id,
        stages: response.data.stages.map((stage: any) => ({
          id: stage.id,
          name: stage.name,
          description: stage.description,
          location: stage.location,
          timestamp: new Date(stage.timestamp),
          responsible: stage.responsible,
          certifications: stage.certifications || [],
          quality: stage.quality,
          temperature: stage.temperature,
          humidity: stage.humidity,
        })),
        blockchainHash: response.data.blockchain_hash,
        verificationStatus: response.data.verification_status,
        traceabilityScore: response.data.traceability_score,
        sustainabilityMetrics: response.data.sustainability_metrics,
      };
    } catch (error) {
      console.error('获取供应链信息失败:', error);
      return null;
    }
  }

  /**
   * 创建预约
   */
  async createAppointment(
    doctorId: string,
    timeSlot: Date,
    type: 'consultation' | 'checkup' | 'follow-up',
    notes?: string
  ): Promise<AppointmentInfo | null> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/appointments`, {
        doctor_id: doctorId,
        time_slot: timeSlot.toISOString(),
        type,
        notes,
      });

      return {
        id: response.data.id,
        doctorId: response.data.doctor_id,
        patientId: response.data.patient_id,
        timeSlot: new Date(response.data.time_slot),
        type: response.data.type,
        status: response.data.status,
        notes: response.data.notes,
        location: response.data.location,
        meetingLink: response.data.meeting_link,
        reminders: response.data.reminders || [],
        createdAt: new Date(response.data.created_at),
      };
    } catch (error) {
      console.error('创建预约失败:', error);
      return null;
    }
  }

  /**
   * 获取用户预约列表
   */
  async getUserAppointments(userId: string): Promise<AppointmentInfo[]> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/appointments/user/${userId}`);
      
      return response.data.map((appointment: any) => ({
        id: appointment.id,
        doctorId: appointment.doctor_id,
        patientId: appointment.patient_id,
        timeSlot: new Date(appointment.time_slot),
        type: appointment.type,
        status: appointment.status,
        notes: appointment.notes,
        location: appointment.location,
        meetingLink: appointment.meeting_link,
        reminders: appointment.reminders || [],
        createdAt: new Date(appointment.created_at),
      }));
    } catch (error) {
      console.error('获取用户预约失败:', error);
      return [];
    }
  }

  /**
   * 订阅服务
   */
  async subscribeToService(
    serviceId: string,
    plan: 'basic' | 'premium' | 'enterprise',
    duration: number // 月数
  ): Promise<{
    subscriptionId: string;
    status: string;
    startDate: Date;
    endDate: Date;
    paymentInfo: any;
  } | null> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/services/subscribe`, {
        service_id: serviceId,
        plan,
        duration,
      });

      return {
        subscriptionId: response.data.subscription_id,
        status: response.data.status,
        startDate: new Date(response.data.start_date),
        endDate: new Date(response.data.end_date),
        paymentInfo: response.data.payment_info,
      };
    } catch (error) {
      console.error('服务订阅失败:', error);
      return null;
    }
  }

  /**
   * 获取智能体状态
   */
  async getStatus(): Promise<any> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/status`);
      return response.data;
    } catch (error) {
      console.error('获取小克状态失败:', error);
      return {
        status: 'offline',
        capabilities: [],
        performance: {
          accuracy: 0,
          responseTime: 0,
          userSatisfaction: 0,
        },
      };
    }
  }

  /**
   * 设置个性化特征
   */
  setPersonality(traits: any): void {
    this.personality = { ...this.personality, ...traits };
  }

  /**
   * 应用个性化风格到响应
   */
  private applyPersonalityToResponse(text: string, context: ServiceContext): string {
    // 根据小克的专业高效风格调整响应
    let styledText = text;

    // 添加专业性表达
    if (context.type === 'service_inquiry') {
      styledText = `基于您的需求，我为您推荐以下专业服务：${styledText}`;
    } else if (context.type === 'product_search') {
      styledText = `经过精准匹配，为您找到以下优质产品：${styledText}`;
    }

    // 添加效率导向的结尾
    if (!styledText.includes('如需')) {
      styledText += ' 如需进一步了解或预约服务，我可以立即为您安排。';
    }

    return styledText;
  }

  /**
   * 生成备用响应
   */
  private generateFallbackResponse(message: string, context: ServiceContext): any {
    return {
      text: '抱歉，我暂时无法处理您的请求。作为您的专业服务顾问，我建议您稍后重试，或者我可以为您转接人工客服。',
      type: 'fallback',
      suggestions: [
        '查看热门服务',
        '浏览推荐产品',
        '联系客服',
        '查看我的订单',
      ],
      timestamp: Date.now(),
    };
  }

  /**
   * 清理资源
   */
  async cleanup(userId: string): Promise<void> {
    try {
      // 清理用户相关的缓存和临时数据
      console.log(`清理小克智能体资源: ${userId}`);
    } catch (error) {
      console.error('清理小克资源失败:', error);
    }
  }
}

// 导出单例实例
export const xiaokeAgent = new XiaokeAgentImpl(); 