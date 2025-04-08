import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/api_endpoints.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/models/knowledge_graph_model.dart';

abstract class IKnowledgeGraphRemoteDataSource {
  Future<KnowledgeGraphModel> getKnowledgeGraph({
    String? nodeId,
    int depth = 2,
    Map<String, dynamic>? filters,
  });
  
  Future<void> subscribeToUpdates({
    required String nodeId,
    required Function(KnowledgeGraphModel) onUpdate,
  });
  
  Future<void> unsubscribeFromUpdates(String nodeId);
  
  Future<void> sendInteraction({
    required String nodeId,
    required String interactionType,
    Map<String, dynamic>? data,
  });
}

class KnowledgeGraphRemoteDataSource implements IKnowledgeGraphRemoteDataSource {
  final ApiClient _apiClient;
  final Map<String, Function(KnowledgeGraphModel)> _updateSubscriptions = {};
  
  KnowledgeGraphRemoteDataSource(this._apiClient) {
    _initializeWebSocket();
  }

  void _initializeWebSocket() {
    final wsUrl = ApiEndpoints.knowledgeGraphWS;
    
    _apiClient.connectWebSocket(
      url: wsUrl,
      onMessage: (dynamic message) {
        if (message is String) {
          try {
            final data = json.decode(message);
            if (data['type'] == 'graphUpdate') {
              final nodeId = data['nodeId'];
              final graphData = KnowledgeGraphModel.fromJson(data['graph']);
              
              if (_updateSubscriptions.containsKey(nodeId)) {
                _updateSubscriptions[nodeId]?.call(graphData);
              }
            }
          } catch (e) {
            print('WebSocket消息解析错误: $e');
          }
        }
      },
      onError: (error) {
        print('WebSocket错误: $error');
        // 尝试重新连接
        Future.delayed(const Duration(seconds: 5), _initializeWebSocket);
      },
    );
  }

  @override
  Future<KnowledgeGraphModel> getKnowledgeGraph({
    String? nodeId,
    int depth = 2,
    Map<String, dynamic>? filters,
  }) async {
    try {
      final response = await _apiClient.get(
        ApiEndpoints.knowledgeGraph,
        queryParameters: {
          if (nodeId != null) 'nodeId': nodeId,
          'depth': depth,
          if (filters != null) ...filters,
        },
      );

      return KnowledgeGraphModel.fromJson(response.data);
    } on DioException catch (e) {
      throw ServerException(
        message: '获取知识图谱数据失败',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw const ServerException(message: '解析知识图谱数据失败');
    }
  }

  @override
  Future<void> subscribeToUpdates({
    required String nodeId,
    required Function(KnowledgeGraphModel) onUpdate,
  }) async {
    _updateSubscriptions[nodeId] = onUpdate;
    
    try {
      await _apiClient.post(
        '${ApiEndpoints.knowledgeGraph}/subscribe',
        data: {'nodeId': nodeId},
      );
    } on DioException catch (e) {
      throw ServerException(
        message: '订阅知识图谱更新失败',
        statusCode: e.response?.statusCode,
      );
    }
  }

  @override
  Future<void> unsubscribeFromUpdates(String nodeId) async {
    _updateSubscriptions.remove(nodeId);
    
    try {
      await _apiClient.post(
        '${ApiEndpoints.knowledgeGraph}/unsubscribe',
        data: {'nodeId': nodeId},
      );
    } on DioException catch (e) {
      throw ServerException(
        message: '取消订阅知识图谱更新失败',
        statusCode: e.response?.statusCode,
      );
    }
  }

  @override
  Future<void> sendInteraction({
    required String nodeId,
    required String interactionType,
    Map<String, dynamic>? data,
  }) async {
    try {
      await _apiClient.post(
        '${ApiEndpoints.knowledgeGraph}/interaction',
        data: {
          'nodeId': nodeId,
          'type': interactionType,
          if (data != null) 'data': data,
        },
      );
    } on DioException catch (e) {
      throw ServerException(
        message: '发送交互数据失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
}