/**
 * 推荐引擎服务
 * 基于用户健康数据和行为提供个性化产品和服务推荐
 */

import { Product } from '../../types/business';

// 推荐引擎接口
export interface RecommendationEngine {
  generateRecommendations(customerData: any, limit: number): Promise<Product[]>;
  getPersonalizedRanking(customerId: string, productIds: string[]): Promise<string[]>;
  explainRecommendation(customerId: string, productId: string): Promise<string>;
  refreshRecommendations(customerId: string): Promise<void>;
}

// 推荐模型类型
export enum RecommendationModelType {
  COLLABORATIVE_FILTERING = 'collaborative_filtering',
  CONTENT_BASED = 'content_based',
  HYBRID = 'hybrid',
  TCM_KNOWLEDGE_BASED = 'tcm_knowledge_based'
}

// 推荐上下文
interface RecommendationContext {
  customerId: string;
  healthProfile: any;
  recentViews: string[];
  purchaseHistory: any[];
  preferredCategories: string[];
  seasonalFactors: any;
  tcmConstitution: string;
}

// 推荐引擎实现
export class RecommendationEngineImpl implements RecommendationEngine {
  private modelType: RecommendationModelType;
  private productService: any;
  private customerService: any;
  private tcmKnowledgeService: any;
  
  constructor(
    modelType: RecommendationModelType,
    productService: any,
    customerService: any,
    tcmKnowledgeService: any
  ) {
    this.modelType = modelType;
    this.productService = productService;
    this.customerService = customerService;
    this.tcmKnowledgeService = tcmKnowledgeService;
  }
  
  // 生成个性化推荐
  async generateRecommendations(customerData: any, limit: number = 5): Promise<Product[]> {
    try {
      // 构建推荐上下文
      const context = await this.buildRecommendationContext(customerData.id);
      
      // 根据模型类型选择推荐策略
      let recommendedProductIds: string[] = [];
      
      switch (this.modelType) {
        case RecommendationModelType.COLLABORATIVE_FILTERING:
          recommendedProductIds = await this.collaborativeFilteringRecommend(context, limit);
          break;
        case RecommendationModelType.CONTENT_BASED:
          recommendedProductIds = await this.contentBasedRecommend(context, limit);
          break;
        case RecommendationModelType.TCM_KNOWLEDGE_BASED:
          recommendedProductIds = await this.tcmKnowledgeBasedRecommend(context, limit);
          break;
        case RecommendationModelType.HYBRID:
        default:
          recommendedProductIds = await this.hybridRecommend(context, limit);
          break;
      }
      
      // 获取完整的产品信息
      const products = await Promise.all(
        recommendedProductIds.map(id => this.productService.getProductById(id))
      );
      
      return products.filter(p => p !== null);
    } catch (error) {
      console.error('Error generating recommendations:', error);
      return [];
    }
  }
  
  // 获取个性化排序
  async getPersonalizedRanking(customerId: string, productIds: string[]): Promise<string[]> {
    try {
      const context = await this.buildRecommendationContext(customerId);
      
      // 为每个产品计算相关性分数
      const scoredProducts = await Promise.all(
        productIds.map(async (productId) => {
          const score = await this.calculateRelevanceScore(productId, context);
          return { productId, score };
        })
      );
      
      // 按分数降序排序
      scoredProducts.sort((a, b) => b.score - a.score);
      
      // 返回排序后的产品ID
      return scoredProducts.map(item => item.productId);
    } catch (error) {
      console.error('Error ranking products:', error);
      return productIds; // 出错时返回原始顺序
    }
  }
  
  // 解释推荐原因
  async explainRecommendation(customerId: string, productId: string): Promise<string> {
    try {
      const context = await this.buildRecommendationContext(customerId);
      const product = await this.productService.getProductById(productId);
      
      if (!product) {
        return '无法找到该产品';
      }
      
      // 基于TCM体质的解释
      if (context.tcmConstitution && product.category === 'tcm_formula') {
        const tcmExplanation = await this.tcmKnowledgeService.getConstitutionProductMatch(
          context.tcmConstitution,
          productId
        );
        
        if (tcmExplanation) {
          return `根据您的${context.tcmConstitution}体质特点，${tcmExplanation}`;
        }
      }
      
      // 基于历史购买行为的解释
      const purchasedSimilar = context.purchaseHistory.some(
        purchase => this.productService.areSimilarProducts(purchase.productId, productId)
      );
      
      if (purchasedSimilar) {
        return `基于您之前购买的类似产品，我们认为这个产品也可能适合您`;
      }
      
      // 基于季节因素的解释
      if (context.seasonalFactors && product.tags.includes(context.seasonalFactors.currentSeason)) {
        return `这个产品特别适合${context.seasonalFactors.currentSeason}季节使用`;
      }
      
      // 默认解释
      return `根据您的健康档案和偏好，我们认为这个产品可能对您有益`;
    } catch (error) {
      console.error('Error explaining recommendation:', error);
      return '无法生成推荐解释';
    }
  }
  
  // 刷新用户推荐
  async refreshRecommendations(customerId: string): Promise<void> {
    try {
      // 获取最新的用户数据
      const customerData = await this.customerService.getCustomerById(customerId);
      
      // 生成新的推荐
      const recommendations = await this.generateRecommendations(customerData, 10);
      
      // 更新用户推荐缓存
      await this.customerService.updateRecommendations(customerId, recommendations);
    } catch (error) {
      console.error('Error refreshing recommendations:', error);
      throw new Error('刷新推荐失败');
    }
  }
  
  // 私有方法: 构建推荐上下文
  private async buildRecommendationContext(customerId: string): Promise<RecommendationContext> {
    const customer = await this.customerService.getCustomerById(customerId);
    const recentViews = await this.customerService.getRecentProductViews(customerId);
    const purchaseHistory = await this.customerService.getCustomerPurchases(customerId);
    const preferences = customer.preferences || {};
    
    // 获取季节因素
    const currentDate = new Date();
    const currentSeason = this.getSeasonFromDate(currentDate);
    
    return {
      customerId,
      healthProfile: customer.healthProfile,
      recentViews,
      purchaseHistory,
      preferredCategories: preferences.categories || [],
      seasonalFactors: {
        currentSeason,
        isHoliday: this.isHolidaySeason(currentDate)
      },
      tcmConstitution: customer.healthProfile?.tcmConstitution || ''
    };
  }
  
  // 私有方法: 基于协同过滤的推荐
  private async collaborativeFilteringRecommend(context: RecommendationContext, limit: number): Promise<string[]> {
    // 查找相似用户
    const similarUserIds = await this.customerService.findSimilarCustomers(context.customerId);
    
    // 获取相似用户的购买历史
    const similarUsersPurchases = await Promise.all(
      similarUserIds.map(userId => this.customerService.getCustomerPurchases(userId))
    );
    
    // 扁平化并统计产品出现频率
    const productFrequency: Record<string, number> = {};
    similarUsersPurchases.flat().forEach(purchase => {
      if (!context.purchaseHistory.some(p => p.productId === purchase.productId)) {
        productFrequency[purchase.productId] = (productFrequency[purchase.productId] || 0) + 1;
      }
    });
    
    // 排序并返回前N个产品
    return Object.entries(productFrequency)
      .sort((a, b) => b[1] - a[1])
      .map(([productId]) => productId)
      .slice(0, limit);
  }
  
  // 私有方法: 基于内容的推荐
  private async contentBasedRecommend(context: RecommendationContext, limit: number): Promise<string[]> {
    // 获取用户已购买产品的特征
    const purchasedProductIds = context.purchaseHistory.map(p => p.productId);
    const purchasedProducts = await Promise.all(
      purchasedProductIds.map(id => this.productService.getProductById(id))
    );
    
    // 提取用户偏好特征
    const preferredTags = this.extractPreferredTags(purchasedProducts);
    const preferredCategories = context.preferredCategories.length > 0 
      ? context.preferredCategories 
      : this.extractPreferredCategories(purchasedProducts);
    
    // 查找匹配产品
    const matchingProducts = await this.productService.findProductsByFeatures(
      preferredTags,
      preferredCategories,
      purchasedProductIds // 排除已购买的产品
    );
    
    return matchingProducts.slice(0, limit).map(p => p.id);
  }
  
  // 私有方法: 基于中医知识的推荐
  private async tcmKnowledgeBasedRecommend(context: RecommendationContext, limit: number): Promise<string[]> {
    if (!context.tcmConstitution) {
      // 如果没有中医体质信息，回退到内容推荐
      return this.contentBasedRecommend(context, limit);
    }
    
    // 基于体质获取适合的产品
    const suitableProducts = await this.tcmKnowledgeService.getSuitableProductsForConstitution(
      context.tcmConstitution,
      context.seasonalFactors.currentSeason
    );
    
    // 排除已购买的产品
    const purchasedProductIds = new Set(context.purchaseHistory.map(p => p.productId));
    const filteredProducts = suitableProducts.filter(p => !purchasedProductIds.has(p.id));
    
    return filteredProducts.slice(0, limit).map(p => p.id);
  }
  
  // 私有方法: 混合推荐策略
  private async hybridRecommend(context: RecommendationContext, limit: number): Promise<string[]> {
    // 从各种推荐方法获取结果
    const collaborativeResults = await this.collaborativeFilteringRecommend(context, Math.ceil(limit / 2));
    const contentResults = await this.contentBasedRecommend(context, Math.ceil(limit / 2));
    const tcmResults = await this.tcmKnowledgeBasedRecommend(context, Math.ceil(limit / 2));
    
    // 合并结果，避免重复
    const combinedResults: string[] = [];
    const seenProducts = new Set<string>();
    
    // 交替添加各种推荐结果
    const allResults = [collaborativeResults, tcmResults, contentResults];
    let index = 0;
    
    while (combinedResults.length < limit && allResults.some(arr => arr.length > 0)) {
      const currentArray = allResults[index % allResults.length];
      
      if (currentArray.length > 0) {
        const productId = currentArray.shift()!;
        
        if (!seenProducts.has(productId)) {
          combinedResults.push(productId);
          seenProducts.add(productId);
        }
      }
      
      index++;
    }
    
    return combinedResults;
  }
  
  // 私有方法: 计算产品相关性分数
  private async calculateRelevanceScore(productId: string, context: RecommendationContext): Promise<number> {
    const product = await this.productService.getProductById(productId);
    
    if (!product) {
      return 0;
    }
    
    let score = 0;
    
    // 基于中医体质匹配加分
    if (context.tcmConstitution && product.category === 'tcm_formula') {
      const matchScore = await this.tcmKnowledgeService.getConstitutionProductMatchScore(
        context.tcmConstitution,
        productId
      );
      score += matchScore * 2; // 权重加倍
    }
    
    // 基于类别偏好加分
    if (context.preferredCategories.includes(product.category)) {
      score += 1;
    }
    
    // 基于标签匹配加分
    const preferredTags = this.extractPreferredTags(
      await Promise.all(
        context.purchaseHistory.map(p => this.productService.getProductById(p.productId))
      )
    );
    
    const tagMatchCount = product.tags.filter(tag => preferredTags.includes(tag)).length;
    score += tagMatchCount * 0.5;
    
    // 基于季节匹配加分
    if (product.tags.includes(context.seasonalFactors.currentSeason)) {
      score += 1;
    }
    
    return score;
  }
  
  // 辅助方法: 从日期获取季节
  private getSeasonFromDate(date: Date): string {
    const month = date.getMonth();
    
    if (month >= 2 && month <= 4) return '春季';
    if (month >= 5 && month <= 7) return '夏季';
    if (month >= 8 && month <= 10) return '秋季';
    return '冬季';
  }
  
  // 辅助方法: 判断是否节假日季节
  private isHolidaySeason(date: Date): boolean {
    const month = date.getMonth();
    const day = date.getDate();
    
    // 简单判断几个主要节日
    if (month === 0 && day <= 5) return true; // 元旦
    if (month === 4 && day >= 1 && day <= 5) return true; // 五一
    if (month === 9 && day >= 1 && day <= 7) return true; // 国庆
    if (month === 11 && (day >= 20 && day <= 31)) return true; // 圣诞/元旦
    
    return false;
  }
  
  // 辅助方法: 提取偏好标签
  private extractPreferredTags(products: Product[]): string[] {
    const tagFrequency: Record<string, number> = {};
    
    products.forEach(product => {
      if (product && product.tags) {
        product.tags.forEach(tag => {
          tagFrequency[tag] = (tagFrequency[tag] || 0) + 1;
        });
      }
    });
    
    // 按频率排序并返回前10个标签
    return Object.entries(tagFrequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([tag]) => tag);
  }
  
  // 辅助方法: 提取偏好类别
  private extractPreferredCategories(products: Product[]): string[] {
    const categoryFrequency: Record<string, number> = {};
    
    products.forEach(product => {
      if (product && product.category) {
        categoryFrequency[product.category] = (categoryFrequency[product.category] || 0) + 1;
      }
    });
    
    // 按频率排序并返回类别
    return Object.entries(categoryFrequency)
      .sort((a, b) => b[1] - a[1])
      .map(([category]) => category);
  }
}

// 工厂函数
export function createRecommendationEngine(
  modelType: RecommendationModelType,
  productService: any,
  customerService: any,
  tcmKnowledgeService: any
): RecommendationEngine {
  return new RecommendationEngineImpl(
    modelType,
    productService,
    customerService,
    tcmKnowledgeService
  );
} 