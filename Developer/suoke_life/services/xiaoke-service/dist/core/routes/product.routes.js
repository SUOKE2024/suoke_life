"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const product_service_1 = __importDefault(require("../../services/product/product.service"));
const error_middleware_1 = require("../middleware/error.middleware");
// 创建路由
const createProductRoutes = (io) => {
    const router = express_1.default.Router();
    /**
     * @route   GET /api/v1/products
     * @desc    获取产品列表
     * @access  Public
     */
    router.get('/', async (req, res, next) => {
        try {
            const { category, query, sort, limit = '20', page = '1', includeOutOfStock = 'false' } = req.query;
            const skip = (parseInt(page, 10) - 1) * parseInt(limit, 10);
            const result = await product_service_1.default.getProducts({
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
            next(error);
        }
    });
    /**
     * @route   GET /api/v1/products/:id
     * @desc    获取产品详情
     * @access  Public
     */
    router.get('/:id', async (req, res, next) => {
        try {
            const { id } = req.params;
            const product = await product_service_1.default.getProductById(id);
            if (!product) {
                throw new error_middleware_1.ApiError(404, '产品不存在', 'PRODUCT_NOT_FOUND');
            }
            res.json({
                success: true,
                data: product
            });
        }
        catch (error) {
            next(error);
        }
    });
    /**
     * @route   GET /api/v1/products/constitution/:type
     * @desc    根据体质获取推荐产品
     * @access  Public
     */
    router.get('/constitution/:type', async (req, res, next) => {
        try {
            const { type } = req.params;
            const { limit = '10' } = req.query;
            const products = await product_service_1.default.getProductsByConstitution(type, parseInt(limit, 10));
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
            next(error);
        }
    });
    /**
     * @route   GET /api/v1/products/solar-term/:term
     * @desc    根据节气获取推荐产品
     * @access  Public
     */
    router.get('/solar-term/:term', async (req, res, next) => {
        try {
            const { term } = req.params;
            const { limit = '10' } = req.query;
            const products = await product_service_1.default.getProductsBySolarTerm(term, parseInt(limit, 10));
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
            next(error);
        }
    });
    return router;
};
exports.default = createProductRoutes;
