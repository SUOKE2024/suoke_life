"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecommendationService = void 0;
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const seasonal_service_1 = __importDefault(require("../seasonal/seasonal.service"));
const product_model_1 = require("../../models/product.model");
const activity_model_1 = require("../../models/activity.model");
const user_profile_model_1 = require("../../models/user-profile.model");
const container_1 = require("../../core/container");
const product_repository_1 = require("../../repositories/product.repository");
// 缓存配置
const RECOMMENDATION_CACHE_TTL = 3600; // 1小时
/**
 * 推荐服务
 * 提供基于用户画像和节气的产品和活动推荐功能
 */
class RecommendationService {
    constructor() {
        this.logger = logger_1.logger;
        this.cacheService = cache_1.getCache;
        this.productRepository = container_1.container.resolve(product_repository_1.ProductRepository);
        // ... existing code ...
    }
    /**
     * 获取基于用户画像的产品推荐
     * @param userId 用户ID
     * @param limit 限制返回数量
     */
    async getPersonalizedProductRecommendations(userId, limit = 10) {
        try {
            // 尝试从缓存获取
            const cacheKey = `personalized_products:${userId}:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取个性化产品推荐: ${userId}`);
                return cachedData;
            }
            // 获取用户画像
            const userProfile = await user_profile_model_1.UserProfileModel.findOne({ userId }).lean();
            if (!userProfile) {
                logger_1.logger.warn(`用户画像不存在: ${userId}`);
                // 如果用户画像不存在，返回热门产品推荐
                return this.getPopularProducts(limit);
            }
            // 根据用户体质、偏好和健康状况构建查询条件
            const query = {};
            // 基于体质的推荐
            if (userProfile.constitution && userProfile.constitution.type) {
                query.$or = [
                    { 'suitableConstitutions': userProfile.constitution.type },
                    { 'suitableConstitutions': 'all' }
                ];
            }
            // 基于用户偏好的推荐
            if (userProfile.preferences && userProfile.preferences.dietaryPreferences && userProfile.preferences.dietaryPreferences.length > 0) {
                query.tags = { $in: userProfile.preferences.dietaryPreferences };
            }
            // 基于健康状况的推荐
            if (userProfile.healthConditions && userProfile.healthConditions.length > 0) {
                query.healthBenefits = { $in: userProfile.healthConditions };
            }
            // 获取符合条件的产品
            let recommendedProducts = await product_model_1.ProductModel.find(query)
                .sort({ rating: -1 })
                .limit(limit * 2) // 获取更多产品，以便后续过滤
                .lean();
            // 如果推荐不足，补充热门产品
            if (recommendedProducts.length < limit) {
                const popularProducts = await this.getPopularProducts(limit - recommendedProducts.length);
                const existingIds = new Set(recommendedProducts.map(p => p._id.toString()));
                // 添加不重复的热门产品
                for (const product of popularProducts) {
                    if (!existingIds.has(product._id.toString())) {
                        recommendedProducts.push(product);
                        if (recommendedProducts.length >= limit)
                            break;
                    }
                }
            }
            // 截取指定数量的推荐
            recommendedProducts = recommendedProducts.slice(0, limit);
            // 添加推荐原因
            recommendedProducts = recommendedProducts.map(product => {
                const reasons = [];
                // 添加推荐理由
                if (userProfile.constitution && product.suitableConstitutions &&
                    (product.suitableConstitutions.includes(userProfile.constitution.type) ||
                        product.suitableConstitutions.includes('all'))) {
                    reasons.push(`适合${userProfile.constitution.type}体质`);
                }
                if (userProfile.preferences && userProfile.preferences.dietaryPreferences &&
                    product.tags && product.tags.some(tag => userProfile.preferences.dietaryPreferences.includes(tag))) {
                    reasons.push('符合您的饮食偏好');
                }
                if (userProfile.healthConditions && product.healthBenefits &&
                    product.healthBenefits.some(benefit => userProfile.healthConditions.includes(benefit))) {
                    reasons.push('有益于您的健康状况');
                }
                if (reasons.length === 0) {
                    reasons.push('热门推荐');
                }
                return {
                    ...product,
                    recommendationReasons: reasons
                };
            });
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, recommendedProducts, RECOMMENDATION_CACHE_TTL);
            return recommendedProducts;
        }
        catch (error) {
            logger_1.logger.error('获取个性化产品推荐失败:', error);
            throw error;
        }
    }
    /**
     * 获取热门产品
     * @param limit 限制返回数量
     */
    async getPopularProducts(limit = 10) {
        try {
            // 尝试从缓存获取
            const cacheKey = `popular_products:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取热门产品');
                return cachedData;
            }
            // 获取热门产品
            const popularProducts = await product_model_1.ProductModel.find({
                isAvailable: true,
                stock: { $gt: 0 }
            })
                .sort({
                salesCount: -1,
                rating: -1
            })
                .limit(limit)
                .lean();
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, popularProducts, RECOMMENDATION_CACHE_TTL);
            return popularProducts;
        }
        catch (error) {
            logger_1.logger.error('获取热门产品失败:', error);
            throw error;
        }
    }
    /**
     * 获取基于节气的产品推荐
     * @param limit 限制返回数量
     */
    async getSeasonalProductRecommendations(limit = 10) {
        try {
            // 尝试从缓存获取
            const cacheKey = `seasonal_products:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取节气产品推荐');
                return cachedData;
            }
            // 获取当前节气
            const currentSolarTerm = await seasonal_service_1.default.getCurrentSolarTerm();
            if (!currentSolarTerm) {
                logger_1.logger.warn('当前节气信息不可用');
                return {
                    solarTerm: null,
                    products: await this.getPopularProducts(limit)
                };
            }
            // 构建查询条件
            const query = {
                isAvailable: true,
                stock: { $gt: 0 }
            };
            // 基于节气标签查询
            query.$or = [
                { solarTerms: currentSolarTerm.id },
                { solarTerms: 'all' }
            ];
            // 使用节气中的季节性食物名称查询相关产品
            if (currentSolarTerm.seasonalFoods && currentSolarTerm.seasonalFoods.length > 0) {
                const foodNames = currentSolarTerm.seasonalFoods.map(food => food.name);
                query.$or.push({ tags: { $in: foodNames } });
            }
            // 获取符合条件的产品
            let seasonalProducts = await product_model_1.ProductModel.find(query)
                .sort({ rating: -1 })
                .limit(limit)
                .lean();
            // 如果节气推荐不足，补充热门产品
            if (seasonalProducts.length < limit) {
                const popularProducts = await this.getPopularProducts(limit - seasonalProducts.length);
                const existingIds = new Set(seasonalProducts.map(p => p._id.toString()));
                // 添加不重复的热门产品
                for (const product of popularProducts) {
                    if (!existingIds.has(product._id.toString())) {
                        seasonalProducts.push(product);
                        if (seasonalProducts.length >= limit)
                            break;
                    }
                }
            }
            // 添加推荐原因
            seasonalProducts = seasonalProducts.map(product => {
                const reasons = [];
                if (product.solarTerms && (product.solarTerms.includes(currentSolarTerm.id) || product.solarTerms.includes('all'))) {
                    reasons.push(`适合${currentSolarTerm.name}节气`);
                }
                if (currentSolarTerm.seasonalFoods && product.tags) {
                    const matchedFoods = currentSolarTerm.seasonalFoods
                        .filter(food => product.tags.includes(food.name))
                        .map(food => food.name);
                    if (matchedFoods.length > 0) {
                        reasons.push(`含有节气食材: ${matchedFoods.join(', ')}`);
                    }
                }
                if (reasons.length === 0) {
                    reasons.push('热门推荐');
                }
                return {
                    ...product,
                    recommendationReasons: reasons
                };
            });
            const result = {
                solarTerm: {
                    id: currentSolarTerm.id,
                    name: currentSolarTerm.name,
                    date: currentSolarTerm.date,
                    description: currentSolarTerm.description
                },
                products: seasonalProducts
            };
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, result, RECOMMENDATION_CACHE_TTL);
            return result;
        }
        catch (error) {
            logger_1.logger.error('获取节气产品推荐失败:', error);
            throw error;
        }
    }
    /**
     * 获取基于用户画像的活动推荐
     * @param userId 用户ID
     * @param limit 限制返回数量
     */
    async getPersonalizedActivityRecommendations(userId, limit = 5) {
        try {
            // 尝试从缓存获取
            const cacheKey = `personalized_activities:${userId}:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取个性化活动推荐: ${userId}`);
                return cachedData;
            }
            // 获取用户画像
            const userProfile = await user_profile_model_1.UserProfileModel.findOne({ userId }).lean();
            if (!userProfile) {
                logger_1.logger.warn(`用户画像不存在: ${userId}`);
                // 如果用户画像不存在，返回热门活动推荐
                return this.getPopularActivities(limit);
            }
            // 根据用户偏好和活动历史构建查询条件
            const query = {
                status: 'active',
                startDate: { $gt: new Date() } // 未开始的活动
            };
            // 基于用户兴趣爱好的推荐
            if (userProfile.preferences && userProfile.preferences.activityInterests && userProfile.preferences.activityInterests.length > 0) {
                query.activityType = { $in: userProfile.preferences.activityInterests };
            }
            // 基于用户位置的推荐（如果有）
            if (userProfile.location && userProfile.location.city) {
                query.$or = [
                    { 'location.city': userProfile.location.city },
                    { 'location.province': userProfile.location.province },
                    { isOnline: true } // 线上活动也可以推荐
                ];
            }
            // 获取已参加的活动ID，避免重复推荐
            const participatedActivities = userProfile.activityHistory ?
                userProfile.activityHistory.map(h => h.activityId) : [];
            if (participatedActivities.length > 0) {
                query._id = { $nin: participatedActivities };
            }
            // 获取符合条件的活动
            let recommendedActivities = await activity_model_1.FarmActivityModel.find(query)
                .sort({
                startDate: 1, // 优先推荐即将开始的活动
                popularity: -1
            })
                .limit(limit * 2) // 获取更多活动，以便后续过滤
                .lean();
            // 如果推荐不足，补充热门活动
            if (recommendedActivities.length < limit) {
                const popularActivities = await this.getPopularActivities(limit - recommendedActivities.length);
                const existingIds = new Set(recommendedActivities.map(a => a._id.toString()));
                // 添加不重复的热门活动
                for (const activity of popularActivities) {
                    if (!existingIds.has(activity._id.toString()) &&
                        !participatedActivities.includes(activity._id.toString())) {
                        recommendedActivities.push(activity);
                        if (recommendedActivities.length >= limit)
                            break;
                    }
                }
            }
            // 截取指定数量的推荐
            recommendedActivities = recommendedActivities.slice(0, limit);
            // 添加推荐原因
            recommendedActivities = recommendedActivities.map(activity => {
                const reasons = [];
                // 添加推荐理由
                if (userProfile.preferences && userProfile.preferences.activityInterests &&
                    activity.activityType &&
                    userProfile.preferences.activityInterests.includes(activity.activityType)) {
                    reasons.push(`符合您对${activity.activityType}的兴趣`);
                }
                if (userProfile.location && activity.location &&
                    (userProfile.location.city === activity.location.city ||
                        userProfile.location.province === activity.location.province)) {
                    reasons.push(`在您所在的${activity.location.city || activity.location.province}`);
                }
                if (activity.isOnline) {
                    reasons.push('线上活动，随时可参与');
                }
                if (reasons.length === 0) {
                    reasons.push('热门活动');
                }
                return {
                    ...activity,
                    recommendationReasons: reasons,
                    daysToStart: this.calculateDaysToStart(activity.startDate)
                };
            });
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, recommendedActivities, RECOMMENDATION_CACHE_TTL);
            return recommendedActivities;
        }
        catch (error) {
            logger_1.logger.error('获取个性化活动推荐失败:', error);
            throw error;
        }
    }
    /**
     * 获取热门活动
     * @param limit 限制返回数量
     */
    async getPopularActivities(limit = 5) {
        try {
            // 尝试从缓存获取
            const cacheKey = `popular_activities:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取热门活动');
                return cachedData;
            }
            // 获取热门活动
            const popularActivities = await activity_model_1.FarmActivityModel.find({
                status: 'active',
                startDate: { $gt: new Date() } // 未开始的活动
            })
                .sort({
                popularity: -1,
                startDate: 1 // 优先推荐即将开始的活动
            })
                .limit(limit)
                .lean();
            // 添加距离开始还有多少天
            const activitiesWithDays = popularActivities.map(activity => ({
                ...activity,
                daysToStart: this.calculateDaysToStart(activity.startDate)
            }));
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, activitiesWithDays, RECOMMENDATION_CACHE_TTL);
            return activitiesWithDays;
        }
        catch (error) {
            logger_1.logger.error('获取热门活动失败:', error);
            throw error;
        }
    }
    /**
     * 获取基于节气的活动推荐
     * @param limit 限制返回数量
     */
    async getSeasonalActivityRecommendations(limit = 5) {
        try {
            // 尝试从缓存获取
            const cacheKey = `seasonal_activities:${limit}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取节气活动推荐');
                return cachedData;
            }
            // 获取当前节气
            const currentSolarTerm = await seasonal_service_1.default.getCurrentSolarTerm();
            if (!currentSolarTerm) {
                logger_1.logger.warn('当前节气信息不可用');
                return {
                    solarTerm: null,
                    activities: await this.getPopularActivities(limit)
                };
            }
            // 构建查询条件
            const query = {
                status: 'active',
                startDate: { $gt: new Date() } // 未开始的活动
            };
            // 基于节气标签查询
            query.$or = [
                { solarTerms: currentSolarTerm.id },
                { tags: { $in: [currentSolarTerm.id, currentSolarTerm.name] } }
            ];
            // 使用节气推荐的活动类型
            if (currentSolarTerm.activities && currentSolarTerm.activities.length > 0) {
                // 从节气推荐活动中提取活动类型
                const activityTypes = currentSolarTerm.activities
                    .map(activity => {
                    // 从活动描述中提取活动类型
                    const types = ['采摘', '种植', '烹饪', '手工', '健身', '冥想', '徒步', '野营'];
                    for (const type of types) {
                        if (activity.includes(type)) {
                            return type;
                        }
                    }
                    return null;
                })
                    .filter(type => type !== null);
                if (activityTypes.length > 0) {
                    query.$or.push({ activityType: { $in: activityTypes } });
                }
            }
            // 获取符合条件的活动
            let seasonalActivities = await activity_model_1.FarmActivityModel.find(query)
                .sort({
                startDate: 1, // 优先推荐即将开始的活动
                popularity: -1
            })
                .limit(limit)
                .lean();
            // 如果节气推荐不足，补充热门活动
            if (seasonalActivities.length < limit) {
                const popularActivities = await this.getPopularActivities(limit - seasonalActivities.length);
                const existingIds = new Set(seasonalActivities.map(a => a._id.toString()));
                // 添加不重复的热门活动
                for (const activity of popularActivities) {
                    if (!existingIds.has(activity._id.toString())) {
                        seasonalActivities.push(activity);
                        if (seasonalActivities.length >= limit)
                            break;
                    }
                }
            }
            // 添加推荐原因和距离开始天数
            seasonalActivities = seasonalActivities.map(activity => {
                const reasons = [];
                if ((activity.solarTerms && activity.solarTerms.includes(currentSolarTerm.id)) ||
                    (activity.tags && (activity.tags.includes(currentSolarTerm.id) || activity.tags.includes(currentSolarTerm.name)))) {
                    reasons.push(`适合${currentSolarTerm.name}节气`);
                }
                // 检查活动类型是否匹配节气推荐活动
                if (currentSolarTerm.activities && activity.activityType) {
                    const matchedActivity = currentSolarTerm.activities.find(a => a.includes(activity.activityType));
                    if (matchedActivity) {
                        reasons.push(`节气推荐活动: ${activity.activityType}`);
                    }
                }
                if (reasons.length === 0) {
                    reasons.push('热门推荐');
                }
                return {
                    ...activity,
                    recommendationReasons: reasons,
                    daysToStart: this.calculateDaysToStart(activity.startDate)
                };
            });
            const result = {
                solarTerm: {
                    id: currentSolarTerm.id,
                    name: currentSolarTerm.name,
                    date: currentSolarTerm.date,
                    description: currentSolarTerm.description,
                    recommendedActivities: currentSolarTerm.activities
                },
                activities: seasonalActivities
            };
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, result, RECOMMENDATION_CACHE_TTL);
            return result;
        }
        catch (error) {
            logger_1.logger.error('获取节气活动推荐失败:', error);
            throw error;
        }
    }
    /**
     * 计算距离活动开始还有多少天
     * @param startDate 活动开始日期
     */
    calculateDaysToStart(startDate) {
        const now = new Date();
        const start = new Date(startDate);
        const diffTime = start.getTime() - now.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays > 0 ? diffDays : 0;
    }
    /**
     * 基于健康知识获取产品推荐
     * @param userProfile 用户档案
     * @param healthConcepts 健康概念数组
     * @param limit 返回数量限制
     * @returns 产品推荐列表
     */
    async getHealthOrientedProductRecommendations(userProfile, healthConcepts, limit = 10) {
        // 缓存键
        const cacheKey = `health_products_${JSON.stringify(userProfile.id)}_${healthConcepts.join('_')}`;
        // 尝试获取缓存
        const cachedRecommendations = await this.cacheService.get(cacheKey);
        if (cachedRecommendations) {
            this.logger.debug(`使用缓存的健康产品推荐: ${cacheKey}`);
            return cachedRecommendations;
        }
        try {
            this.logger.debug(`获取健康导向产品推荐: ${JSON.stringify(healthConcepts)}`);
            const knowledgeGraphService = container_1.container.resolve('knowledgeGraphService');
            const knowledgeIntegrationService = container_1.container.resolve('knowledgeIntegrationService');
            // 查询健康概念相关产品
            const healthRelatedProductIds = [];
            // 从知识图谱服务查询健康概念关联的产品
            for (const concept of healthConcepts) {
                try {
                    const conceptNodes = await knowledgeGraphService.searchNodes(concept);
                    if (conceptNodes.length > 0) {
                        const conceptNode = conceptNodes[0];
                        const query = `
              MATCH (c {id: '${conceptNode.id}'})-[r*1..2]-(p:Product)
              RETURN p.id as productId, p.name as productName
              LIMIT 20
            `;
                        const result = await knowledgeGraphService.query(query);
                        // 收集产品ID
                        const productIds = result.map((item) => item.productId);
                        healthRelatedProductIds.push(...productIds);
                    }
                }
                catch (error) {
                    this.logger.error(`获取概念相关产品失败: ${concept}`, error);
                }
            }
            // 如果没有通过知识图谱找到产品，使用用户体质进行查询
            if (healthRelatedProductIds.length === 0 && userProfile.constitution) {
                const constitutionQuery = `
          MATCH (c:Constitution {name: '${userProfile.constitution}'})-[r:SUITABLE_FOR]-(p:Product)
          RETURN p.id as productId
          LIMIT 15
        `;
                try {
                    const result = await knowledgeGraphService.query(constitutionQuery);
                    const productIds = result.map((item) => item.productId);
                    healthRelatedProductIds.push(...productIds);
                }
                catch (error) {
                    this.logger.error(`获取体质相关产品失败: ${userProfile.constitution}`, error);
                }
            }
            // 去重
            const uniqueProductIds = [...new Set(healthRelatedProductIds)];
            // 查询产品详细信息
            const products = [];
            for (const productId of uniqueProductIds) {
                try {
                    // 通过知识整合服务获取产品知识增强信息
                    const productEnrichment = await knowledgeIntegrationService.enrichProductKnowledge(productId);
                    // 获取产品基本信息
                    const product = await this.productRepository.findById(productId);
                    if (product) {
                        // 合并产品基本信息和知识增强信息
                        products.push({
                            ...product,
                            healthBenefits: productEnrichment.healthBenefits || [],
                            suitableConstitutions: productEnrichment.constitutionFit?.suitable || [],
                            unsuitableConstitutions: productEnrichment.constitutionFit?.unsuitable || [],
                            seasonalInfo: productEnrichment.seasonalRelevance || {},
                            knowledgeItems: productEnrichment.knowledgeItems?.slice(0, 3) || []
                        });
                    }
                }
                catch (error) {
                    this.logger.error(`获取产品信息失败: ${productId}`, error);
                }
            }
            // 如果产品不足，补充常规推荐
            if (products.length < limit) {
                const regularRecommendations = await this.getPersonalizedProductRecommendations(userProfile, limit - products.length);
                products.push(...regularRecommendations);
            }
            // 从结果中移除重复产品并截取指定数量
            const uniqueProducts = this.removeDuplicates(products, 'id').slice(0, limit);
            // 缓存结果
            await this.cacheService.set(cacheKey, uniqueProducts, RECOMMENDATION_CACHE_TTL);
            return uniqueProducts;
        }
        catch (error) {
            this.logger.error('获取健康产品推荐失败', error);
            // 如果出错，返回个性化推荐作为备选
            return await this.getPersonalizedProductRecommendations(userProfile, limit);
        }
    }
    /**
     * 获取节气相关产品推荐
     * @param solarTerm 节气名称
     * @param userProfile 用户档案
     * @param limit 返回数量限制
     * @returns 节气相关产品推荐
     */
    async getSolarTermProductRecommendations(solarTerm, userProfile, limit = 10) {
        // 缓存键
        const cacheKey = `solar_term_products_${solarTerm}_${userProfile.id}`;
        // 尝试获取缓存
        const cachedRecommendations = await this.cacheService.get(cacheKey);
        if (cachedRecommendations) {
            this.logger.debug(`使用缓存的节气产品推荐: ${cacheKey}`);
            return cachedRecommendations;
        }
        try {
            this.logger.debug(`获取节气产品推荐: ${solarTerm}`);
            const knowledgeIntegrationService = container_1.container.resolve('knowledgeIntegrationService');
            // 获取节气相关农产品知识
            const solarTermData = await knowledgeIntegrationService.getSolarTermAgricultureKnowledge(solarTerm);
            // 获取产品详细信息
            const products = [];
            for (const productName of solarTermData.products) {
                try {
                    // 查找产品
                    const productResult = await this.productRepository.findByName(productName);
                    if (productResult && productResult.length > 0) {
                        // 添加产品信息
                        products.push({
                            ...productResult[0],
                            solarTerm: solarTerm,
                            seasonalRelevance: true,
                            knowledgeItems: solarTermData.knowledgeItems
                                .filter(item => item.content.includes(productName))
                                .slice(0, 2)
                        });
                    }
                }
                catch (error) {
                    this.logger.error(`获取节气相关产品信息失败: ${productName}`, error);
                }
            }
            // 如果产品不足，补充季节性推荐
            if (products.length < limit) {
                const seasonalRecommendations = await this.getSeasonalProductRecommendations(limit - products.length);
                products.push(...seasonalRecommendations);
            }
            // 从结果中移除重复产品并截取指定数量
            const uniqueProducts = this.removeDuplicates(products, 'id').slice(0, limit);
            // 缓存结果
            await this.cacheService.set(cacheKey, uniqueProducts, RECOMMENDATION_CACHE_TTL);
            return uniqueProducts;
        }
        catch (error) {
            this.logger.error(`获取节气产品推荐失败: ${solarTerm}`, error);
            // 如果出错，返回季节性推荐作为备选
            return await this.getSeasonalProductRecommendations(limit);
        }
    }
}
exports.RecommendationService = RecommendationService;
exports.default = new RecommendationService();
