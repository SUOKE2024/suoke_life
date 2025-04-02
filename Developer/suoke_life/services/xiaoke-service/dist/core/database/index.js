"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.closeDatabase = exports.connectToDatabase = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const logger_1 = require("../../utils/logger");
/**
 * 连接MongoDB数据库
 */
const connectToDatabase = async () => {
    try {
        // 获取环境变量
        const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/xiaoke-service';
        const options = {
        // MongoDB连接选项
        };
        if (process.env.MONGODB_USER && process.env.MONGODB_PASSWORD) {
            Object.assign(options, {
                user: process.env.MONGODB_USER,
                pass: process.env.MONGODB_PASSWORD,
            });
        }
        // 设置连接事件监听
        mongoose_1.default.connection.on('connected', () => {
            logger_1.logger.info('MongoDB连接成功');
        });
        mongoose_1.default.connection.on('error', (err) => {
            logger_1.logger.error('MongoDB连接错误:', err);
        });
        mongoose_1.default.connection.on('disconnected', () => {
            logger_1.logger.warn('MongoDB连接断开');
        });
        // 连接到数据库
        await mongoose_1.default.connect(uri, options);
        return mongoose_1.default;
    }
    catch (error) {
        logger_1.logger.error('MongoDB连接失败:', error);
        throw error;
    }
};
exports.connectToDatabase = connectToDatabase;
/**
 * 关闭数据库连接
 */
const closeDatabase = async () => {
    try {
        await mongoose_1.default.connection.close();
        logger_1.logger.info('MongoDB连接已关闭');
    }
    catch (error) {
        logger_1.logger.error('关闭MongoDB连接时出错:', error);
        throw error;
    }
};
exports.closeDatabase = closeDatabase;
exports.default = {
    connect: exports.connectToDatabase,
    close: exports.closeDatabase,
};
