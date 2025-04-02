import mongoose from 'mongoose';
import { logger } from '../../utils/logger';
import { ProductInfo } from '../../core/agent/types';
import { getCache, setCache } from '../../core/cache';
import { ProductModel } from '../../models/product.model';
import { productQueryCounter, productInventoryGauge } from '../../core/metrics';

// 缓存配置
const PRODUCT_CACHE_TTL = parseInt(process.env.PRODUCT_CACHE_TTL || '86400', 10); // 默认24小时

/**
 * 产品服务类
 * 负责管理产品信息、库存和属性
 */
export class ProductService {
  /**
   * 获取产品详情
   */
  async getProductById(productId: string): Promise<ProductInfo | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `product:${productId}`;
      const cachedProduct = await getCache<ProductInfo>(cacheKey);
      
      if (cachedProduct) {
        logger.debug(`从缓存获取产品信息: ${productId}`);
        productQueryCounter.inc({ product_type: cachedProduct.category, source: 'cache', result: 'success' });
        return cachedProduct;
      }
      
      // 从数据库获取
      const product = await ProductModel.findById(productId).lean();
      
      if (!product) {
        logger.debug(`产品不存在: ${productId}`);
        productQueryCounter.inc({ product_type: 'unknown', source: 'database', result: 'not_found' });
        return null;
      }
      
      // 转换为ProductInfo类型
      const productInfo: ProductInfo = {
        id: product._id.toString(),
        name: product.name,
        description: product.description,
        category: product.category,
        price: product.price,
        unit: product.unit,
        stock: product.stock,
        images: product.images,
        producer: product.producer,
        certifications: product.certifications,
        nutritionFacts: product.nutritionFacts,
        tcmProperties: product.tcmProperties,
        harvestDate: product.harvestDate,
        expiryDate: product.expiryDate,
        storageConditions: product.storageConditions,
        seasonality: product.seasonality,
        traceabilityId: product.traceabilityId,
        blockchainVerified: product.blockchainVerified,
        metadata: product.metadata
      };
      
      // 更新缓存
      await setCache(cacheKey, productInfo, PRODUCT_CACHE_TTL);
      
      // 更新指标
      productQueryCounter.inc({ product_type: product.category, source: 'database', result: 'success' });
      productInventoryGauge.set({ product_id: product._id.toString(), product_name: product.name, category: product.category }, product.stock);
      
      return productInfo;
    } catch (error) {
      logger.error(`获取产品信息失败:`, error);
      productQueryCounter.inc({ product_type: 'unknown', source: 'database', result: 'error' });
      throw error;
    }
  }
  
  /**
   * 获取产品列表
   */
  async getProducts(options: {
    category?: string;
    query?: string;
    sort?: string;
    limit?: number;
    skip?: number;
    includeOutOfStock?: boolean;
  }): Promise<{ products: ProductInfo[]; total: number }> {
    try {
      const {
        category,
        query,
        sort = 'createdAt_desc',
        limit = 20,
        skip = 0,
        includeOutOfStock = false
      } = options;
      
      // 构建查询条件
      const filter: any = {};
      
      if (category) {
        filter.category = category;
      }
      
      if (query) {
        filter.$or = [
          { name: { $regex: query, $options: 'i' } },
          { description: { $regex: query, $options: 'i' } }
        ];
      }
      
      if (!includeOutOfStock) {
        filter.stock = { $gt: 0 };
      }
      
      // 处理排序
      const [sortField, sortOrder] = sort.split('_');
      const sortOptions: any = {};
      sortOptions[sortField] = sortOrder === 'desc' ? -1 : 1;
      
      // 执行查询
      const total = await ProductModel.countDocuments(filter);
      
      const products = await ProductModel.find(filter)
        .sort(sortOptions)
        .skip(skip)
        .limit(limit)
        .lean();
      
      // 转换结果
      const productInfos = products.map(product => ({
        id: product._id.toString(),
        name: product.name,
        description: product.description,
        category: product.category,
        price: product.price,
        unit: product.unit,
        stock: product.stock,
        images: product.images,
        producer: product.producer,
        certifications: product.certifications,
        nutritionFacts: product.nutritionFacts,
        tcmProperties: product.tcmProperties,
        harvestDate: product.harvestDate,
        expiryDate: product.expiryDate,
        storageConditions: product.storageConditions,
        seasonality: product.seasonality,
        traceabilityId: product.traceabilityId,
        blockchainVerified: product.blockchainVerified,
        metadata: product.metadata
      }));
      
      // 更新指标
      productQueryCounter.inc({ 
        product_type: category || 'all', 
        source: 'database', 
        result: productInfos.length > 0 ? 'success' : 'empty' 
      });
      
      return { products: productInfos, total };
    } catch (error) {
      logger.error(`获取产品列表失败:`, error);
      productQueryCounter.inc({ product_type: 'all', source: 'database', result: 'error' });
      throw error;
    }
  }
  
  /**
   * 根据体质推荐产品
   */
  async getProductsByConstitution(constitution: string, limit: number = 10): Promise<ProductInfo[]> {
    try {
      // 缓存键
      const cacheKey = `products:constitution:${constitution}:limit:${limit}`;
      
      // 尝试从缓存获取
      const cachedProducts = await getCache<ProductInfo[]>(cacheKey);
      if (cachedProducts) {
        productQueryCounter.inc({ product_type: 'constitution', source: 'cache', result: 'success' });
        return cachedProducts;
      }
      
      // 根据体质查询符合的产品
      // 这里使用TCM属性匹配体质特性
      const constitutionMapping: Record<string, any> = {
        '气虚质': { 'tcmProperties.nature': '温', 'tcmProperties.taste': '甘' },
        '阳虚质': { 'tcmProperties.nature': '热', 'tcmProperties.taste': '辛' },
        '阴虚质': { 'tcmProperties.nature': '寒', 'tcmProperties.taste': '酸' },
        '痰湿质': { 'tcmProperties.nature': '温', 'tcmProperties.taste': '苦' },
        '湿热质': { 'tcmProperties.nature': '寒', 'tcmProperties.taste': '苦' },
        '血瘀质': { 'tcmProperties.nature': '温', 'tcmProperties.taste': '辛' },
        '气郁质': { 'tcmProperties.nature': '温', 'tcmProperties.taste': '辛' },
        '特禀质': { 'tcmProperties.nature': '平', 'tcmProperties.taste': '甘' },
        '平和质': { 'tcmProperties.nature': '平', 'tcmProperties.taste': '甘' }
      };
      
      const filter = constitutionMapping[constitution] || {};
      filter.stock = { $gt: 0 };
      
      const products = await ProductModel.find(filter)
        .limit(limit)
        .lean();
      
      // 转换结果
      const productInfos = products.map(product => ({
        id: product._id.toString(),
        name: product.name,
        description: product.description,
        category: product.category,
        price: product.price,
        unit: product.unit,
        stock: product.stock,
        images: product.images,
        producer: product.producer,
        certifications: product.certifications,
        nutritionFacts: product.nutritionFacts,
        tcmProperties: product.tcmProperties,
        harvestDate: product.harvestDate,
        expiryDate: product.expiryDate,
        storageConditions: product.storageConditions,
        seasonality: product.seasonality,
        traceabilityId: product.traceabilityId,
        blockchainVerified: product.blockchainVerified,
        metadata: product.metadata
      }));
      
      // 更新缓存
      await setCache(cacheKey, productInfos, PRODUCT_CACHE_TTL);
      
      // 更新指标
      productQueryCounter.inc({ 
        product_type: 'constitution', 
        source: 'database', 
        result: productInfos.length > 0 ? 'success' : 'empty' 
      });
      
      return productInfos;
    } catch (error) {
      logger.error(`获取体质相关产品失败:`, error);
      productQueryCounter.inc({ product_type: 'constitution', source: 'database', result: 'error' });
      throw error;
    }
  }
  
  /**
   * 根据节气获取产品
   */
  async getProductsBySolarTerm(solarTerm: string, limit: number = 10): Promise<ProductInfo[]> {
    try {
      // 缓存键
      const cacheKey = `products:solarTerm:${solarTerm}:limit:${limit}`;
      
      // 尝试从缓存获取
      const cachedProducts = await getCache<ProductInfo[]>(cacheKey);
      if (cachedProducts) {
        productQueryCounter.inc({ product_type: 'solar_term', source: 'cache', result: 'success' });
        return cachedProducts;
      }
      
      // 根据节气查询符合的产品
      const filter: any = {
        'metadata.solarTerms': solarTerm,
        stock: { $gt: 0 }
      };
      
      const products = await ProductModel.find(filter)
        .limit(limit)
        .lean();
      
      // 转换结果
      const productInfos = products.map(product => ({
        id: product._id.toString(),
        name: product.name,
        description: product.description,
        category: product.category,
        price: product.price,
        unit: product.unit,
        stock: product.stock,
        images: product.images,
        producer: product.producer,
        certifications: product.certifications,
        nutritionFacts: product.nutritionFacts,
        tcmProperties: product.tcmProperties,
        harvestDate: product.harvestDate,
        expiryDate: product.expiryDate,
        storageConditions: product.storageConditions,
        seasonality: product.seasonality,
        traceabilityId: product.traceabilityId,
        blockchainVerified: product.blockchainVerified,
        metadata: product.metadata
      }));
      
      // 更新缓存
      await setCache(cacheKey, productInfos, PRODUCT_CACHE_TTL);
      
      // 更新指标
      productQueryCounter.inc({ 
        product_type: 'solar_term', 
        source: 'database', 
        result: productInfos.length > 0 ? 'success' : 'empty' 
      });
      
      return productInfos;
    } catch (error) {
      logger.error(`获取节气相关产品失败:`, error);
      productQueryCounter.inc({ product_type: 'solar_term', source: 'database', result: 'error' });
      throw error;
    }
  }
}

export default new ProductService();