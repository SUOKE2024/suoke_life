import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import productService, { ProductService } from '../services/product/product.service';
import { AuthenticatedRequest } from '../core/middleware/auth.middleware';
import { httpRequestsTotal } from '../core/metrics';

/**
 * 产品控制器
 * 处理与产品相关的HTTP请求
 */
export class ProductController {
  private productService: ProductService;

  constructor(productService: ProductService) {
    this.productService = productService;
  }

  /**
   * 获取产品列表
   */
  async getProducts(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/products', 
        status: '200' 
      });

      const {
        category,
        query,
        sort,
        limit = '20',
        page = '1',
        includeOutOfStock = 'false'
      } = req.query;
      
      const skip = (parseInt(page as string, 10) - 1) * parseInt(limit as string, 10);
      
      const result = await this.productService.getProducts({
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
      logger.error('获取产品列表失败:', error);
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
  async getProductById(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
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
    } catch (error) {
      logger.error('获取产品详情失败:', error);
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
  async getProductsByConstitution(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/products/constitution/:type', 
        status: '200' 
      });

      const { type } = req.params;
      const { limit = '10' } = req.query;
      
      const products = await this.productService.getProductsByConstitution(
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
      logger.error('获取体质推荐产品失败:', error);
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
  async getProductsBySolarTerm(req: Request, res: Response): Promise<void> {
    try {
      // 追踪请求指标
      httpRequestsTotal.inc({ 
        method: req.method, 
        path: '/api/v1/products/solar-term/:term', 
        status: '200' 
      });

      const { term } = req.params;
      const { limit = '10' } = req.query;
      
      const products = await this.productService.getProductsBySolarTerm(
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
      logger.error('获取节气推荐产品失败:', error);
      res.status(500).json({
        success: false,
        error: '获取节气推荐产品失败',
        message: error instanceof Error ? error.message : '未知错误'
      });
    }
  }
}

export default new ProductController(productService); 