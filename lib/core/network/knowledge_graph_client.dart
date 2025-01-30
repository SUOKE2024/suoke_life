import 'package:dio/dio.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';

class KnowledgeGraphClient {
  final Dio _dio;
  final AppConfig _appConfig;

  KnowledgeGraphClient(this._appConfig)
      : _dio = Dio(BaseOptions(baseUrl: _appConfig.knowledgeGraphApiBaseUrl)); //  从 AppConfig 获取知识图谱 API Base URL

  Future<Map<String, dynamic>?> queryEntities(String query) async {
    try {
      final response = await _dio.get('/entities', queryParameters: {'query': query});
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>?;
      } else {
        print('Knowledge Graph API queryEntities failed with status code: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Error querying Knowledge Graph API entities: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getEntityRelations(String entityId) async {
    try {
      final response = await _dio.get('/entities/$entityId/relations');
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>?;
      } else {
        print('Knowledge Graph API getEntityRelations failed with status code: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Error getting Knowledge Graph API entity relations: $e');
      return null;
    }
  }
} 