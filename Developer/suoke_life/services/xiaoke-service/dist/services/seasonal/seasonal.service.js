"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SeasonalService = void 0;
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const solar_terms_json_1 = __importDefault(require("../../data/solar-terms.json"));
// 缓存配置
const SEASONAL_CACHE_TTL = 86400; // 24小时
/**
 * 节气服务
 * 处理与中国传统二十四节气相关的功能
 */
class SeasonalService {
    constructor() {
        this.solarTerms = solar_terms_json_1.default;
    }
    /**
     * 获取当前节气信息
     */
    async getCurrentSolarTerm() {
        try {
            // 尝试从缓存获取
            const cacheKey = 'current_solar_term';
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取当前节气信息');
                return cachedData;
            }
            const now = new Date();
            // 查找当前或最近的节气
            let currentTerm = null;
            let closestFutureDiff = Infinity;
            let closestPastDiff = Infinity;
            let closestFutureTerm = null;
            let closestPastTerm = null;
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
                await (0, cache_1.setCache)(cacheKey, currentTerm, SEASONAL_CACHE_TTL);
            }
            return currentTerm;
        }
        catch (error) {
            logger_1.logger.error('获取当前节气信息失败:', error);
            throw error;
        }
    }
    /**
     * 获取指定日期的节气信息
     * @param date 日期字符串 (YYYY-MM-DD)
     */
    async getSolarTermByDate(date) {
        try {
            // 尝试从缓存获取
            const cacheKey = `solar_term:${date}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取节气信息: ${date}`);
                return cachedData;
            }
            const targetDate = new Date(date);
            // 查找匹配的节气
            let matchedTerm = null;
            let closestFutureDiff = Infinity;
            let closestPastDiff = Infinity;
            let closestFutureTerm = null;
            let closestPastTerm = null;
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
                await (0, cache_1.setCache)(cacheKey, matchedTerm, SEASONAL_CACHE_TTL);
            }
            return matchedTerm;
        }
        catch (error) {
            logger_1.logger.error(`获取日期节气信息失败: ${date}`, error);
            throw error;
        }
    }
    /**
     * 获取指定节气信息
     * @param termId 节气ID
     */
    async getSolarTermById(termId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `solar_term_id:${termId}`;
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug(`从缓存获取节气信息: ${termId}`);
                return cachedData;
            }
            const term = this.solarTerms.find(t => t.id === termId);
            if (term) {
                // 更新缓存
                await (0, cache_1.setCache)(cacheKey, term, SEASONAL_CACHE_TTL);
            }
            return term || null;
        }
        catch (error) {
            logger_1.logger.error(`获取节气信息失败: ${termId}`, error);
            throw error;
        }
    }
    /**
     * 获取所有节气基础信息列表
     */
    async getAllSolarTerms() {
        try {
            // 尝试从缓存获取
            const cacheKey = 'all_solar_terms_list';
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取所有节气列表');
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
            await (0, cache_1.setCache)(cacheKey, termsList, SEASONAL_CACHE_TTL);
            return termsList;
        }
        catch (error) {
            logger_1.logger.error('获取所有节气列表失败:', error);
            throw error;
        }
    }
    /**
     * 获取基于当前节气的饮食推荐
     */
    async getCurrentDietaryRecommendations() {
        try {
            // 尝试从缓存获取
            const cacheKey = 'current_dietary_recommendations';
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取当前节气饮食推荐');
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
            await (0, cache_1.setCache)(cacheKey, recommendations, SEASONAL_CACHE_TTL);
            return recommendations;
        }
        catch (error) {
            logger_1.logger.error('获取当前节气饮食推荐失败:', error);
            throw error;
        }
    }
    /**
     * 获取基于当前节气的健康建议
     */
    async getCurrentHealthTips() {
        try {
            // 尝试从缓存获取
            const cacheKey = 'current_health_tips';
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取当前节气健康建议');
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
            await (0, cache_1.setCache)(cacheKey, healthTips, SEASONAL_CACHE_TTL);
            return healthTips;
        }
        catch (error) {
            logger_1.logger.error('获取当前节气健康建议失败:', error);
            throw error;
        }
    }
    /**
     * 获取下一个节气信息
     */
    async getNextSolarTerm() {
        try {
            // 尝试从缓存获取
            const cacheKey = 'next_solar_term';
            const cachedData = await (0, cache_1.getCache)(cacheKey);
            if (cachedData) {
                logger_1.logger.debug('从缓存获取下一个节气信息');
                return cachedData;
            }
            const now = new Date();
            // 查找下一个节气
            let nextTerm = null;
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
                await (0, cache_1.setCache)(cacheKey, nextTerm, SEASONAL_CACHE_TTL);
            }
            return nextTerm;
        }
        catch (error) {
            logger_1.logger.error('获取下一个节气信息失败:', error);
            throw error;
        }
    }
    /**
     * 判断两个日期是否为同一天（忽略时分秒）
     */
    isSameDay(date1, date2) {
        return (date1.getFullYear() === date2.getFullYear() &&
            date1.getMonth() === date2.getMonth() &&
            date1.getDate() === date2.getDate());
    }
}
exports.SeasonalService = SeasonalService;
exports.default = new SeasonalService();
