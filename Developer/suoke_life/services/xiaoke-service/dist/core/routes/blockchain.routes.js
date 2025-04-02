"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = default_1;
const express_1 = require("express");
const blockchain_controller_1 = __importDefault(require("../../controllers/blockchain.controller"));
const auth_middleware_1 = require("../middleware/auth.middleware");
/**
 * 区块链路由
 * 处理与区块链集成相关的HTTP路由
 */
function default_1(io) {
    const router = (0, express_1.Router)();
    // 为Websocket实时通知设置响应拦截器中间件
    const captureResponseData = (req, res, next) => {
        const originalJson = res.json;
        res.json = function (data) {
            res.locals.responseData = data;
            return originalJson.call(this, data);
        };
        next();
    };
    /**
     * @route   POST /api/v1/blockchain/upload
     * @desc    上传溯源数据到区块链
     * @access  Private (Admin, Producer)
     */
    router.post('/upload', (0, auth_middleware_1.auth)(['admin', 'producer']), captureResponseData, async (req, res) => {
        await blockchain_controller_1.default.uploadToBlockchain(req, res);
        // 通知上链成功
        const responseData = res.locals.responseData;
        if (responseData && responseData.success) {
            io.emit('blockchain:upload_success', {
                traceabilityId: responseData.data.traceabilityId,
                transactionId: responseData.data.transactionId,
                timestamp: new Date().toISOString()
            });
            // 通知管理员
            io.to('admin').emit('blockchain:new_record', {
                traceabilityId: responseData.data.traceabilityId,
                transactionId: responseData.data.transactionId,
                blockNumber: responseData.data.blockNumber,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   GET /api/v1/blockchain/verify/:transactionId
     * @desc    验证区块链记录
     * @access  Public
     */
    router.get('/verify/:transactionId', captureResponseData, async (req, res) => {
        await blockchain_controller_1.default.verifyBlockchainRecord(req, res);
        // 记录验证活动
        const responseData = res.locals.responseData;
        if (responseData && responseData.success) {
            io.emit('blockchain:verification', {
                transactionId: req.params.transactionId,
                verified: responseData.data.verified,
                traceabilityId: responseData.data.traceabilityId,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   POST /api/v1/blockchain/batch-upload
     * @desc    批量上传溯源数据到区块链
     * @access  Private (Admin)
     */
    router.post('/batch-upload', (0, auth_middleware_1.auth)(['admin']), captureResponseData, async (req, res) => {
        await blockchain_controller_1.default.batchUploadToBlockchain(req, res);
        // 通知批量上链结果
        const responseData = res.locals.responseData;
        if (responseData && responseData.success) {
            io.to('admin').emit('blockchain:batch_upload_completed', {
                processed: responseData.data.processed,
                succeeded: responseData.data.succeeded,
                failed: responseData.data.failed,
                timestamp: new Date().toISOString()
            });
        }
    });
    return router;
}
