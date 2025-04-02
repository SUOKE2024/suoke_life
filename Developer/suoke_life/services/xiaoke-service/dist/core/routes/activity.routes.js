"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const auth_middleware_1 = require("../middleware/auth.middleware");
const activity_controller_1 = __importDefault(require("../../controllers/activity.controller"));
/**
 * 活动路由
 */
exports.default = (io) => {
    const router = express_1.default.Router();
    // 获取活动列表
    router.get('/', activity_controller_1.default.getActivities);
    // 获取热门活动
    router.get('/popular', activity_controller_1.default.getPopularActivities);
    // 获取活动详情
    router.get('/:id', activity_controller_1.default.getActivityById);
    // 活动预约（需要登录）
    router.post('/:id/register', auth_middleware_1.requireAuth, activity_controller_1.default.registerForActivity);
    // 提交活动评价（需要登录）
    router.post('/:id/review', auth_middleware_1.requireAuth, activity_controller_1.default.addActivityReview);
    return router;
};
