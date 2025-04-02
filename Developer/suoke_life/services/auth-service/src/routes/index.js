/**
 * 路由配置入口
 */
const express = require('express');
const router = express.Router();

// 导入路由
const authRoutes = require('./auth.routes');
const oauthRoutes = require('./oauth.routes');
const phoneAuthRoutes = require('./phone-auth.routes');
const internalRoutes = require('./internal');
const knowledgeAuthRoutes = require('./knowledge-auth.routes');
const sessionsRoutes = require('./sessions.routes');
const smsAuthRoutes = require('./sms-auth.routes');
const twoFactorRoutes = require('./two-factor.routes');
const securityLogsRoutes = require('./security-logs.routes');
const biometricRoutes = require('./biometric.routes');
const deviceRoutes = require('./device.routes');
const deviceVerificationRoutes = require('./device-verification.routes');
const securityDashboardRoutes = require('./security-dashboard.routes');

// 注册路由
router.use('/auth', authRoutes);
router.use('/oauth', oauthRoutes);
router.use('/phone', phoneAuthRoutes);
router.use('/internal', internalRoutes);
router.use('/knowledge', knowledgeAuthRoutes);
router.use('/sessions', sessionsRoutes);
router.use('/sms', smsAuthRoutes);
router.use('/2fa', twoFactorRoutes);
router.use('/security-logs', securityLogsRoutes);
router.use('/biometric', biometricRoutes);
router.use('/devices', deviceRoutes);
router.use('/device-verification', deviceVerificationRoutes);
router.use('/security-dashboard', securityDashboardRoutes);

module.exports = router; 