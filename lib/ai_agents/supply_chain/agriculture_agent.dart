import '../models/ai_agent.dart';
import '../core/agent_microkernel.dart';
import '../integration/service_integration.dart';
import '../core/security_privacy_framework.dart';

/// 农产品类型
enum AgricultureProductType {
  /// 水果
  fruit,
  
  /// 蔬菜
  vegetable,
  
  /// 粮食
  grain,
  
  /// 肉类
  meat,
  
  /// 水产
  seafood,
  
  /// 禽蛋
  poultry,
  
  /// 调味品
  seasoning,
  
  /// 坚果
  nut,
  
  /// 中药材
  medicinalHerb,
  
  /// 其他
  other,
}

/// 农产品产地
enum AgricultureOrigin {
  /// 东北
  northeast,
  
  /// 华北
  northChina,
  
  /// 华东
  eastChina,
  
  /// 华中
  centralChina,
  
  /// 华南
  southChina,
  
  /// 西南
  southwest,
  
  /// 西北
  northwest,
  
  /// 进口
  imported,
}

/// 农产品等级
enum AgricultureGrade {
  /// 特级
  premium,
  
  /// 一级
  firstClass,
  
  /// 二级
  secondClass,
  
  /// 三级
  thirdClass,
}

/// 农产品认证
enum AgricultureCertification {
  /// 有机
  organic,
  
  /// 绿色
  green,
  
  /// 无公害
  pollution_free,
  
  /// 地理标志
  geographical_indication,
}

/// 农产品信息
class AgricultureProduct {
  /// 产品ID
  final String id;
  
  /// 产品名称
  final String name;
  
  /// 产品类型
  final AgricultureProductType type;
  
  /// 产地
  final AgricultureOrigin origin;
  
  /// 等级
  final AgricultureGrade? grade;
  
  /// 认证列表
  final List<AgricultureCertification>? certifications;
  
  /// 价格（人民币，元/kg）
  final double price;
  
  /// 库存量（kg）
  final double stock;
  
  /// 生产日期
  final DateTime productionDate;
  
  /// 保质期（天）
  final int shelfLife;
  
  /// 供应商ID
  final String supplierId;
  
  /// 图片URL列表
  final List<String>? imageUrls;
  
  /// 产品描述
  final String? description;
  
  /// 营养成分
  final Map<String, dynamic>? nutrition;
  
  /// 医药功效（如果适用）
  final List<String>? medicinalEffects;
  
  /// 推荐搭配
  final List<String>? recommendedCombinations;
  
  const AgricultureProduct({
    required this.id,
    required this.name,
    required this.type,
    required this.origin,
    this.grade,
    this.certifications,
    required this.price,
    required this.stock,
    required this.productionDate,
    required this.shelfLife,
    required this.supplierId,
    this.imageUrls,
    this.description,
    this.nutrition,
    this.medicinalEffects,
    this.recommendedCombinations,
  });
}

/// 农产品搜索条件
class AgricultureSearchFilter {
  /// 关键词
  final String? keyword;
  
  /// 产品类型
  final List<AgricultureProductType>? types;
  
  /// 产地
  final List<AgricultureOrigin>? origins;
  
  /// 等级
  final List<AgricultureGrade>? grades;
  
  /// 认证
  final List<AgricultureCertification>? certifications;
  
  /// 价格范围
  final RangeValues? priceRange;
  
  /// 是否有货
  final bool? inStock;
  
  /// 医药功效关键词
  final List<String>? medicinalEffectKeywords;
  
  /// 排序方式
  final AgricultureSortOption? sortBy;
  
  const AgricultureSearchFilter({
    this.keyword,
    this.types,
    this.origins,
    this.grades,
    this.certifications,
    this.priceRange,
    this.inStock,
    this.medicinalEffectKeywords,
    this.sortBy,
  });
}

/// 价格范围
class RangeValues {
  final double start;
  final double end;
  
  const RangeValues(this.start, this.end);
}

/// 农产品排序选项
enum AgricultureSortOption {
  /// 价格从低到高
  priceAsc,
  
  /// 价格从高到低
  priceDesc,
  
  /// 新鲜度
  freshness,
  
  /// 人气度
  popularity,
}

/// 农产品代理接口
abstract class AgricultureAgent {
  /// 搜索农产品
  Future<List<AgricultureProduct>> searchProducts(AgricultureSearchFilter filter);
  
  /// 获取产品详情
  Future<AgricultureProduct?> getProductDetail(String productId);
  
  /// 获取推荐产品
  Future<List<AgricultureProduct>> getRecommendedProducts({
    String? userId,
    String? basedOnProductId,
    AgricultureProductType? type,
  });
  
  /// 获取药食同源推荐
  Future<List<AgricultureProduct>> getMedicinalFoodRecommendations(
    List<String> healthConditions,
  );
  
  /// 获取产品溯源信息
  Future<Map<String, dynamic>> getProductTraceability(String productId);
  
  /// 检查产品库存
  Future<double> checkProductStock(String productId);
  
  /// 获取季节性产品
  Future<List<AgricultureProduct>> getSeasonalProducts();
  
  /// 获取地域特产
  Future<List<AgricultureProduct>> getRegionalSpecialties(AgricultureOrigin origin);
}

/// 农产品代理实现
class AgricultureAgentImpl implements AgricultureAgent {
  final AIAgent _aiAgent;
  final ServiceIntegration _serviceIntegration;
  final AgentMicrokernel _microkernel;
  final SecurityPrivacyFramework _securityFramework;
  
  AgricultureAgentImpl({
    required AIAgent aiAgent,
    required ServiceIntegration serviceIntegration,
    required AgentMicrokernel microkernel,
    required SecurityPrivacyFramework securityFramework,
  }) : _aiAgent = aiAgent,
       _serviceIntegration = serviceIntegration,
       _microkernel = microkernel,
       _securityFramework = securityFramework;
  
  @override
  Future<List<AgricultureProduct>> searchProducts(AgricultureSearchFilter filter) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{};
      
      if (filter.keyword != null) {
        queryParams['keyword'] = filter.keyword;
      }
      
      if (filter.types != null && filter.types!.isNotEmpty) {
        queryParams['types'] = filter.types!.map((t) => t.toString().split('.').last).join(',');
      }
      
      if (filter.origins != null && filter.origins!.isNotEmpty) {
        queryParams['origins'] = filter.origins!.map((o) => o.toString().split('.').last).join(',');
      }
      
      if (filter.grades != null && filter.grades!.isNotEmpty) {
        queryParams['grades'] = filter.grades!.map((g) => g.toString().split('.').last).join(',');
      }
      
      if (filter.certifications != null && filter.certifications!.isNotEmpty) {
        queryParams['certifications'] = filter.certifications!.map((c) => c.toString().split('.').last).join(',');
      }
      
      if (filter.priceRange != null) {
        queryParams['min_price'] = filter.priceRange!.start;
        queryParams['max_price'] = filter.priceRange!.end;
      }
      
      if (filter.inStock != null) {
        queryParams['in_stock'] = filter.inStock;
      }
      
      if (filter.medicinalEffectKeywords != null && filter.medicinalEffectKeywords!.isNotEmpty) {
        queryParams['medicinal_effects'] = filter.medicinalEffectKeywords!.join(',');
      }
      
      if (filter.sortBy != null) {
        queryParams['sort_by'] = filter.sortBy.toString().split('.').last;
      }
      
      // 发送请求到服务
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/search',
        method: 'GET',
        queryParams: queryParams,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final productsData = response.data!['products'] as List<dynamic>;
      final products = productsData.map((data) => _parseProductData(data)).toList();
      
      return products;
    } catch (e) {
      print('Error searching products: $e');
      return [];
    }
  }
  
  @override
  Future<AgricultureProduct?> getProductDetail(String productId) async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/$productId',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return null;
      }
      
      return _parseProductData(response.data!);
    } catch (e) {
      print('Error getting product detail: $e');
      return null;
    }
  }
  
  @override
  Future<List<AgricultureProduct>> getRecommendedProducts({
    String? userId,
    String? basedOnProductId,
    AgricultureProductType? type,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      
      if (userId != null) {
        queryParams['user_id'] = userId;
      }
      
      if (basedOnProductId != null) {
        queryParams['based_on_product_id'] = basedOnProductId;
      }
      
      if (type != null) {
        queryParams['type'] = type.toString().split('.').last;
      }
      
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/recommended',
        method: 'GET',
        queryParams: queryParams,
        userId: userId,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final productsData = response.data!['products'] as List<dynamic>;
      final products = productsData.map((data) => _parseProductData(data)).toList();
      
      return products;
    } catch (e) {
      print('Error getting recommended products: $e');
      return [];
    }
  }
  
  @override
  Future<List<AgricultureProduct>> getMedicinalFoodRecommendations(
    List<String> healthConditions,
  ) async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/medicinal-food',
        method: 'GET',
        queryParams: {
          'health_conditions': healthConditions.join(','),
        },
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final productsData = response.data!['products'] as List<dynamic>;
      final products = productsData.map((data) => _parseProductData(data)).toList();
      
      return products;
    } catch (e) {
      print('Error getting medicinal food recommendations: $e');
      return [];
    }
  }
  
  @override
  Future<Map<String, dynamic>> getProductTraceability(String productId) async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/$productId/traceability',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return {};
      }
      
      return response.data!;
    } catch (e) {
      print('Error getting product traceability: $e');
      return {};
    }
  }
  
  @override
  Future<double> checkProductStock(String productId) async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/$productId/stock',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return 0.0;
      }
      
      return response.data!['stock_level'] as double;
    } catch (e) {
      print('Error checking product stock: $e');
      return 0.0;
    }
  }
  
  @override
  Future<List<AgricultureProduct>> getSeasonalProducts() async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/seasonal',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final productsData = response.data!['products'] as List<dynamic>;
      final products = productsData.map((data) => _parseProductData(data)).toList();
      
      return products;
    } catch (e) {
      print('Error getting seasonal products: $e');
      return [];
    }
  }
  
  @override
  Future<List<AgricultureProduct>> getRegionalSpecialties(AgricultureOrigin origin) async {
    try {
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/agriculture/products/regional',
        method: 'GET',
        queryParams: {
          'origin': origin.toString().split('.').last,
        },
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final productsData = response.data!['products'] as List<dynamic>;
      final products = productsData.map((data) => _parseProductData(data)).toList();
      
      return products;
    } catch (e) {
      print('Error getting regional specialties: $e');
      return [];
    }
  }
  
  /// 解析产品数据
  AgricultureProduct _parseProductData(Map<String, dynamic> data) {
    return AgricultureProduct(
      id: data['id'] as String,
      name: data['name'] as String,
      type: _parseProductType(data['type'] as String),
      origin: _parseOrigin(data['origin'] as String),
      grade: data['grade'] != null ? _parseGrade(data['grade'] as String) : null,
      certifications: data['certifications'] != null
        ? (data['certifications'] as List<dynamic>).map((c) => _parseCertification(c as String)).toList()
        : null,
      price: data['price'] as double,
      stock: data['stock'] as double,
      productionDate: DateTime.parse(data['production_date'] as String),
      shelfLife: data['shelf_life'] as int,
      supplierId: data['supplier_id'] as String,
      imageUrls: data['image_urls'] != null ? (data['image_urls'] as List<dynamic>).cast<String>() : null,
      description: data['description'] as String?,
      nutrition: data['nutrition'] as Map<String, dynamic>?,
      medicinalEffects: data['medicinal_effects'] != null 
        ? (data['medicinal_effects'] as List<dynamic>).cast<String>() 
        : null,
      recommendedCombinations: data['recommended_combinations'] != null 
        ? (data['recommended_combinations'] as List<dynamic>).cast<String>() 
        : null,
    );
  }
  
  /// 解析产品类型
  AgricultureProductType _parseProductType(String typeStr) {
    switch (typeStr.toLowerCase()) {
      case 'fruit':
        return AgricultureProductType.fruit;
      case 'vegetable':
        return AgricultureProductType.vegetable;
      case 'grain':
        return AgricultureProductType.grain;
      case 'meat':
        return AgricultureProductType.meat;
      case 'seafood':
        return AgricultureProductType.seafood;
      case 'poultry':
        return AgricultureProductType.poultry;
      case 'seasoning':
        return AgricultureProductType.seasoning;
      case 'nut':
        return AgricultureProductType.nut;
      case 'medicinalherb':
      case 'medicinal_herb':
        return AgricultureProductType.medicinalHerb;
      default:
        return AgricultureProductType.other;
    }
  }
  
  /// 解析产地
  AgricultureOrigin _parseOrigin(String originStr) {
    switch (originStr.toLowerCase()) {
      case 'northeast':
        return AgricultureOrigin.northeast;
      case 'northchina':
      case 'north_china':
        return AgricultureOrigin.northChina;
      case 'eastchina':
      case 'east_china':
        return AgricultureOrigin.eastChina;
      case 'centralchina':
      case 'central_china':
        return AgricultureOrigin.centralChina;
      case 'southchina':
      case 'south_china':
        return AgricultureOrigin.southChina;
      case 'southwest':
        return AgricultureOrigin.southwest;
      case 'northwest':
        return AgricultureOrigin.northwest;
      case 'imported':
        return AgricultureOrigin.imported;
      default:
        return AgricultureOrigin.imported;
    }
  }
  
  /// 解析等级
  AgricultureGrade _parseGrade(String gradeStr) {
    switch (gradeStr.toLowerCase()) {
      case 'premium':
        return AgricultureGrade.premium;
      case 'firstclass':
      case 'first_class':
        return AgricultureGrade.firstClass;
      case 'secondclass':
      case 'second_class':
        return AgricultureGrade.secondClass;
      case 'thirdclass':
      case 'third_class':
        return AgricultureGrade.thirdClass;
      default:
        return AgricultureGrade.secondClass;
    }
  }
  
  /// 解析认证
  AgricultureCertification _parseCertification(String certStr) {
    switch (certStr.toLowerCase()) {
      case 'organic':
        return AgricultureCertification.organic;
      case 'green':
        return AgricultureCertification.green;
      case 'pollutionfree':
      case 'pollution_free':
        return AgricultureCertification.pollution_free;
      case 'geographicalindication':
      case 'geographical_indication':
        return AgricultureCertification.geographical_indication;
      default:
        return AgricultureCertification.green;
    }
  }
} 