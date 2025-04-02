"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductController = void 0;
const logger_1 = require("../utils/logger");
const product_service_1 = __importDefault(require("../services/product/product.service"));
const metrics_1 = require("../core/metrics");
/**
 * 产品控制器
 * 处理与产品相关的HTTP请求
 */
class ProductController {
    constructor(productService) {
        this.productService = productService;
    }
    /**
     * 获取产品列表
     */
    async getProducts(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/products',
                status: '200'
            });
            const { category, query, sort, limit = '20', page = '1', includeOutOfStock = 'false' } = req.query;
            const skip = (parseInt(page, 10) - 1) * parseInt(limit, 10);
            const result = await this.productService.getProducts({
                category: category,
                query: query,
                sort: sort,
                limit: parseInt(limit, 10),
                skip,
                includeOutOfStock: includeOutOfStock === 'true'
            });
            res.json({
                success: true,
                data: {
                    products: result.products,
                    pagination: {
                        total: result.total,
                        page: parseInt(page, 10),
                        limit: parseInt(limit, 10),
                        pages: Math.ceil(result.total / parseInt(limit, 10))
                    }
                }
            });
        }
        catch (error) {
            logger_1.logger.error('获取产品列表失败:', error);
            res.status(500).json({
                success: false,
                error: '获取产品列表失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取产品详情
     */
    async getProductById(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/products/:id',
                status: '200'
            });
            const { id } = req.params;
            const product = await this.productService.getProductById(id);
            if (!product) {
                res.status(404).json({
                    success: false,
                    error: '产品不存在',
                    code: 'PRODUCT_NOT_FOUND'
                });
                return;
            }
            res.json({
                success: true,
                data: product
            });
        }
        catch (error) {
            logger_1.logger.error('获取产品详情失败:', error);
            res.status(500).json({
                success: false,
                error: '获取产品详情失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 根据体质获取推荐产品
     */
    async getProductsByConstitution(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/products/constitution/:type',
                status: '200'
            });
            const { type } = req.params;
            const { limit = '10' } = req.query;
            const products = await this.productService.getProductsByConstitution(type, parseInt(limit, 10));
            res.json({
                success: true,
                data: {
                    constitution: type,
                    products,
                    count: products.length
                }
            });
        }
        catch (error) {
            logger_1.logger.error('获取体质推荐产品失败:', error);
            res.status(500).json({
                success: false,
                error: '获取体质推荐产品失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 根据节气获取推荐产品
     */
    async getProductsBySolarTerm(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/products/solar-term/:term',
                status: '200'
            });
            const { term } = req.params;
            const { limit = '10' } = req.query;
            const products = await this.productService.getProductsBySolarTerm(term, parseInt(limit, 10));
            res.json({
                success: true,
                data: {
                    solarTerm: term,
                    products,
                    count: products.length
                }
            });
        }
        catch (error) {
            logger_1.logger.error('获取节气推荐产品失败:', error);
            res.status(500).json({
                success: false,
                error: '获取节气推荐产品失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
}
exports.ProductController = ProductController;
exports.default = new ProductController(product_service_1.default);
