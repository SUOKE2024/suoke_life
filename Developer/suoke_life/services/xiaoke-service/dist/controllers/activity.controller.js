"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ActivityController = void 0;
const logger_1 = require("../utils/logger");
const activity_service_1 = __importDefault(require("../services/activity/activity.service"));
const metrics_1 = require("../core/metrics");
/**
 * 活动控制器
 * 处理与农事活动相关的HTTP请求
 */
class ActivityController {
    constructor(activityService) {
        /**
         * 获取活动列表
         */
        this.getActivities = async (req, res) => {
            try {
                const { category, query, location, startDate, endDate, sort = 'startDate_asc', limit = 20, skip = 0 } = req.query;
                const result = await this.activityService.getActivities({
                    category: category,
                    query: query,
                    location: location,
                    startDate: startDate,
                    endDate: endDate,
                    sort: sort,
                    limit: Number(limit),
                    skip: Number(skip)
                });
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities',
                    status: '200'
                });
                res.status(200).json(result);
            }
            catch (error) {
                logger_1.logger.error('获取活动列表失败', error);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities',
                    status: '500'
                });
                res.status(500).json({
                    error: '获取活动列表失败',
                    message: error.message
                });
            }
        };
        /**
         * 获取活动详情
         */
        this.getActivityById = async (req, res) => {
            try {
                const { id } = req.params;
                const activity = await this.activityService.getActivityById(id);
                if (!activity) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id',
                        status: '404'
                    });
                    res.status(404).json({ error: '活动不存在' });
                    return;
                }
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id',
                    status: '200'
                });
                res.status(200).json(activity);
            }
            catch (error) {
                logger_1.logger.error(`获取活动详情失败: ${req.params.id}`, error);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id',
                    status: '500'
                });
                res.status(500).json({
                    error: '获取活动详情失败',
                    message: error.message
                });
            }
        };
        /**
         * 预约活动
         */
        this.registerForActivity = async (req, res) => {
            try {
                const { id } = req.params;
                const { participants } = req.body;
                const userId = req.user?.id;
                if (!userId) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/register',
                        status: '401'
                    });
                    res.status(401).json({ error: '用户未认证' });
                    return;
                }
                if (!participants || participants < 1) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/register',
                        status: '400'
                    });
                    res.status(400).json({ error: '参与人数必须大于0' });
                    return;
                }
                const result = await this.activityService.registerForActivity(id, userId, participants);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id/register',
                    status: '200'
                });
                res.status(200).json({ success: true, message: '活动预约成功' });
            }
            catch (error) {
                logger_1.logger.error(`预约活动失败: ${req.params.id}`, error);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id/register',
                    status: '500'
                });
                const errorMessage = error.message;
                if (errorMessage.includes('已经预约过')) {
                    res.status(400).json({ error: errorMessage });
                }
                else if (errorMessage.includes('名额不足')) {
                    res.status(400).json({ error: errorMessage });
                }
                else if (errorMessage.includes('不存在')) {
                    res.status(404).json({ error: errorMessage });
                }
                else {
                    res.status(500).json({
                        error: '预约活动失败',
                        message: errorMessage
                    });
                }
            }
        };
        /**
         * 添加活动评价
         */
        this.addActivityReview = async (req, res) => {
            try {
                const { id } = req.params;
                const { rating, comment, photoUrls } = req.body;
                const userId = req.user?.id;
                if (!userId) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/review',
                        status: '401'
                    });
                    res.status(401).json({ error: '用户未认证' });
                    return;
                }
                if (!rating || rating < 1 || rating > 5) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/review',
                        status: '400'
                    });
                    res.status(400).json({ error: '评分必须在1-5之间' });
                    return;
                }
                if (!comment || comment.trim().length === 0) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/review',
                        status: '400'
                    });
                    res.status(400).json({ error: '评论内容不能为空' });
                    return;
                }
                const activity = await this.activityService.addActivityReview(id, {
                    userId,
                    rating,
                    comment,
                    photoUrls
                });
                if (!activity) {
                    // 记录指标
                    metrics_1.httpRequestsTotal.inc({
                        method: req.method,
                        path: '/api/v1/activities/:id/review',
                        status: '404'
                    });
                    res.status(404).json({ error: '活动不存在' });
                    return;
                }
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id/review',
                    status: '200'
                });
                res.status(200).json({
                    success: true,
                    message: '评价提交成功',
                    activity
                });
            }
            catch (error) {
                logger_1.logger.error(`添加活动评价失败: ${req.params.id}`, error);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/:id/review',
                    status: '500'
                });
                res.status(500).json({
                    error: '添加活动评价失败',
                    message: error.message
                });
            }
        };
        /**
         * 获取热门活动
         */
        this.getPopularActivities = async (req, res) => {
            try {
                const { limit = 5 } = req.query;
                const activities = await this.activityService.getPopularActivities(Number(limit));
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/popular',
                    status: '200'
                });
                res.status(200).json(activities);
            }
            catch (error) {
                logger_1.logger.error('获取热门活动失败', error);
                // 记录指标
                metrics_1.httpRequestsTotal.inc({
                    method: req.method,
                    path: '/api/v1/activities/popular',
                    status: '500'
                });
                res.status(500).json({
                    error: '获取热门活动失败',
                    message: error.message
                });
            }
        };
        this.activityService = activityService;
    }
}
exports.ActivityController = ActivityController;
exports.default = new ActivityController(activity_service_1.default);
