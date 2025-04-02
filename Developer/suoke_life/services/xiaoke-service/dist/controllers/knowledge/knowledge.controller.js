"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeController = void 0;
const logger_1 = require("../../utils/logger");
/**
 * 知识控制器
 */
class KnowledgeController {
    constructor(knowledgeBaseService, knowledgeGraphService, knowledgeIntegrationService) {
        this.logger = new logger_1.Logger('KnowledgeController');
        /**
         * 搜索知识库
         */
        this.searchKnowledge = async (req, res) => {
            try {
                const { query } = req.body;
                const options = req.body.options || {};
                if (!query) {
                    res.status(400).json({ error: '查询内容不能为空' });
                    return;
                }
                const result = await this.knowledgeBaseService.search(query, options);
                res.json(result);
            }
            catch (error) {
                this.logger.error('搜索知识库失败', error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 获取知识条目
         */
        this.getKnowledgeItem = async (req, res) => {
            try {
                const { id } = req.params;
                if (!id) {
                    res.status(400).json({ error: '知识条目ID不能为空' });
                    return;
                }
                const item = await this.knowledgeBaseService.getItem(id);
                res.json(item);
            }
            catch (error) {
                this.logger.error(`获取知识条目失败: ${req.params.id}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 根据分类获取知识条目
         */
        this.getKnowledgeByCategory = async (req, res) => {
            try {
                const { category } = req.params;
                const limit = parseInt(req.query.limit) || 20;
                if (!category) {
                    res.status(400).json({ error: '分类名称不能为空' });
                    return;
                }
                const items = await this.knowledgeBaseService.getItemsByCategory(category, limit);
                res.json(items);
            }
            catch (error) {
                this.logger.error(`获取分类知识失败: ${req.params.category}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 根据标签获取知识条目
         */
        this.getKnowledgeByTag = async (req, res) => {
            try {
                const { tag } = req.params;
                const limit = parseInt(req.query.limit) || 20;
                if (!tag) {
                    res.status(400).json({ error: '标签名称不能为空' });
                    return;
                }
                const items = await this.knowledgeBaseService.getItemsByTag(tag, limit);
                res.json(items);
            }
            catch (error) {
                this.logger.error(`获取标签知识失败: ${req.params.tag}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 搜索图谱节点
         */
        this.searchGraphNodes = async (req, res) => {
            try {
                const { query } = req.query;
                if (!query) {
                    res.status(400).json({ error: '查询内容不能为空' });
                    return;
                }
                const nodes = await this.knowledgeGraphService.searchNodes(query);
                res.json(nodes);
            }
            catch (error) {
                this.logger.error(`搜索图谱节点失败: ${req.query.query}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 获取节点关系
         */
        this.getNodeRelations = async (req, res) => {
            try {
                const { nodeId } = req.params;
                if (!nodeId) {
                    res.status(400).json({ error: '节点ID不能为空' });
                    return;
                }
                const relations = await this.knowledgeGraphService.getNodeRelations(nodeId);
                res.json(relations);
            }
            catch (error) {
                this.logger.error(`获取节点关系失败: ${req.params.nodeId}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 查找最短路径
         */
        this.findShortestPath = async (req, res) => {
            try {
                const { fromId, toId } = req.query;
                if (!fromId || !toId) {
                    res.status(400).json({ error: '起始节点ID和目标节点ID不能为空' });
                    return;
                }
                const path = await this.knowledgeGraphService.findShortestPath(fromId, toId);
                res.json(path);
            }
            catch (error) {
                this.logger.error(`查找最短路径失败: ${req.query.fromId} -> ${req.query.toId}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 产品知识增强
         */
        this.enrichProductKnowledge = async (req, res) => {
            try {
                const { productId } = req.params;
                if (!productId) {
                    res.status(400).json({ error: '产品ID不能为空' });
                    return;
                }
                const enrichment = await this.knowledgeIntegrationService.enrichProductKnowledge(productId);
                res.json(enrichment);
            }
            catch (error) {
                this.logger.error(`产品知识增强失败: ${req.params.productId}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 搜索农产品与健康知识的关联
         */
        this.searchAgricultureHealthKnowledge = async (req, res) => {
            try {
                const { query } = req.body;
                const options = req.body.options || {};
                if (!query) {
                    res.status(400).json({ error: '查询内容不能为空' });
                    return;
                }
                const result = await this.knowledgeIntegrationService.searchAgricultureHealthKnowledge(query, options);
                res.json(result);
            }
            catch (error) {
                this.logger.error('搜索农产品健康知识失败', error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 获取产品相关健康知识
         */
        this.getProductHealthKnowledge = async (req, res) => {
            try {
                const { productId } = req.params;
                if (!productId) {
                    res.status(400).json({ error: '产品ID不能为空' });
                    return;
                }
                const items = await this.knowledgeIntegrationService.getProductHealthKnowledge(productId);
                res.json(items);
            }
            catch (error) {
                this.logger.error(`获取产品健康知识失败: ${req.params.productId}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 获取节气相关农产品知识
         */
        this.getSolarTermAgricultureKnowledge = async (req, res) => {
            try {
                const { solarTerm } = req.params;
                if (!solarTerm) {
                    res.status(400).json({ error: '节气名称不能为空' });
                    return;
                }
                const result = await this.knowledgeIntegrationService.getSolarTermAgricultureKnowledge(solarTerm);
                res.json(result);
            }
            catch (error) {
                this.logger.error(`获取节气农产品知识失败: ${req.params.solarTerm}`, error);
                res.status(500).json({ error: error.message });
            }
        };
        /**
         * 服务健康检查
         */
        this.healthCheck = async (_req, res) => {
            res.json({ status: 'ok', message: '知识服务正常运行' });
        };
        this.knowledgeBaseService = knowledgeBaseService;
        this.knowledgeGraphService = knowledgeGraphService;
        this.knowledgeIntegrationService = knowledgeIntegrationService;
    }
}
exports.KnowledgeController = KnowledgeController;
