"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.BlockchainController = void 0;
const logger_1 = require("../utils/logger");
const blockchain_service_1 = __importDefault(require("../services/traceability/blockchain.service"));
const metrics_1 = require("../core/metrics");
/**
 * 区块链控制器
 * 处理与区块链集成相关的HTTP请求
 */
class BlockchainController {
    constructor(blockchainService) {
        this.blockchainService = blockchainService;
    }
    /**
     * 上传溯源数据到区块链
     */
    async uploadToBlockchain(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/blockchain/upload',
                status: '200'
            });
            const { traceabilityId } = req.body;
            if (!traceabilityId) {
                res.status(400).json({
                    success: false,
                    error: '缺少溯源ID',
                    code: 'MISSING_TRACEABILITY_ID'
                });
                return;
            }
            const result = await this.blockchainService.uploadToBlockchain(traceabilityId);
            if (!result.success) {
                res.status(400).json({
                    success: false,
                    error: result.message || '上链失败',
                    code: 'BLOCKCHAIN_UPLOAD_FAILED'
                });
                return;
            }
            res.json({
                success: true,
                data: {
                    traceabilityId,
                    transactionId: result.transactionId,
                    blockNumber: result.blockNumber,
                    timestamp: result.timestamp,
                    message: '上链成功'
                }
            });
        }
        catch (error) {
            logger_1.logger.error('上传到区块链失败:', error);
            res.status(500).json({
                success: false,
                error: '上传到区块链失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 验证区块链记录
     */
    async verifyBlockchainRecord(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/blockchain/verify/:transactionId',
                status: '200'
            });
            const { transactionId } = req.params;
            if (!transactionId) {
                res.status(400).json({
                    success: false,
                    error: '缺少交易ID',
                    code: 'MISSING_TRANSACTION_ID'
                });
                return;
            }
            const result = await this.blockchainService.verifyBlockchainRecord(transactionId);
            res.json({
                success: true,
                data: result
            });
        }
        catch (error) {
            logger_1.logger.error('验证区块链记录失败:', error);
            res.status(500).json({
                success: false,
                error: '验证区块链记录失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 批量上传溯源数据到区块链（仅限管理员）
     */
    async batchUploadToBlockchain(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/blockchain/batch-upload',
                status: '200'
            });
            const { limit } = req.query;
            const parsedLimit = limit ? parseInt(limit, 10) : 10;
            // 权限检查
            if (req.user.role !== 'admin' && req.user.role !== 'producer') {
                res.status(403).json({
                    success: false,
                    error: '没有权限执行批量上链操作',
                    code: 'PERMISSION_DENIED'
                });
                return;
            }
            const result = await this.blockchainService.batchUploadToBlockchain(parsedLimit);
            res.json({
                success: true,
                data: result
            });
        }
        catch (error) {
            logger_1.logger.error('批量上传到区块链失败:', error);
            res.status(500).json({
                success: false,
                error: '批量上传到区块链失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
}
exports.BlockchainController = BlockchainController;
exports.default = new BlockchainController(blockchain_service_1.default);
