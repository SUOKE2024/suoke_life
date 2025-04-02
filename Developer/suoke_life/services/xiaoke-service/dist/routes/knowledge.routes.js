"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = knowledgeRoutes;
/**
 * 知识相关路由
 */
const express_1 = require("express");
const knowledge_1 = require("../controllers/knowledge");
const knowledge_2 = require("./knowledge");
const logger_1 = require("../utils/logger");
const knowledge_3 = require("../services/knowledge");
/**
 * 创建知识服务路由
 */
function knowledgeRoutes(io) {
    const router = (0, express_1.Router)();
    logger_1.logger.info('初始化知识服务路由');
    try {
        // 创建服务实例
        const knowledgeBaseService = (0, knowledge_3.createKnowledgeBaseService)();
        const knowledgeGraphService = (0, knowledge_3.createKnowledgeGraphService)();
        const knowledgeIntegrationService = (0, knowledge_3.createKnowledgeIntegrationService)(knowledgeBaseService, knowledgeGraphService);
        // 初始化服务
        Promise.all([
            knowledgeBaseService.initialize(),
            knowledgeGraphService.initialize()
        ]).then(() => {
            return knowledgeIntegrationService.initialize();
        }).then(() => {
            logger_1.logger.info('知识服务已成功初始化');
            // 通知客户端服务已就绪
            io.emit('knowledge:ready', { status: 'ready' });
        }).catch(error => {
            logger_1.logger.error('知识服务初始化失败', error);
            io.emit('knowledge:error', { status: 'error', message: error.message });
        });
        // 创建控制器
        const knowledgeController = new knowledge_1.KnowledgeController(knowledgeBaseService, knowledgeGraphService, knowledgeIntegrationService);
        // 获取知识路由
        const knowledgeApiRoutes = (0, knowledge_2.createKnowledgeRoutes)(knowledgeController);
        // 挂载子路由
        router.use('/', knowledgeApiRoutes);
        // WebSocket事件处理
        io.on('connection', (socket) => {
            // 知识查询事件
            socket.on('knowledge:search', async (data) => {
                try {
                    const result = await knowledgeBaseService.search(data.query, data.options);
                    socket.emit('knowledge:search:result', { success: true, result });
                }
                catch (error) {
                    logger_1.logger.error('知识查询WebSocket错误', error);
                    socket.emit('knowledge:search:result', {
                        success: false,
                        error: error.message
                    });
                }
            });
            // 产品知识增强事件
            socket.on('knowledge:product:enrich', async (data) => {
                try {
                    const result = await knowledgeIntegrationService.enrichProductKnowledge(data.productId);
                    socket.emit('knowledge:product:enrich:result', { success: true, result });
                }
                catch (error) {
                    logger_1.logger.error('产品知识增强WebSocket错误', error);
                    socket.emit('knowledge:product:enrich:result', {
                        success: false,
                        error: error.message
                    });
                }
            });
        });
    }
    catch (error) {
        logger_1.logger.error('知识服务路由初始化失败', error);
        router.use('/', (_req, res) => {
            res.status(500).json({
                success: false,
                error: '知识服务暂不可用',
                message: error.message,
                code: 'KNOWLEDGE_SERVICE_UNAVAILABLE'
            });
        });
    }
    return router;
}
