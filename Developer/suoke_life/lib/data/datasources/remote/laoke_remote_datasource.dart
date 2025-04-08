import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';

abstract class LaokeRemoteDataSource {
  /// 获取服务状态
  Future<Map<String, dynamic>> getServiceStatus();
  
  /// 获取知识分类
  Future<List<Map<String, dynamic>>> getKnowledgeCategories();
  
  /// 获取知识文章列表
  Future<Map<String, dynamic>> getKnowledgeArticles({
    String? categoryId,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取知识文章详情
  Future<Map<String, dynamic>> getKnowledgeArticleById(String id);
  
  /// 获取培训课程列表
  Future<Map<String, dynamic>> getTrainingCourses({
    String? categoryId,
    String? level,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取培训课程详情
  Future<Map<String, dynamic>> getTrainingCourseById(String id);
  
  /// 获取博客文章列表
  Future<Map<String, dynamic>> getBlogPosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取博客文章详情
  Future<Map<String, dynamic>> getBlogPostById(String id);
  
  /// 文字转语音
  Future<String> textToSpeech(
    String text, {
    String? voiceId,
    Map<String, dynamic>? options,
  });
}

class LaokeRemoteDataSourceImpl implements LaokeRemoteDataSource {
  final ApiClient _apiClient;
  
  LaokeRemoteDataSourceImpl({required ApiClient apiClient})
      : _apiClient = apiClient;
  
  @override
  Future<Map<String, dynamic>> getServiceStatus() async {
    try {
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/status'
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取服务状态失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getKnowledgeCategories() async {
    try {
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/knowledge/categories'
      );
      return List<Map<String, dynamic>>.from(response.data['data']);
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取知识分类失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getKnowledgeArticles({
    String? categoryId,
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final queryParams = {
        if (categoryId != null) 'categoryId': categoryId,
        'page': page.toString(),
        'limit': limit.toString(),
      };
      
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/knowledge/articles',
        queryParameters: queryParams,
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取知识文章失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getKnowledgeArticleById(String id) async {
    try {
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/knowledge/articles/$id'
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取知识文章详情失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getTrainingCourses({
    String? categoryId,
    String? level,
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final queryParams = {
        if (categoryId != null) 'categoryId': categoryId,
        if (level != null) 'level': level,
        'page': page.toString(),
        'limit': limit.toString(),
      };
      
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/training/courses',
        queryParameters: queryParams,
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取培训课程失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getTrainingCourseById(String id) async {
    try {
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/training/courses/$id'
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取培训课程详情失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getBlogPosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final queryParams = {
        if (authorId != null) 'authorId': authorId,
        if (categoryId != null) 'categoryId': categoryId,
        if (tag != null) 'tag': tag,
        if (status != null) 'status': status,
        'page': page.toString(),
        'limit': limit.toString(),
      };
      
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/blog/posts',
        queryParameters: queryParams,
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取博客文章失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getBlogPostById(String id) async {
    try {
      final response = await _apiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/blog/posts/$id'
      );
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '获取博客文章详情失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
  
  @override
  Future<String> textToSpeech(
    String text, {
    String? voiceId,
    Map<String, dynamic>? options,
  }) async {
    try {
      final response = await _apiClient.post(
        '${ApiConstants.laokeServiceBaseUrl}/accessibility/text-to-speech',
        data: {
          'text': text,
          if (voiceId != null) 'voiceId': voiceId,
          if (options != null) ...options,
        },
      );
      return response.data['data']['audioData'];
    } on DioException catch (e) {
      throw ServerException(
        message: e.response?.data?['message'] ?? '文字转语音失败',
        statusCode: e.response?.statusCode,
      );
    }
  }
} 