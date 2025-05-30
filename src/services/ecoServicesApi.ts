import AsyncStorage from "@react-native-async-storage/async-storage";
import CryptoJS from "crypto-js";
import { apiCache } from "../utils/apiCache";

// 数据类型定义
export interface FarmProduct {
  id: string;
  name: string;
  category: string;
  origin: string;
  healthBenefits: string[];
  season: string;
  price: number;
  unit: string;
  image: string;
  organic: boolean;
  stock: number;
  rating: number;
  reviews: number;
  blockchain: {
    verified: boolean;
    traceability: BlockchainTrace[];
    certifications: string[];
  };
  tcmProperties: {
    nature: string;
    flavor: string;
    meridian: string[];
    functions: string[];
    constitution: string[];
  };
  aiRecommendation?: {
    score: number;
    reason: string;
    personalizedBenefits: string[];
  };
}

export interface BlockchainTrace {
  timestamp: string;
  location: string;
  action: string;
  verifier: string;
  hash: string;
}

export interface WellnessDestination {
  id: string;
  name: string;
  location: string;
  type: "mountain" | "water" | "forest" | "hot_spring" | "temple" | "village";
  description: string;
  healthFeatures: string[];
  activities: string[];
  rating: number;
  price: number;
  image: string;
  tcmBenefits: string[];
  availability: {
    available: boolean;
    nextAvailable: string;
    capacity: number;
    booked: number;
  };
  weatherSuitability: {
    currentScore: number;
    forecast: string;
    bestTime: string;
  };
  personalizedScore?: {
    score: number;
    factors: string[];
    recommendations: string[];
  };
}

export interface NutritionPlan {
  id: string;
  name: string;
  constitution: string;
  season: string;
  meals: {
    breakfast: string[];
    lunch: string[];
    dinner: string[];
    snacks: string[];
  };
  ingredients: FarmProduct[];
  benefits: string[];
  nutritionFacts: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
  };
  aiOptimized: boolean;
}

export interface UserPreferences {
  constitution: string;
  allergies: string[];
  dietaryRestrictions: string[];
  healthGoals: string[];
  location: string;
  budget: {
    min: number;
    max: number;
  };
}

// 安全配置
const ENCRYPTION_KEY = "suoke_life_eco_services_key_2024";
const API_BASE_URL = "https://api.suokelife.com/eco";

// 性能监控
class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number[]> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  startTimer(operation: string): number {
    return Date.now();
  }

  endTimer(operation: string, startTime: number): void {
    const duration = Date.now() - startTime;
    if (!this.metrics.has(operation)) {
      this.metrics.set(operation, []);
    }
    this.metrics.get(operation)!.push(duration);

    // 保留最近100次记录
    const records = this.metrics.get(operation)!;
    if (records.length > 100) {
      records.splice(0, records.length - 100);
    }
  }

  getAverageTime(operation: string): number {
    const records = this.metrics.get(operation);
    if (!records || records.length === 0) return 0;
    return records.reduce((sum, time) => sum + time, 0) / records.length;
  }

  getMetrics(): Record<string, { average: number; count: number }> {
    const result: Record<string, { average: number; count: number }> = {};
    this.metrics.forEach((times, operation) => {
      result[operation] = {
        average: this.getAverageTime(operation),
        count: times.length,
      };
    });
    return result;
  }
}

// 数据加密工具
class DataEncryption {
  static encrypt(data: any): string {
    const jsonString = JSON.stringify(data);
    return CryptoJS.AES.encrypt(jsonString, ENCRYPTION_KEY).toString();
  }

  static decrypt(encryptedData: string): any {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
      const decryptedString = bytes.toString(CryptoJS.enc.Utf8);
      return JSON.parse(decryptedString);
    } catch (error) {
      console.error("解密失败:", error);
      return null;
    }
  }
}

// 隐私保护工具
class PrivacyManager {
  private static sensitiveFields = ["location", "allergies", "healthGoals"];

  static anonymizeData(data: any): any {
    const anonymized = { ...data };
    this.sensitiveFields.forEach((field) => {
      if (anonymized[field]) {
        anonymized[field] = this.hashSensitiveData(anonymized[field]);
      }
    });
    return anonymized;
  }

  private static hashSensitiveData(data: any): string {
    return CryptoJS.SHA256(JSON.stringify(data)).toString();
  }

  static async getUserConsent(dataType: string): Promise<boolean> {
    try {
      const consent = await AsyncStorage.getItem(`consent_${dataType}`);
      return consent === "true";
    } catch (error) {
      console.error("获取用户同意状态失败:", error);
      return false;
    }
  }

  static async setUserConsent(
    dataType: string,
    consent: boolean
  ): Promise<void> {
    try {
      await AsyncStorage.setItem(`consent_${dataType}`, consent.toString());
    } catch (error) {
      console.error("保存用户同意状态失败:", error);
    }
  }
}

// 主要的生态服务API类
export class EcoServicesAPI {
  private static instance: EcoServicesAPI;
  private performanceMonitor: PerformanceMonitor;
  private requestQueue: Map<string, Promise<any>> = new Map();

  private constructor() {
    this.performanceMonitor = PerformanceMonitor.getInstance();
  }

  static getInstance(): EcoServicesAPI {
    if (!EcoServicesAPI.instance) {
      EcoServicesAPI.instance = new EcoServicesAPI();
    }
    return EcoServicesAPI.instance;
  }

  // 防重复请求装饰器
  private async deduplicateRequest<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    if (this.requestQueue.has(key)) {
      return this.requestQueue.get(key);
    }

    const promise = requestFn();
    this.requestQueue.set(key, promise);

    try {
      const result = await promise;
      this.requestQueue.delete(key);
      return result;
    } catch (error) {
      this.requestQueue.delete(key);
      throw error;
    }
  }

  // 获取农产品列表
  async getFarmProducts(filters?: {
    category?: string;
    constitution?: string;
    season?: string;
    organic?: boolean;
    priceRange?: { min: number; max: number };
  }): Promise<FarmProduct[]> {
    const startTime = this.performanceMonitor.startTimer("getFarmProducts");
    const cacheKey = `farm_products_${JSON.stringify(filters || {})}`;

    try {
      return await this.deduplicateRequest(cacheKey, async () => {
        // 先尝试从缓存获取
        const cached = await apiCache.get(cacheKey);
        if (cached) {
          this.performanceMonitor.endTimer("getFarmProducts", startTime);
          return cached;
        }

        // 模拟API调用
        await new Promise<void>((resolve) => setTimeout(() => resolve(), 500));

        // 这里应该是真实的API调用
        const mockData = await this.getMockFarmProducts(filters);

        // 缓存结果（30分钟）
        await apiCache.set(cacheKey, mockData, 30 * 60 * 1000);

        this.performanceMonitor.endTimer("getFarmProducts", startTime);
        return mockData;
      });
    } catch (error) {
      this.performanceMonitor.endTimer("getFarmProducts", startTime);
      console.error("获取农产品失败:", error);
      throw error;
    }
  }

  // 获取山水养生目的地
  async getWellnessDestinations(filters?: {
    type?: string;
    location?: string;
    priceRange?: { min: number; max: number };
    constitution?: string;
  }): Promise<WellnessDestination[]> {
    const startTime = this.performanceMonitor.startTimer(
      "getWellnessDestinations"
    );
    const cacheKey = `wellness_destinations_${JSON.stringify(filters || {})}`;

    try {
      return await this.deduplicateRequest(cacheKey, async () => {
        const cached = await apiCache.get(cacheKey);
        if (cached) {
          this.performanceMonitor.endTimer(
            "getWellnessDestinations",
            startTime
          );
          return cached;
        }

        await new Promise<void>((resolve) => setTimeout(() => resolve(), 300));

        const mockData = await this.getMockWellnessDestinations(filters);

        // 缓存结果（1小时）
        await apiCache.set(cacheKey, mockData, 60 * 60 * 1000);

        this.performanceMonitor.endTimer("getWellnessDestinations", startTime);
        return mockData;
      });
    } catch (error) {
      this.performanceMonitor.endTimer("getWellnessDestinations", startTime);
      console.error("获取养生目的地失败:", error);
      throw error;
    }
  }

  // 获取个性化营养方案
  async getNutritionPlans(
    userPreferences: UserPreferences
  ): Promise<NutritionPlan[]> {
    const startTime = this.performanceMonitor.startTimer("getNutritionPlans");

    try {
      // 检查隐私同意
      const hasConsent = await PrivacyManager.getUserConsent(
        "nutrition_analysis"
      );
      if (!hasConsent) {
        throw new Error("需要用户同意才能进行营养分析");
      }

      // 匿名化敏感数据
      const anonymizedPreferences =
        PrivacyManager.anonymizeData(userPreferences);
      const cacheKey = `nutrition_plans_${CryptoJS.SHA256(
        JSON.stringify(anonymizedPreferences)
      ).toString()}`;

      return await this.deduplicateRequest(cacheKey, async () => {
        const cached = await apiCache.get(cacheKey);
        if (cached) {
          this.performanceMonitor.endTimer("getNutritionPlans", startTime);
          return cached;
        }

        await new Promise<void>((resolve) => setTimeout(() => resolve(), 800));

        const mockData = await this.getMockNutritionPlans(userPreferences);

        // 缓存结果（2小时）
        await apiCache.set(cacheKey, mockData, 2 * 60 * 60 * 1000);

        this.performanceMonitor.endTimer("getNutritionPlans", startTime);
        return mockData;
      });
    } catch (error) {
      this.performanceMonitor.endTimer("getNutritionPlans", startTime);
      console.error("获取营养方案失败:", error);
      throw error;
    }
  }

  // 验证区块链溯源
  async verifyBlockchainTrace(productId: string): Promise<boolean> {
    const startTime = this.performanceMonitor.startTimer(
      "verifyBlockchainTrace"
    );

    try {
      const cacheKey = `blockchain_verify_${productId}`;

      return await this.deduplicateRequest(cacheKey, async () => {
        const cached = await apiCache.get(cacheKey);
        if (cached !== null) {
          this.performanceMonitor.endTimer("verifyBlockchainTrace", startTime);
          return cached;
        }

        // 模拟区块链验证
        await new Promise<void>((resolve) => setTimeout(() => resolve(), 1000));

        const isValid = Math.random() > 0.1; // 90%的验证成功率

        // 缓存结果（24小时）
        await apiCache.set(cacheKey, isValid, 24 * 60 * 60 * 1000);

        this.performanceMonitor.endTimer("verifyBlockchainTrace", startTime);
        return isValid;
      });
    } catch (error) {
      this.performanceMonitor.endTimer("verifyBlockchainTrace", startTime);
      console.error("区块链验证失败:", error);
      return false;
    }
  }

  // 预订养生目的地
  async bookDestination(
    destinationId: string,
    bookingDetails: {
      dates: { start: string; end: string };
      guests: number;
      preferences: string[];
    }
  ): Promise<{ success: boolean; bookingId?: string; message: string }> {
    const startTime = this.performanceMonitor.startTimer("bookDestination");

    try {
      // 加密敏感预订信息
      const encryptedDetails = DataEncryption.encrypt(bookingDetails);

      // 模拟预订API调用
      await new Promise<void>((resolve) => setTimeout(() => resolve(), 1200));

      const success = Math.random() > 0.2; // 80%的预订成功率

      this.performanceMonitor.endTimer("bookDestination", startTime);

      if (success) {
        return {
          success: true,
          bookingId: `BK${Date.now()}`,
          message: "预订成功！我们会尽快联系您确认详细信息。",
        };
      } else {
        return {
          success: false,
          message: "预订失败，请稍后重试或联系客服。",
        };
      }
    } catch (error) {
      this.performanceMonitor.endTimer("bookDestination", startTime);
      console.error("预订失败:", error);
      return {
        success: false,
        message: "预订过程中发生错误，请稍后重试。",
      };
    }
  }

  // 获取性能指标
  getPerformanceMetrics(): Record<string, { average: number; count: number }> {
    return this.performanceMonitor.getMetrics();
  }

  // 清除缓存
  async clearCache(): Promise<void> {
    await apiCache.clear();
  }

  // 模拟数据方法
  private async getMockFarmProducts(filters?: any): Promise<FarmProduct[]> {
    // 这里返回模拟数据，实际应该调用真实API
    return [
      {
        id: "product_1",
        name: "有机枸杞",
        category: "中药材",
        origin: "宁夏中宁",
        healthBenefits: ["明目", "补肾", "抗氧化", "提高免疫力"],
        season: "秋季",
        price: 68,
        unit: "500g",
        image: "goji_berry.jpg",
        organic: true,
        stock: 156,
        rating: 4.8,
        reviews: 234,
        blockchain: {
          verified: true,
          traceability: [
            {
              timestamp: "2024-03-15 08:00",
              location: "宁夏中宁有机农场",
              action: "种植播种",
              verifier: "农业部认证机构",
              hash: "0x1a2b3c4d5e6f...",
            },
          ],
          certifications: ["有机认证", "GAP认证", "地理标志保护"],
        },
        tcmProperties: {
          nature: "平",
          flavor: "甘",
          meridian: ["肝经", "肾经"],
          functions: ["滋补肝肾", "明目润肺"],
          constitution: ["气虚质", "阴虚质", "阳虚质"],
        },
        aiRecommendation: {
          score: 95,
          reason: "根据您的气虚体质，枸杞能有效补气养血",
          personalizedBenefits: ["改善疲劳", "增强免疫", "护眼明目"],
        },
      },
      // 更多模拟数据...
    ];
  }

  private async getMockWellnessDestinations(
    filters?: any
  ): Promise<WellnessDestination[]> {
    // 模拟数据
    return [
      {
        id: "dest_1",
        name: "峨眉山养生谷",
        location: "四川峨眉山",
        type: "mountain",
        description: "集佛教文化、中医养生、自然疗法于一体的综合养生基地",
        healthFeatures: [
          "负氧离子丰富",
          "天然药材资源",
          "清净修心环境",
          "海拔适宜",
        ],
        activities: [
          "太极晨练",
          "药膳体验",
          "禅修静坐",
          "森林浴",
          "中医理疗",
          "药材采摘",
        ],
        rating: 4.8,
        price: 1280,
        image: "emei_mountain.jpg",
        tcmBenefits: ["清肺润燥", "宁心安神", "强身健体", "疏肝理气"],
        availability: {
          available: true,
          nextAvailable: "2024-12-20",
          capacity: 50,
          booked: 32,
        },
        weatherSuitability: {
          currentScore: 85,
          forecast: "晴朗，适宜养生",
          bestTime: "春秋两季",
        },
        personalizedScore: {
          score: 92,
          factors: ["适合气虚质", "海拔适宜", "空气质量优"],
          recommendations: ["建议停留3-5天", "参与太极和禅修", "尝试药膳调理"],
        },
      },
      // 更多模拟数据...
    ];
  }

  private async getMockNutritionPlans(
    userPreferences: UserPreferences
  ): Promise<NutritionPlan[]> {
    // 模拟数据
    return [
      {
        id: "plan_1",
        name: "气虚质春季调理餐",
        constitution: userPreferences.constitution,
        season: "春季",
        meals: {
          breakfast: ["小米粥配红枣", "蒸蛋羹", "枸杞茶", "核桃仁"],
          lunch: ["黄芪炖鸡汤", "山药炒木耳", "五谷饭", "时令蔬菜"],
          dinner: ["莲子银耳汤", "清蒸鲈鱼", "青菜豆腐", "薏米粥"],
          snacks: ["红枣桂圆茶", "坚果拼盘", "蜂蜜柠檬水"],
        },
        ingredients: [],
        benefits: ["补气健脾", "增强体质", "改善疲劳", "提升免疫"],
        nutritionFacts: {
          calories: 1850,
          protein: 85,
          carbs: 245,
          fat: 65,
          fiber: 35,
        },
        aiOptimized: true,
      },
      // 更多模拟数据...
    ];
  }
}

// 导出单例实例
export const ecoServicesAPI = EcoServicesAPI.getInstance();
export { PrivacyManager, DataEncryption, PerformanceMonitor };
