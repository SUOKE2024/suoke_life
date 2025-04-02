"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeIntegrationServiceImpl = exports.KnowledgeGraphServiceImpl = exports.KnowledgeBaseServiceImpl = void 0;
exports.createKnowledgeBaseService = createKnowledgeBaseService;
exports.createKnowledgeGraphService = createKnowledgeGraphService;
exports.createKnowledgeIntegrationService = createKnowledgeIntegrationService;
exports.initializeKnowledgeServices = initializeKnowledgeServices;
const knowledge_base_service_1 = require("./knowledge-base.service");
const knowledge_graph_service_1 = require("./knowledge-graph.service");
const knowledge_integration_service_1 = require("./knowledge-integration.service");
/**
 * 创建知识库服务
 */
function createKnowledgeBaseService() {
    return new knowledge_base_service_1.KnowledgeBaseServiceImpl();
}
/**
 * 创建知识图谱服务
 */
function createKnowledgeGraphService() {
    return new knowledge_graph_service_1.KnowledgeGraphServiceImpl();
}
/**
 * 创建知识整合服务
 */
function createKnowledgeIntegrationService(knowledgeBaseService, knowledgeGraphService) {
    return new knowledge_integration_service_1.KnowledgeIntegrationServiceImpl(knowledgeBaseService, knowledgeGraphService);
}
/**
 * 知识服务初始化
 */
async function initializeKnowledgeServices() {
    // 创建服务实例
    const knowledgeBaseService = createKnowledgeBaseService();
    const knowledgeGraphService = createKnowledgeGraphService();
    // 初始化基础服务
    await Promise.all([
        knowledgeBaseService.initialize(),
        knowledgeGraphService.initialize()
    ]);
    // 创建并初始化整合服务
    const knowledgeIntegrationService = createKnowledgeIntegrationService(knowledgeBaseService, knowledgeGraphService);
    await knowledgeIntegrationService.initialize();
    return {
        knowledgeBaseService,
        knowledgeGraphService,
        knowledgeIntegrationService
    };
}
// 导出类型和服务
__exportStar(require("./types"), exports);
var knowledge_base_service_2 = require("./knowledge-base.service");
Object.defineProperty(exports, "KnowledgeBaseServiceImpl", { enumerable: true, get: function () { return knowledge_base_service_2.KnowledgeBaseServiceImpl; } });
var knowledge_graph_service_2 = require("./knowledge-graph.service");
Object.defineProperty(exports, "KnowledgeGraphServiceImpl", { enumerable: true, get: function () { return knowledge_graph_service_2.KnowledgeGraphServiceImpl; } });
var knowledge_integration_service_2 = require("./knowledge-integration.service");
Object.defineProperty(exports, "KnowledgeIntegrationServiceImpl", { enumerable: true, get: function () { return knowledge_integration_service_2.KnowledgeIntegrationServiceImpl; } });
