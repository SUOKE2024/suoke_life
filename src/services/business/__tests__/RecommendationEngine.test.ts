/**
 * 推荐引擎单元测试
 */

import { Product } from '../../../types/business';
import {
    createRecommendationEngine,
    RecommendationEngine,
    RecommendationModelType
} from '../RecommendationEngine';

// 模拟服务
const mockProductService = {
  getProductById: jest.fn(),
  findProductsByFeatures: jest.fn(),
  areSimilarProducts: jest.fn()
};

const mockCustomerService = {
  getCustomerById: jest.fn(),
  getRecentProductViews: jest.fn(),
  getCustomerPurchases: jest.fn(),
  findSimilarCustomers: jest.fn(),
  updateRecommendations: jest.fn()
};

const mockTcmKnowledgeService = {
  getConstitutionProductMatch: jest.fn(),
  getConstitutionProductMatchScore: jest.fn(),
  getSuitableProductsForConstitution: jest.fn()
};

// 测试数据
const mockProducts: Product[] = [
  {
    id: 'prod-1',
    name: '冬虫夏草胶囊',
    description: '提高免疫力，补肺益肾',
    price: 299.99,
    category: 'tcm_formula',
    imageUrl: 'https://example.com/images/dongchongxiacao.jpg',
    inStock: true,
    rating: 4.8,
    tags: ['补肾', '益肺', '增强免疫力', '冬季'],
    details: {
      usage: '每日2次，每次2粒',
      ingredients: ['冬虫夏草提取物', '蜂蜜', '人参提取物']
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-06-01T00:00:00Z'
  },
  {
    id: 'prod-2',
    name: '智能脉诊仪',
    description: '高精度脉象检测设备，配合APP使用',
    price: 1299.99,
    category: 'smart_device',
    imageUrl: 'https://example.com/images/pulse-device.jpg',
    inStock: true,
    rating: 4.5,
    tags: ['设备', '脉诊', '智能', '便携'],
    details: {
      battery: '锂电池，续航30天',
      connectivity: 'Bluetooth 5.0',
      compatibility: 'iOS 14+, Android 10+'
    },
    createdAt: '2025-02-15T00:00:00Z',
    updatedAt: '2025-05-20T00:00:00Z'
  },
  {
    id: 'prod-3',
    name: '护肝茶饮',
    description: '改善肝功能，促进新陈代谢',
    price: 89.99,
    category: 'tcm_formula',
    imageUrl: 'https://example.com/images/liver-tea.jpg',
    inStock: true,
    rating: 4.3,
    tags: ['护肝', '排毒', '茶饮', '春季'],
    details: {
      usage: '每日1次，每次1袋',
      ingredients: ['决明子', '菊花', '枸杞', '绿茶']
    },
    createdAt: '2025-03-10T00:00:00Z',
    updatedAt: '2025-04-15T00:00:00Z'
  }
];

// 模拟客户数据
const mockCustomer = {
  id: 'customer-123',
  healthProfile: {
    tcmConstitution: '阴虚体质',
    age: 35,
    gender: '男'
  },
  preferences: {
    categories: ['tcm_formula', 'nutrition']
  }
};

const mockPurchaseHistory = [
  { productId: 'prod-1', amount: 299.99, purchaseDate: '2025-05-01T00:00:00Z' }
];

const mockRecentViews = ['prod-2', 'prod-3'];

describe('推荐引擎测试', () => {
  let recommendationEngine: RecommendationEngine;
  
  beforeEach(() => {
    // 重置所有模拟函数
    jest.clearAllMocks();
    
    // 设置基础模拟数据
    mockCustomerService.getCustomerById.mockResolvedValue(mockCustomer);
    mockCustomerService.getCustomerPurchases.mockResolvedValue(mockPurchaseHistory);
    mockCustomerService.getRecentProductViews.mockResolvedValue(mockRecentViews);
    
    // 创建引擎实例
    recommendationEngine = createRecommendationEngine(
      RecommendationModelType.HYBRID,
      mockProductService,
      mockCustomerService,
      mockTcmKnowledgeService
    );
  });
  
  describe('生成推荐功能', () => {
    it('应该使用混合策略生成推荐', async () => {
      // 设置模拟
      mockCustomerService.findSimilarCustomers.mockResolvedValue(['customer-456', 'customer-789']);
      mockCustomerService.getCustomerPurchases.mockImplementation((id) => {
        if (id === 'customer-123') return Promise.resolve(mockPurchaseHistory);
        return Promise.resolve([{ productId: 'prod-3', amount: 89.99 }]);
      });
      
      mockProductService.findProductsByFeatures.mockResolvedValue([mockProducts[2]]);
      mockTcmKnowledgeService.getSuitableProductsForConstitution.mockResolvedValue([mockProducts[0]]);
      
      mockProductService.getProductById.mockImplementation((id) => {
        return Promise.resolve(mockProducts.find(p => p.id === id) || null);
      });
      
      // 执行测试
      const result = await recommendationEngine.generateRecommendations({ id: 'customer-123' }, 3);
      
      // 验证结果
      expect(result.length).toBeGreaterThan(0);
      expect(mockCustomerService.getCustomerById).toHaveBeenCalledWith('customer-123');
      expect(mockCustomerService.getCustomerPurchases).toHaveBeenCalled();
      expect(mockCustomerService.getRecentProductViews).toHaveBeenCalled();
    });
    
    it('应该在发生错误时返回空数组', async () => {
      // 设置模拟
      mockCustomerService.getCustomerById.mockRejectedValue(new Error('获取客户数据失败'));
      
      // 执行测试
      const result = await recommendationEngine.generateRecommendations({ id: 'customer-123' });
      
      // 验证结果
      expect(result).toEqual([]);
      expect(mockCustomerService.getCustomerById).toHaveBeenCalled();
    });
  });
  
  describe('个性化排序功能', () => {
    it('应该基于相关性分数对产品进行排序', async () => {
      // 设置模拟
      mockProductService.getProductById.mockImplementation((id) => {
        return Promise.resolve(mockProducts.find(p => p.id === id) || null);
      });
      
      // 模拟不同的匹配分数
      mockTcmKnowledgeService.getConstitutionProductMatchScore.mockImplementation((constitution, prodId) => {
        if (prodId === 'prod-1') return Promise.resolve(0.9);
        if (prodId === 'prod-3') return Promise.resolve(0.5);
        return Promise.resolve(0.1);
      });
      
      // 执行测试
      const result = await recommendationEngine.getPersonalizedRanking(
        'customer-123', 
        ['prod-2', 'prod-1', 'prod-3']
      );
      
      // 验证结果 - 应该按匹配分数从高到低排序
      expect(result[0]).toBe('prod-1'); // 最高分
      expect(result).toHaveLength(3);
      expect(mockProductService.getProductById).toHaveBeenCalledTimes(3);
    });
    
    it('出错时应该返回原始产品顺序', async () => {
      // 设置模拟
      mockProductService.getProductById.mockRejectedValue(new Error('获取产品数据失败'));
      
      const originalOrder = ['prod-1', 'prod-2', 'prod-3'];
      
      // 执行测试
      const result = await recommendationEngine.getPersonalizedRanking('customer-123', originalOrder);
      
      // 验证结果
      expect(result).toEqual(originalOrder);
    });
  });
  
  describe('推荐解释功能', () => {
    it('应该基于中医体质提供推荐解释', async () => {
      // 设置模拟
      mockProductService.getProductById.mockResolvedValue(mockProducts[0]);
      mockTcmKnowledgeService.getConstitutionProductMatch.mockResolvedValue(
        '冬虫夏草具有补肾益肺的功效，适合阴虚体质人群调理。'
      );
      
      // 执行测试
      const result = await recommendationEngine.explainRecommendation('customer-123', 'prod-1');
      
      // 验证结果
      expect(result).toContain('阴虚体质');
      expect(result).toContain('冬虫夏草具有补肾益肺的功效');
      expect(mockProductService.getProductById).toHaveBeenCalledWith('prod-1');
      expect(mockTcmKnowledgeService.getConstitutionProductMatch).toHaveBeenCalled();
    });
    
    it('应该基于季节因素提供推荐解释', async () => {
      // 设置模拟
      const winterProduct = {
        ...mockProducts[0],
        tags: ['补肾', '益肺', '增强免疫力', '冬季']
      };
      
      mockProductService.getProductById.mockResolvedValue(winterProduct);
      mockTcmKnowledgeService.getConstitutionProductMatch.mockResolvedValue('');
      
      // 模拟当前是冬季
      const originalDateNow = Date.now;
      Date.now = jest.fn(() => new Date('2025-12-15T12:00:00Z').getTime());
      
      // 执行测试
      const result = await recommendationEngine.explainRecommendation('customer-123', 'prod-1');
      
      // 恢复原始Date.now
      Date.now = originalDateNow;
      
      // 验证结果
      expect(result).toContain('冬季');
      expect(mockProductService.getProductById).toHaveBeenCalledWith('prod-1');
    });
    
    it('当产品未找到时应该返回适当消息', async () => {
      // 设置模拟
      mockProductService.getProductById.mockResolvedValue(null);
      
      // 执行测试
      const result = await recommendationEngine.explainRecommendation('customer-123', 'non-existent');
      
      // 验证结果
      expect(result).toBe('无法找到该产品');
      expect(mockProductService.getProductById).toHaveBeenCalledWith('non-existent');
    });
  });
  
  describe('刷新推荐功能', () => {
    it('应该获取最新客户数据并更新推荐', async () => {
      // 设置模拟
      mockProductService.getProductById.mockImplementation((id) => {
        return Promise.resolve(mockProducts.find(p => p.id === id) || null);
      });
      
      // 执行测试
      await recommendationEngine.refreshRecommendations('customer-123');
      
      // 验证结果
      expect(mockCustomerService.getCustomerById).toHaveBeenCalledWith('customer-123');
      expect(mockCustomerService.updateRecommendations).toHaveBeenCalledWith(
        'customer-123',
        expect.any(Array)
      );
    });
    
    it('获取客户数据失败时应该抛出错误', async () => {
      // 设置模拟
      mockCustomerService.getCustomerById.mockRejectedValue(new Error('获取客户数据失败'));
      
      // 执行测试并验证
      await expect(recommendationEngine.refreshRecommendations('customer-123'))
        .rejects.toThrow('刷新推荐失败');
    });
  });
  
  describe('基于中医知识的推荐', () => {
    it('应该为特定体质用户推荐合适的产品', async () => {
      // 设置测试数据 - 阴虚体质
      const yinDeficiencyCustomer = {
        ...mockCustomer,
        healthProfile: {
          ...mockCustomer.healthProfile,
          tcmConstitution: '阴虚体质'
        }
      };
      
      // 适合阴虚体质的产品
      const suitableProducts = [mockProducts[0], mockProducts[2]];
      
      // 设置模拟
      mockCustomerService.getCustomerById.mockResolvedValue(yinDeficiencyCustomer);
      mockTcmKnowledgeService.getSuitableProductsForConstitution.mockResolvedValue(suitableProducts);
      mockProductService.getProductById.mockImplementation((id) => {
        return Promise.resolve(mockProducts.find(p => p.id === id) || null);
      });
      
      // 创建专注于中医知识的引擎
      const tcmEngine = createRecommendationEngine(
        RecommendationModelType.TCM_KNOWLEDGE_BASED,
        mockProductService,
        mockCustomerService,
        mockTcmKnowledgeService
      );
      
      // 执行测试
      const result = await tcmEngine.generateRecommendations({ id: 'customer-123' }, 2);
      
      // 验证结果
      expect(result.length).toBeGreaterThan(0);
      expect(mockTcmKnowledgeService.getSuitableProductsForConstitution).toHaveBeenCalledWith(
        '阴虚体质',
        expect.any(String) // 季节
      );
    });
  });
}); 