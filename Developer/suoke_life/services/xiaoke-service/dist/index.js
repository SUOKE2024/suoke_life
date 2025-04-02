"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const dotenv_1 = __importDefault(require("dotenv"));
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const metrics_1 = require("./utils/metrics");
const routes_1 = require("./core/routes");
const error_middleware_1 = require("./core/middleware/error.middleware");
const request_logger_middleware_1 = require("./core/middleware/request-logger.middleware");
const agent_1 = require("./core/agent");
const database_1 = require("./core/database");
const cache_1 = require("./core/cache");
const telemetry_1 = require("./utils/telemetry");
const vault_1 = require("./utils/vault");
// 加载环境变量
dotenv_1.default.config();
// 初始化日志记录器
const logger = logger('app');
// 应用程序初始化
async function initializeApp() {
    try {
        // 设置OpenTelemetry
        await (0, telemetry_1.setupOpenTelemetry)();
        logger.info('OpenTelemetry initialized');
        // 设置Vault(如果启用)
        if (process.env.USE_VAULT === 'true') {
            await (0, vault_1.setupVault)();
            logger.info('Vault initialized');
        }
        // 初始化指标
        const metricsRegistry = (0, metrics_1.setupMetrics)();
        logger.info('Metrics initialized');
        // 创建Express应用
        const app = (0, express_1.default)();
        const PORT = process.env.PORT || 3011;
        const METRICS_PORT = process.env.METRICS_PORT || 9464;
        // 创建HTTP服务器和WebSocket
        const httpServer = (0, http_1.createServer)(app);
        const io = new socket_io_1.Server(httpServer, {
            cors: {
                origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
                methods: ['GET', 'POST'],
                credentials: true
            }
        });
        // 设置中间件
        app.use((0, cors_1.default)({
            origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
            credentials: true
        }));
        app.use(express_1.default.json({ limit: '50mb' }));
        app.use(express_1.default.urlencoded({ extended: true, limit: '50mb' }));
        app.use(request_logger_middleware_1.requestLoggerMiddleware);
        // 请求日志中间件
        app.use((req, res, next) => {
            const start = Date.now();
            res.on('finish', () => {
                const duration = Date.now() - start;
                logger.info(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
                // 记录请求指标
                (0, metrics_1.recordMetric)('xiaoke_requests_total', 1, {
                    method: req.method,
                    path: req.path,
                    status: res.statusCode.toString()
                });
                (0, metrics_1.recordMetric)('xiaoke_response_time', duration, {
                    method: req.method,
                    path: req.path
                });
                if (res.statusCode >= 400) {
                    (0, metrics_1.recordMetric)('xiaoke_errors_total', 1, {
                        method: req.method,
                        path: req.path,
                        status: res.statusCode.toString()
                    });
                }
            });
            next();
        });
        // 健康检查路由
        app.get('/health', (req, res) => {
            res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
        });
        // 读取配置文件示例(包括从Vault获取密钥)
        app.get('/api/v1/config-info', async (req, res) => {
            try {
                let dbConfig = {
                    host: process.env.MONGODB_URI || 'mongodb://localhost:27017',
                    type: 'MongoDB',
                    secured: true
                };
                // 演示从Vault获取密钥(如果启用)
                if (process.env.USE_VAULT === 'true') {
                    const mongoPassword = await (0, vault_1.getSecretFromVault)('mongodb-password');
                    const redisPassword = await (0, vault_1.getSecretFromVault)('redis-password');
                    dbConfig = {
                        ...dbConfig,
                        passwordSource: 'Vault',
                        passwordLength: mongoPassword ? mongoPassword.length : 0,
                        redisPasswordLength: redisPassword ? redisPassword.length : 0
                    };
                }
                res.json({
                    service: 'xiaoke-service',
                    version: '1.0.0',
                    environment: process.env.NODE_ENV,
                    database: dbConfig
                });
            }
            catch (error) {
                logger.error('Error fetching config info', error);
                res.status(500).json({ error: 'Failed to fetch configuration information' });
            }
        });
        // 读取系统状态
        app.get('/api/v1/status', (req, res) => {
            const memoryUsage = process.memoryUsage();
            const formattedMemory = {
                rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} MB`,
                heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} MB`,
                heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} MB`,
                external: `${Math.round(memoryUsage.external / 1024 / 1024)} MB`
            };
            res.json({
                uptime: process.uptime(),
                timestamp: Date.now(),
                memoryUsage: formattedMemory,
                environment: process.env.NODE_ENV
            });
        });
        // 设置API路由
        (0, routes_1.setupRoutes)(app, io);
        // 错误处理中间件 (必须在所有路由之后)
        app.use(error_middleware_1.errorMiddleware);
        // 启动服务器
        await (0, database_1.connectToDatabase)();
        await (0, cache_1.setupRedisClient)();
        await (0, agent_1.setupAgentSystem)();
        httpServer.listen(PORT, () => {
            logger.info(`Server running on port ${PORT}`);
        });
        // 启动指标服务器
        const metricsApp = (0, express_1.default)();
        metricsApp.get('/metrics', async (req, res) => {
            try {
                const metrics = await metricsRegistry.metrics();
                res.set('Content-Type', metricsRegistry.contentType);
                res.end(metrics);
            }
            catch (error) {
                logger.error('Error generating metrics', error);
                res.status(500).end();
            }
        });
        metricsApp.listen(METRICS_PORT, () => {
            logger.info(`Metrics server running on port ${METRICS_PORT}`);
        });
    }
    catch (error) {
        logger.error('Failed to initialize application', error);
        process.exit(1);
    }
}
// 启动应用
initializeApp().catch(error => {
    console.error('Fatal error during initialization:', error);
    process.exit(1);
});
// 优雅关闭
process.on('SIGTERM', () => {
    logger.info('SIGTERM signal received, closing HTTP server');
    process.exit(0);
});
process.on('SIGINT', () => {
    logger.info('SIGINT signal received, closing HTTP server');
    process.exit(0);
});
