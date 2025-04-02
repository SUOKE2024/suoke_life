import { logger } from '../../utils/logger';
import { getCache, setCache } from '../../core/cache';
import solarTermData from '../../data/solar-terms.json';

// 缓存配置
const SEASONAL_CACHE_TTL = 86400; // 24小时

/**
 * 二十四节气数据类型
 */
export interface SolarTerm {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  date: string; // ISO格式日期
  gregorianDate?: string; // 公历日期描述
  lunarDate?: string; // 农历日期描述
  healthTips: string[];
  dietaryRecommendations: string[];
  seasonalFoods: {
    name: string;
    benefits: string;
    category: string; // 蔬菜、水果、肉类等
    imageUrl?: string;
  }[];
  TCMPrinciples: string; // 中医养生原则
  activities: string[]; // 适宜活动
  avoidances: string[]; // 不宜事项
  relatedProducts?: string[]; // 关联产品ID
}

/**
 * 节气服务
 * 处理与中国传统二十四节气相关的功能
 */
export class SeasonalService {
  private solarTerms: SolarTerm[];
  
  constructor() {
    this.solarTerms = solarTermData as SolarTerm[];
  }
  
  /**
   * 获取当前节气信息
   */
  async getCurrentSolarTerm(): Promise<SolarTerm | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = 'current_solar_term';
      const cachedData = await getCache<SolarTerm>(cacheKey);
      
      if (cachedData) {
        logger.debug('从缓存获取当前节气信息');
        return cachedData;
      }
      
      const now = new Date();
      
      // 查找当前或最近的节气
      let currentTerm: SolarTerm | null = null;
      let closestFutureDiff = Infinity;
      let closestPastDiff = Infinity;
      let closestFutureTerm: SolarTerm | null = null;
      let closestPastTerm: SolarTerm | null = null;
      
      for (const term of this.solarTerms) {
        const termDate = new Date(term.date);
        const diff = termDate.getTime() - now.getTime();
        
        // 精确匹配当天（忽略时分秒）
        if (this.isSameDay(now, termDate)) {
          currentTerm = term;
          break;
        }
        
        // 记录最近的未来节气
        if (diff > 0 && diff < closestFutureDiff) {
          closestFutureDiff = diff;
          closestFutureTerm = term;
        }
        
        // 记录最近的过去节气
        if (diff <= 0 && Math.abs(diff) < closestPastDiff) {
          closestPastDiff = Math.abs(diff);
          closestPastTerm = term;
        }
      }
      
      // 如果没有当天节气，则使用最近的过去节气
      if (!currentTerm && closestPastTerm) {
        currentTerm = closestPastTerm;
      }
      
      // 如果仍然没有找到，使用最近的未来节气
      if (!currentTerm && closestFutureTerm) {
        currentTerm = closestFutureTerm;
      }
      
      if (currentTerm) {
        // 更新缓存
        await setCache(cacheKey, currentTerm, SEASONAL_CACHE_TTL);
      }
      
      return currentTerm;
    } catch (error) {
      logger.error('获取当前节气信息失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取指定日期的节气信息
   * @param date 日期字符串 (YYYY-MM-DD)
   */
  async getSolarTermByDate(date: string): Promise<SolarTerm | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `solar_term:${date}`;
      const cachedData = await getCache<SolarTerm>(cacheKey);
      
      if (cachedData) {
        logger.debug(`从缓存获取节气信息: ${date}`);
        return cachedData;
      }
      
      const targetDate = new Date(date);
      
      // 查找匹配的节气
      let matchedTerm: SolarTerm | null = null;
      let closestFutureDiff = Infinity;
      let closestPastDiff = Infinity;
      let closestFutureTerm: SolarTerm | null = null;
      let closestPastTerm: SolarTerm | null = null;
      
      for (const term of this.solarTerms) {
        const termDate = new Date(term.date);
        const diff = termDate.getTime() - targetDate.getTime();
        
        // 精确匹配当天（忽略时分秒）
        if (this.isSameDay(targetDate, termDate)) {
          matchedTerm = term;
          break;
        }
        
        // 记录最近的未来节气
        if (diff > 0 && diff < closestFutureDiff) {
          closestFutureDiff = diff;
          closestFutureTerm = term;
        }
        
        // 记录最近的过去节气
        if (diff <= 0 && Math.abs(diff) < closestPastDiff) {
          closestPastDiff = Math.abs(diff);
          closestPastTerm = term;
        }
      }
      
      // 如果没有精确匹配，则使用最近的过去节气
      if (!matchedTerm && closestPastTerm) {
        matchedTerm = closestPastTerm;
      }
      
      // 如果仍然没有找到，使用最近的未来节气
      if (!matchedTerm && closestFutureTerm) {
        matchedTerm = closestFutureTerm;
      }
      
      if (matchedTerm) {
        // 更新缓存
        await setCache(cacheKey, matchedTerm, SEASONAL_CACHE_TTL);
      }
      
      return matchedTerm;
    } catch (error) {
      logger.error(`获取日期节气信息失败: ${date}`, error);
      throw error;
    }
  }
  
  /**
   * 获取指定节气信息
   * @param termId 节气ID
   */
  async getSolarTermById(termId: string): Promise<SolarTerm | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `solar_term_id:${termId}`;
      const cachedData = await getCache<SolarTerm>(cacheKey);
      
      if (cachedData) {
        logger.debug(`从缓存获取节气信息: ${termId}`);
        return cachedData;
      }
      
      const term = this.solarTerms.find(t => t.id === termId);
      
      if (term) {
        // 更新缓存
        await setCache(cacheKey, term, SEASONAL_CACHE_TTL);
      }
      
      return term || null;
    } catch (error) {
      logger.error(`获取节气信息失败: ${termId}`, error);
      throw error;
    }
  }
  
  /**
   * 获取所有节气基础信息列表
   */
  async getAllSolarTerms(): Promise<Array<Pick<SolarTerm, 'id' | 'name' | 'nameEn' | 'date'>>> {
    try {
      // 尝试从缓存获取
      const cacheKey = 'all_solar_terms_list';
      const cachedData = await getCache<Array<Pick<SolarTerm, 'id' | 'name' | 'nameEn' | 'date'>>>(cacheKey);
      
      if (cachedData) {
        logger.debug('从缓存获取所有节气列表');
        return cachedData;
      }
      
      // 构建简化的节气列表
      const termsList = this.solarTerms.map(term => ({
        id: term.id,
        name: term.name,
        nameEn: term.nameEn,
        date: term.date
      }));
      
      // 按日期排序
      termsList.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      
      // 更新缓存
      await setCache(cacheKey, termsList, SEASONAL_CACHE_TTL);
      
      return termsList;
    } catch (error) {
      logger.error('获取所有节气列表失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取基于当前节气的饮食推荐
   */
  async getCurrentDietaryRecommendations(): Promise<{
    solarTerm: {
      id: string;
      name: string;
      date: string;
    };
    recommendations: string[];
    seasonalFoods: SolarTerm['seasonalFoods'];
  } | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = 'current_dietary_recommendations';
      const cachedData = await getCache<any>(cacheKey);
      
      if (cachedData) {
        logger.debug('从缓存获取当前节气饮食推荐');
        return cachedData;
      }
      
      const currentTerm = await this.getCurrentSolarTerm();
      
      if (!currentTerm) {
        return null;
      }
      
      const recommendations = {
        solarTerm: {
          id: currentTerm.id,
          name: currentTerm.name,
          date: currentTerm.date
        },
        recommendations: currentTerm.dietaryRecommendations,
        seasonalFoods: currentTerm.seasonalFoods
      };
      
      // 更新缓存
      await setCache(cacheKey, recommendations, SEASONAL_CACHE_TTL);
      
      return recommendations;
    } catch (error) {
      logger.error('获取当前节气饮食推荐失败:', error);
      throw error;
    }
  }

  /**
   * 获取基于当前节气的健康建议
   */
  async getCurrentHealthTips(): Promise<{
    solarTerm: {
      id: string;
      name: string;
      date: string;
    };
    healthTips: string[];
    TCMPrinciples: string;
    activities: string[];
    avoidances: string[];
  } | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = 'current_health_tips';
      const cachedData = await getCache<any>(cacheKey);
      
      if (cachedData) {
        logger.debug('从缓存获取当前节气健康建议');
        return cachedData;
      }
      
      const currentTerm = await this.getCurrentSolarTerm();
      
      if (!currentTerm) {
        return null;
      }
      
      const healthTips = {
        solarTerm: {
          id: currentTerm.id,
          name: currentTerm.name,
          date: currentTerm.date
        },
        healthTips: currentTerm.healthTips,
        TCMPrinciples: currentTerm.TCMPrinciples,
        activities: currentTerm.activities,
        avoidances: currentTerm.avoidances
      };
      
      // 更新缓存
      await setCache(cacheKey, healthTips, SEASONAL_CACHE_TTL);
      
      return healthTips;
    } catch (error) {
      logger.error('获取当前节气健康建议失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取下一个节气信息
   */
  async getNextSolarTerm(): Promise<SolarTerm | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = 'next_solar_term';
      const cachedData = await getCache<SolarTerm>(cacheKey);
      
      if (cachedData) {
        logger.debug('从缓存获取下一个节气信息');
        return cachedData;
      }
      
      const now = new Date();
      
      // 查找下一个节气
      let nextTerm: SolarTerm | null = null;
      let closestFutureDiff = Infinity;
      
      for (const term of this.solarTerms) {
        const termDate = new Date(term.date);
        const diff = termDate.getTime() - now.getTime();
        
        // 找到未来最近的节气
        if (diff > 0 && diff < closestFutureDiff) {
          closestFutureDiff = diff;
          nextTerm = term;
        }
      }
      
      if (nextTerm) {
        // 更新缓存
        await setCache(cacheKey, nextTerm, SEASONAL_CACHE_TTL);
      }
      
      return nextTerm;
    } catch (error) {
      logger.error('获取下一个节气信息失败:', error);
      throw error;
    }
  }
  
  /**
   * 判断两个日期是否为同一天（忽略时分秒）
   */
  private isSameDay(date1: Date, date2: Date): boolean {
    return (
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate()
    );
  }
}

export default new SeasonalService(); 