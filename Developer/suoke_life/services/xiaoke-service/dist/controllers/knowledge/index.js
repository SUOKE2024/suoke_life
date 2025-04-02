"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeController = void 0;
exports.createKnowledgeController = createKnowledgeController;
const knowledge_controller_1 = require("./knowledge.controller");
/**
 * 创建知识控制器
 */
function createKnowledgeController(knowledgeBaseService, knowledgeGraphService, knowledgeIntegrationService) {
    return new knowledge_controller_1.KnowledgeController(knowledgeBaseService, knowledgeGraphService, knowledgeIntegrationService);
}
// 导出控制器类
var knowledge_controller_2 = require("./knowledge.controller");
Object.defineProperty(exports, "KnowledgeController", { enumerable: true, get: function () { return knowledge_controller_2.KnowledgeController; } });
