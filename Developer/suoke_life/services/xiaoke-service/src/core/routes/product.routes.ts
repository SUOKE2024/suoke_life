import express from 'express';
import { Server } from 'socket.io';
import productService from '../../services/product/product.service';
import { logger } from '../../utils/logger';
import { ApiError } from '../middleware/error.middleware';

// 创建路由
const createProductRoutes = (io: Server) => {
  const router = express.Router();
  
  /**
   * @route   GET /api/v1/products
   * @desc    获取产品列表
   * @access  Public
   */
  router.get('/', async (req, res, next) => {
    try {
      const {
        category,
        query,
        sort,
        limit = '20',
        page = '1',
        includeOutOfStock = 'false'
      } = req.query;
      
      const skip = (parseInt(page as string, 10) - 1) * parseInt(limit as string, 10);
      
      const result = await productService.getProducts({
        category: category as string,
        query: query as string,
        sort: sort as string,
        limit: parseInt(limit as string, 10),
        skip,
        includeOutOfStock: (includeOutOfStock as string) === 'true'
      });
      
      res.json({
        success: true,
        data: {
          products: result.products,
          pagination: {
            total: result.total,
            page: parseInt(page as string, 10),
            limit: parseInt(limit as string, 10),
            pages: Math.ceil(result.total / parseInt(limit as string, 10))
          }
        }
      });
    } catch (error) {
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
      
      const product = await productService.getProductById(id);
      
      if (!product) {
        throw new ApiError(404, '产品不存在', 'PRODUCT_NOT_FOUND');
      }
      
      res.json({
        success: true,
        data: product
      });
    } catch (error) {
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
      
      const products = await productService.getProductsByConstitution(
        type,
        parseInt(limit as string, 10)
      );
      
      res.json({
        success: true,
        data: {
          constitution: type,
          products,
          count: products.length
        }
      });
    } catch (error) {
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
      
      const products = await productService.getProductsBySolarTerm(
        term,
        parseInt(limit as string, 10)
      );
      
      res.json({
        success: true,
        data: {
          solarTerm: term,
          products,
          count: products.length
        }
      });
    } catch (error) {
      next(error);
    }
  });
  
  return router;
};

export default createProductRoutes; 