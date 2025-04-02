/**
 * 路由索引文件
 * 集中管理和导出所有路由
 */
const express = require('express');
const router = express.Router();

// 导入路由模块
const userRoutes = require('./user.routes');
const profileRoutes = require('./profile.routes');
const healthRoutes = require('./health.routes');
const healthProfileRoutes = require('./health-profile.routes');
const openaiRoutes = require('./openai.routes');
const knowledgePreferenceRoutes = require('./knowledge-preference.routes');
const recommendationRoutes = require('./recommendation.routes');
const socialShareRoutes = require('./social-share.routes');
const userMatchRoutes = require('./user-match.routes');
const apiDocsRoutes = require('./api-docs.routes');

// 注册路由
router.use('/users', userRoutes);
router.use('/profiles', profileRoutes);
router.use('/health', healthRoutes);
router.use('/health-profiles', healthProfileRoutes);
router.use('/openai', openaiRoutes);
router.use('/knowledge-preferences', knowledgePreferenceRoutes);
router.use('/recommendations', recommendationRoutes);
router.use('/social-shares', socialShareRoutes);
router.use('/user-matches', userMatchRoutes);
router.use('/api-docs', apiDocsRoutes);

module.exports = router;