"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ActivityService = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const activity_model_1 = require("../../models/activity.model");
const metrics_1 = require("../../core/metrics");
// 缓存配置
const ACTIVITY_CACHE_TTL = parseInt(process.env.ACTIVITY_CACHE_TTL || '3600', 10); // 默认1小时
/**
 * 活动服务类
 * 负责管理农事活动信息、预约和评价
 */
class ActivityService {
    /**
     * 获取活动列表
     */
    async getActivities(options) {
        try {
            const { category, query, location, startDate, endDate, sort = 'startDate_asc', limit = 20, skip = 0 } = options;
            // 构建查询条件
            const filter = {};
            if (category) {
                filter.category = category;
            }
            if (query) {
                filter.$or = [
                    { name: { $regex: query, $options: 'i' } },
                    { description: { $regex: query, $options: 'i' } }
                ];
            }
            if (location) {
                filter.location = { $regex: location, $options: 'i' };
            }
            if (startDate) {
                filter.startDate = { $gte: startDate };
            }
            if (endDate) {
                filter.endDate = { $lte: endDate };
            }
            // 处理排序
            const [sortField, sortOrder] = sort.split('_');
            const sortOptions = {};
            sortOptions[sortField] = sortOrder === 'desc' ? -1 : 1;
            // 执行查询
            const total = await activity_model_1.ActivityModel.countDocuments(filter);
            const activities = await activity_model_1.ActivityModel.find(filter)
                .sort(sortOptions)
                .skip(skip)
                .limit(limit)
                .lean();
            // 转换结果
            const activityInfos = activities.map(activity => ({
                id: activity._id.toString(),
                name: activity.name,
                description: activity.description,
                location: activity.location,
                startDate: activity.startDate,
                endDate: activity.endDate,
                capacity: activity.capacity,
                currentRegistrations: activity.currentRegistrations,
                price: activity.price,
                category: activity.category,
                organizer: activity.organizer,
                contactInfo: activity.contactInfo,
                images: activity.images,
                requirements: activity.requirements,
                included: activity.included,
                reviews: activity.reviews,
                metadata: activity.metadata
            }));
            // 更新指标
            metrics_1.farmActivityCounter.inc({
                activity_type: category || 'all',
                location: 'multiple',
                status: 'view'
            });
            return { activities: activityInfos, total };
        }
        catch (error) {
            logger_1.logger.error(`获取活动列表失败:`, error);
            throw error;
        }
    }
    /**
     * 获取活动详情
     */
    async getActivityById(activityId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `activity:${activityId}`;
            const cachedActivity = await (0, cache_1.getCache)(cacheKey);
            if (cachedActivity) {
                logger_1.logger.debug(`从缓存获取活动信息: ${activityId}`);
                // 更新指标
                metrics_1.farmActivityCounter.inc({
                    activity_type: cachedActivity.category,
                    location: cachedActivity.location,
                    status: 'view'
                });
                return cachedActivity;
            }
            // 从数据库获取
            const activity = await activity_model_1.ActivityModel.findById(activityId).lean();
            if (!activity) {
                logger_1.logger.debug(`活动不存在: ${activityId}`);
                return null;
            }
            // 转换为FarmActivity类型
            const activityInfo = {
                id: activity._id.toString(),
                name: activity.name,
                description: activity.description,
                location: activity.location,
                startDate: activity.startDate,
                endDate: activity.endDate,
                capacity: activity.capacity,
                currentRegistrations: activity.currentRegistrations,
                price: activity.price,
                category: activity.category,
                organizer: activity.organizer,
                contactInfo: activity.contactInfo,
                images: activity.images,
                requirements: activity.requirements,
                included: activity.included,
                reviews: activity.reviews,
                metadata: activity.metadata
            };
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, activityInfo, ACTIVITY_CACHE_TTL);
            // 更新指标
            metrics_1.farmActivityCounter.inc({
                activity_type: activity.category,
                location: activity.location,
                status: 'view'
            });
            return activityInfo;
        }
        catch (error) {
            logger_1.logger.error(`获取活动信息失败:`, error);
            throw error;
        }
    }
    /**
     * 预约活动
     */
    async registerForActivity(activityId, userId, participants) {
        try {
            // 使用事务确保原子性
            const session = await mongoose_1.default.startSession();
            session.startTransaction();
            try {
                // 查找活动
                const activity = await activity_model_1.ActivityModel.findById(activityId).session(session);
                if (!activity) {
                    throw new Error(`活动不存在: ${activityId}`);
                }
                // 检查是否已经注册
                const existingRegistration = await activity_model_1.ActivityRegistrationModel.findOne({
                    activityId,
                    userId
                }).session(session);
                if (existingRegistration) {
                    throw new Error('您已经预约过此活动');
                }
                // 检查容量
                if (activity.currentRegistrations + participants > activity.capacity) {
                    throw new Error('活动名额不足');
                }
                // 创建预约记录
                await activity_model_1.ActivityRegistrationModel.create([{
                        activityId,
                        userId,
                        participants,
                        registrationDate: new Date().toISOString(),
                        status: 'confirmed'
                    }], { session });
                // 更新活动当前注册人数
                await activity_model_1.ActivityModel.findByIdAndUpdate(activityId, { $inc: { currentRegistrations: participants } }, { session });
                // 提交事务
                await session.commitTransaction();
                // 清除缓存
                const cacheKey = `activity:${activityId}`;
                await (0, cache_1.setCache)(cacheKey, null, 1);
                // 更新指标
                metrics_1.farmActivityCounter.inc({
                    activity_type: activity.category,
                    location: activity.location,
                    status: 'registered'
                });
                return true;
            }
            catch (error) {
                // 回滚事务
                await session.abortTransaction();
                throw error;
            }
            finally {
                // 结束会话
                session.endSession();
            }
        }
        catch (error) {
            logger_1.logger.error(`预约活动失败:`, error);
            throw error;
        }
    }
    /**
     * 添加活动评价
     */
    async addActivityReview(activityId, review) {
        try {
            // 添加日期
            const reviewWithDate = {
                ...review,
                date: new Date().toISOString()
            };
            // 更新活动评价
            const activity = await activity_model_1.ActivityModel.findByIdAndUpdate(activityId, { $push: { reviews: reviewWithDate } }, { new: true }).lean();
            if (!activity) {
                logger_1.logger.debug(`活动不存在: ${activityId}`);
                return null;
            }
            // 清除缓存
            const cacheKey = `activity:${activityId}`;
            await (0, cache_1.setCache)(cacheKey, null, 1);
            // 转换为FarmActivity类型
            const activityInfo = {
                id: activity._id.toString(),
                name: activity.name,
                description: activity.description,
                location: activity.location,
                startDate: activity.startDate,
                endDate: activity.endDate,
                capacity: activity.capacity,
                currentRegistrations: activity.currentRegistrations,
                price: activity.price,
                category: activity.category,
                organizer: activity.organizer,
                contactInfo: activity.contactInfo,
                images: activity.images,
                requirements: activity.requirements,
                included: activity.included,
                reviews: activity.reviews,
                metadata: activity.metadata
            };
            // 更新指标
            metrics_1.farmActivityCounter.inc({
                activity_type: activity.category,
                location: activity.location,
                status: 'reviewed'
            });
            return activityInfo;
        }
        catch (error) {
            logger_1.logger.error(`添加活动评价失败:`, error);
            throw error;
        }
    }
    /**
     * 获取热门活动
     */
    async getPopularActivities(limit = 5) {
        try {
            // 尝试从缓存获取
            const cacheKey = `activities:popular:limit:${limit}`;
            const cachedActivities = await (0, cache_1.getCache)(cacheKey);
            if (cachedActivities) {
                logger_1.logger.debug(`从缓存获取热门活动`);
                return cachedActivities;
            }
            // 查询热门活动 (基于注册人数百分比)
            const activities = await activity_model_1.ActivityModel.aggregate([
                {
                    $match: {
                        startDate: { $gte: new Date().toISOString() }
                    }
                },
                {
                    $addFields: {
                        registrationPercentage: {
                            $multiply: [
                                { $divide: ['$currentRegistrations', '$capacity'] },
                                100
                            ]
                        }
                    }
                },
                {
                    $sort: { registrationPercentage: -1 }
                },
                {
                    $limit: limit
                }
            ]);
            // 转换结果
            const activityInfos = activities.map(activity => ({
                id: activity._id.toString(),
                name: activity.name,
                description: activity.description,
                location: activity.location,
                startDate: activity.startDate,
                endDate: activity.endDate,
                capacity: activity.capacity,
                currentRegistrations: activity.currentRegistrations,
                price: activity.price,
                category: activity.category,
                organizer: activity.organizer,
                contactInfo: activity.contactInfo,
                images: activity.images,
                requirements: activity.requirements,
                included: activity.included,
                reviews: activity.reviews,
                metadata: activity.metadata
            }));
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, activityInfos, ACTIVITY_CACHE_TTL);
            return activityInfos;
        }
        catch (error) {
            logger_1.logger.error(`获取热门活动失败:`, error);
            throw error;
        }
    }
}
exports.ActivityService = ActivityService;
exports.default = new ActivityService();
