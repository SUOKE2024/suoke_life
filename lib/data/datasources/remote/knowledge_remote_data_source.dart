import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

import '../../../core/error/exceptions.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/network_info.dart';
import '../../models/knowledge_node_model.dart';
import '../../models/node_relation_model.dart';
import '../knowledge_data_source.dart';

/// API配置常量
class ApiEndpoints {
  static const String knowledge = '/knowledge';
  static const String nodes = '/knowledge/nodes';
  static const String relations = '/knowledge/relations';
  static const String search = '/knowledge/search';
  static const String semanticSearch = '/knowledge/semantic-search';
  static const String statistics = '/knowledge/statistics';
  static const String embedding = '/ai/embedding';
  static const String sync = '/sync/knowledge';
}

/// 知识图谱远程数据源实现
class KnowledgeRemoteDataSource implements KnowledgeDataSource {
  final ApiClient _apiClient;
  final NetworkInfo _networkInfo;
  final Logger _logger;
  
  KnowledgeRemoteDataSource({
    required ApiClient apiClient,
    required NetworkInfo networkInfo,
    required Logger logger,
  })  : _apiClient = apiClient,
        _networkInfo = networkInfo,
        _logger = logger;
  
  @override
  Future<List<KnowledgeNodeModel>> getAllNodes() async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get(ApiEndpoints.nodes);
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => KnowledgeNodeModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('获取所有知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '获取所有知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取所有知识节点失败', error: e);
      throw ServerException(
        message: '获取所有知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<KnowledgeNodeModel> getNodeById(String nodeId) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get('${ApiEndpoints.nodes}/$nodeId');
      
      return KnowledgeNodeModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      _logger.e('获取知识节点失败: ${e.message}', error: e);
      
      if (e.response?.statusCode == 404) {
        throw NotFoundException(
          message: '知识节点不存在: $nodeId',
          statusCode: e.response?.statusCode,
        );
      }
      
      throw ServerException(
        message: '获取知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取知识节点失败', error: e);
      throw ServerException(
        message: '获取知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> getNodesByType(String type) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get(
        ApiEndpoints.nodes,
        queryParameters: {'type': type},
      );
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => KnowledgeNodeModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('获取类型知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '获取类型知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取类型知识节点失败', error: e);
      throw ServerException(
        message: '获取类型知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> searchNodes(
    String query, {
    List<String>? types,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final queryParams = {
        'query': query,
        'limit': limit.toString(),
        'offset': offset.toString(),
      };
      
      if (types != null && types.isNotEmpty) {
        queryParams['types'] = types.join(',');
      }
      
      final response = await _apiClient.get(
        ApiEndpoints.search,
        queryParameters: queryParams,
      );
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => KnowledgeNodeModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('搜索知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '搜索知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('搜索知识节点失败', error: e);
      throw ServerException(
        message: '搜索知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> semanticSearchNodes(
    List<double> queryEmbedding, {
    List<String>? types,
    int limit = 20,
    double minScore = 0.6,
  }) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final requestData = {
        'embedding': queryEmbedding,
        'limit': limit,
        'min_score': minScore,
      };
      
      if (types != null && types.isNotEmpty) {
        requestData['types'] = types;
      }
      
      final response = await _apiClient.post(
        ApiEndpoints.semanticSearch,
        data: requestData,
      );
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => KnowledgeNodeModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('语义搜索知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '语义搜索知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('语义搜索知识节点失败', error: e);
      throw ServerException(
        message: '语义搜索知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<KnowledgeNodeModel> saveNode(KnowledgeNodeModel node) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.post(
        ApiEndpoints.nodes,
        data: node.toJson(),
      );
      
      return KnowledgeNodeModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      _logger.e('保存知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '保存知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('保存知识节点失败', error: e);
      throw ServerException(
        message: '保存知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<KnowledgeNodeModel> updateNode(KnowledgeNodeModel node) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.put(
        '${ApiEndpoints.nodes}/${node.id}',
        data: node.toJson(),
      );
      
      return KnowledgeNodeModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      _logger.e('更新知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '更新知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('更新知识节点失败', error: e);
      throw ServerException(
        message: '更新知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> deleteNode(String nodeId) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      await _apiClient.delete('${ApiEndpoints.nodes}/$nodeId');
    } on DioException catch (e) {
      _logger.e('删除知识节点失败: ${e.message}', error: e);
      throw ServerException(
        message: '删除知识节点失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('删除知识节点失败', error: e);
      throw ServerException(
        message: '删除知识节点失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<NodeRelationModel>> getNodeRelations(String nodeId) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get(
        ApiEndpoints.relations,
        queryParameters: {'node_id': nodeId},
      );
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => NodeRelationModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('获取节点关系失败: ${e.message}', error: e);
      throw ServerException(
        message: '获取节点关系失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取节点关系失败', error: e);
      throw ServerException(
        message: '获取节点关系失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<NodeRelationModel>> getRelationsByType(String relationType) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get(
        ApiEndpoints.relations,
        queryParameters: {'type': relationType},
      );
      
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => NodeRelationModel.fromJson(item)).toList();
    } on DioException catch (e) {
      _logger.e('获取关系类型失败: ${e.message}', error: e);
      throw ServerException(
        message: '获取关系类型失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取关系类型失败', error: e);
      throw ServerException(
        message: '获取关系类型失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<NodeRelationModel> saveRelation(NodeRelationModel relation) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.post(
        ApiEndpoints.relations,
        data: relation.toJson(),
      );
      
      return NodeRelationModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      _logger.e('保存节点关系失败: ${e.message}', error: e);
      throw ServerException(
        message: '保存节点关系失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('保存节点关系失败', error: e);
      throw ServerException(
        message: '保存节点关系失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<NodeRelationModel> updateRelation(NodeRelationModel relation) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.put(
        '${ApiEndpoints.relations}/${relation.id}',
        data: relation.toJson(),
      );
      
      return NodeRelationModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      _logger.e('更新节点关系失败: ${e.message}', error: e);
      throw ServerException(
        message: '更新节点关系失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('更新节点关系失败', error: e);
      throw ServerException(
        message: '更新节点关系失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> deleteRelation(String relationId) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      await _apiClient.delete('${ApiEndpoints.relations}/$relationId');
    } on DioException catch (e) {
      _logger.e('删除节点关系失败: ${e.message}', error: e);
      throw ServerException(
        message: '删除节点关系失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('删除节点关系失败', error: e);
      throw ServerException(
        message: '删除节点关系失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getKnowledgeGraphStatistics() async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.get(ApiEndpoints.statistics);
      
      return response.data['data'];
    } on DioException catch (e) {
      _logger.e('获取知识图谱统计失败: ${e.message}', error: e);
      throw ServerException(
        message: '获取知识图谱统计失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('获取知识图谱统计失败', error: e);
      throw ServerException(
        message: '获取知识图谱统计失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<double>> generateNodeEmbedding(
    String content, {
    String title = '',
    String type = '',
  }) async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      // 构建请求
      final requestData = {
        'content': content,
      };
      
      if (title.isNotEmpty) {
        requestData['title'] = title;
      }
      
      if (type.isNotEmpty) {
        requestData['type'] = type;
      }
      
      final response = await _apiClient.post(
        ApiEndpoints.embedding,
        data: requestData,
      );
      
      final embeddings = response.data['data']['embedding'] as List<dynamic>;
      return embeddings.map((value) => (value as num).toDouble()).toList();
    } on DioException catch (e) {
      _logger.e('生成节点嵌入向量失败: ${e.message}', error: e);
      throw ServerException(
        message: '生成节点嵌入向量失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('生成节点嵌入向量失败', error: e);
      throw ServerException(
        message: '生成节点嵌入向量失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<bool> syncKnowledgeGraph() async {
    try {
      final isConnected = await _networkInfo.isConnected;
      if (!isConnected) {
        throw NetworkException(message: '无网络连接');
      }
      
      final response = await _apiClient.post(ApiEndpoints.sync);
      
      return response.data['success'] as bool;
    } on DioException catch (e) {
      _logger.e('同步知识图谱失败: ${e.message}', error: e);
      throw ServerException(
        message: '同步知识图谱失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      _logger.e('同步知识图谱失败', error: e);
      throw ServerException(
        message: '同步知识图谱失败: $e',
        statusCode: 500,
      );
    }
  }
}