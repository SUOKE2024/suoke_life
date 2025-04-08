import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';

/// 知识远程数据源接口
abstract class KnowledgeRemoteDataSource {
  /// 获取知识节点列表
  Future<List<KnowledgeNodeModel>> getNodes({
    String? query,
    List<String>? tags,
    List<String>? types,
    int page = 1,
    int pageSize = 20
  });
  
  /// 获取指定知识节点
  Future<KnowledgeNodeModel> getNodeById(String nodeId);
  
  /// 获取知识节点关系
  Future<List<KnowledgeRelationModel>> getNodeRelations(String nodeId);
  
  /// 搜索知识节点
  Future<List<KnowledgeNodeModel>> searchNodes(String query);
}

/// 知识远程数据源实现
class KnowledgeRemoteDataSourceImpl implements KnowledgeRemoteDataSource {
  final ApiClient _apiClient;
  
  KnowledgeRemoteDataSourceImpl(this._apiClient);
  
  @override
  Future<List<KnowledgeNodeModel>> getNodes({
    String? query,
    List<String>? tags,
    List<String>? types,
    int page = 1,
    int pageSize = 20
  }) async {
    try {
      final Map<String, dynamic> queryParams = {
        'page': page,
        'pageSize': pageSize,
        if (query != null) 'query': query,
        if (tags != null) 'tags': tags.join(','),
        if (types != null) 'types': types.join(','),
      };
      
      final response = await _apiClient.get(
        '/api/v1/knowledge/nodes',
        queryParameters: queryParams
      );
      
      final List<dynamic> nodesJson = response.data['nodes'];
      return nodesJson.map((json) => KnowledgeNodeModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<KnowledgeNodeModel> getNodeById(String nodeId) async {
    try {
      final response = await _apiClient.get('/api/v1/knowledge/nodes/$nodeId');
      return KnowledgeNodeModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<List<KnowledgeRelationModel>> getNodeRelations(String nodeId) async {
    try {
      final response = await _apiClient.get('/api/v1/knowledge/nodes/$nodeId/relations');
      final List<dynamic> relationsJson = response.data['relations'];
      return relationsJson.map((json) => KnowledgeRelationModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  @override
  Future<List<KnowledgeNodeModel>> searchNodes(String query) async {
    try {
      final response = await _apiClient.get(
        '/api/v1/knowledge/search',
        queryParameters: {'query': query}
      );
      
      final List<dynamic> resultsJson = response.data['results'];
      return resultsJson.map((json) => KnowledgeNodeModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  
  Exception _handleError(DioException e) {
    if (e.response?.statusCode == 401) {
      return UnauthorizedException('未授权访问，请先登录');
    } else if (e.response?.statusCode == 404) {
      return NotFoundException('资源不存在: ${e.message}');
    } else {
      return NetworkException('网络请求失败: ${e.message}');
    }
  }
}

/// 网络异常
class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
}

/// 未授权异常
class UnauthorizedException implements Exception {
  final String message;
  UnauthorizedException(this.message);
}

/// 资源不存在异常
class NotFoundException implements Exception {
  final String message;
  NotFoundException(this.message);
} 