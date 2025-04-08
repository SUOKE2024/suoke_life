import 'package:flutter/foundation.dart';

/// 向量数据库服务接口
abstract class VectorDBService {
  /// 初始化向量数据库
  Future<void> initialize();

  /// 添加向量到数据库
  /// 
  /// [collection] - 集合名称
  /// [vectorData] - 向量数据，包含id、向量和元数据
  Future<bool> addVector({
    required String collection,
    required Map<String, dynamic> vectorData,
  });

  /// 批量添加向量到数据库
  /// 
  /// [collection] - 集合名称
  /// [vectorsData] - 向量数据列表
  Future<bool> addVectors({
    required String collection,
    required List<Map<String, dynamic>> vectorsData,
  });

  /// 根据ID获取向量
  /// 
  /// [collection] - 集合名称
  /// [id] - 向量ID
  Future<Map<String, dynamic>?> getVector({
    required String collection,
    required String id,
  });

  /// 删除向量
  /// 
  /// [collection] - 集合名称
  /// [id] - 向量ID
  Future<bool> deleteVector({
    required String collection,
    required String id,
  });

  /// 批量删除向量
  /// 
  /// [collection] - 集合名称
  /// [ids] - 向量ID列表
  Future<bool> deleteVectors({
    required String collection,
    required List<String> ids,
  });

  /// 搜索相似向量
  /// 
  /// [collection] - 集合名称
  /// [queryVector] - 查询向量
  /// [limit] - 返回结果数量限制
  /// [threshold] - 相似度阈值
  /// [filter] - 元数据过滤条件
  Future<List<Map<String, dynamic>>> searchSimilarVectors({
    required String collection,
    required List<double> queryVector,
    int limit = 5,
    double threshold = 0.7,
    Map<String, dynamic>? filter,
  });

  /// 创建集合
  /// 
  /// [collection] - 集合名称
  /// [dimension] - 向量维度
  Future<bool> createCollection({
    required String collection,
    required int dimension,
  });

  /// 删除集合
  /// 
  /// [collection] - 集合名称
  Future<bool> deleteCollection({
    required String collection,
  });

  /// 获取所有集合
  Future<List<String>> listCollections();

  /// 获取集合信息
  /// 
  /// [collection] - 集合名称
  Future<Map<String, dynamic>> getCollectionInfo({
    required String collection,
  });

  /// 获取集合统计信息
  /// 
  /// [collection] - 集合名称
  Future<Map<String, dynamic>> getCollectionStats({
    required String collection,
  });

  /// 关闭数据库连接
  Future<void> close();
} 