"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupRoutes = void 0;
const user_routes_1 = __importDefault(require("../../routes/user.routes"));
const auth_routes_1 = __importDefault(require("../../routes/auth.routes"));
const product_routes_1 = __importDefault(require("../../routes/product.routes"));
const traceability_routes_1 = __importDefault(require("../../routes/traceability.routes"));
const visualization_routes_1 = __importDefault(require("../../routes/visualization.routes"));
const blockchain_routes_1 = __importDefault(require("../../routes/blockchain.routes"));
const seasonal_routes_1 = __importDefault(require("../../routes/seasonal.routes"));
const recommendation_routes_1 = __importDefault(require("../../routes/recommendation.routes"));
const knowledge_routes_1 = __importDefault(require("../../routes/knowledge.routes"));
const supply_chain_routes_1 = __importDefault(require("../../routes/supply-chain.routes"));
const logger_1 = require("../../utils/logger");
const metrics_1 = require("../metrics");
/**
 * 设置所有路由
 * @param app Express 应用实例
 * @param io Socket.IO 服务器实例
 */
const setupRoutes = (app, io) => {
    // API 前缀
    const apiPrefix = '/api/v1';
    // 基础健康检查路由
    app.get('/health', (req, res) => {
        metrics_1.httpRequestsTotal.inc({ method: req.method, path: '/health', status: '200' });
        res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });
    app.get('/', (req, res) => {
        metrics_1.httpRequestsTotal.inc({ method: req.method, path: '/', status: '200' });
        res.json({
            name: 'Xiaoke API Service',
            version: process.env.APP_VERSION || '1.0.0',
            environment: process.env.NODE_ENV || 'development'
        });
    });
    // 使用路由模块
    logger_1.logger.info(`设置API路由，前缀: ${apiPrefix}`);
    app.use(`${apiPrefix}/users`, (0, user_routes_1.default)(io));
    app.use(`${apiPrefix}/auth`, (0, auth_routes_1.default)(io));
    app.use(`${apiPrefix}/products`, (0, product_routes_1.default)(io));
    app.use(`${apiPrefix}/traceability`, (0, traceability_routes_1.default)(io));
    app.use(`${apiPrefix}/visualization`, (0, visualization_routes_1.default)(io));
    app.use(`${apiPrefix}/blockchain`, (0, blockchain_routes_1.default)(io));
    app.use(`${apiPrefix}/seasonal`, (0, seasonal_routes_1.default)(io));
    app.use(`${apiPrefix}/recommendations`, (0, recommendation_routes_1.default)(io));
    app.use(`${apiPrefix}/knowledge`, (0, knowledge_routes_1.default)(io));
    app.use(`${apiPrefix}/supply-chain`, (0, supply_chain_routes_1.default)(io));
    // 404 处理
    app.use((req, res) => {
        metrics_1.httpRequestsTotal.inc({ method: req.method, path: 'not_found', status: '404' });
        res.status(404).json({
            success: false,
            error: '请求的路径不存在',
            code: 'ROUTE_NOT_FOUND'
        });
    });
    // 全局错误处理
    app.use((err, req, res, next) => {
        logger_1.logger.error('全局错误处理器捕获到错误:', err);
        metrics_1.httpRequestsTotal.inc({ method: req.method, path: req.path, status: '500' });
        res.status(500).json({
            success: false,
            error: '服务器内部错误',
            message: process.env.NODE_ENV === 'production' ? '请稍后再试' : err.message,
            code: 'SERVER_ERROR'
        });
    });
};
exports.setupRoutes = setupRoutes;
exports.default = exports.setupRoutes;
