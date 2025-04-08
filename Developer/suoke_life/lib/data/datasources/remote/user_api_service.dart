import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/exceptions/user_exceptions.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/user_profile.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/user_preferences_model.dart';

/// 用户API服务接口
/// 
/// 提供与用户服务交互的方法，包括获取用户信息、更新用户信息等
abstract class UserApiService {
  /// 获取用户信息
  Future<User> getUserById(String userId, String accessToken);
  
  /// 获取用户个人资料
  Future<UserProfile> getUserProfile(String userId, String accessToken);
  
  /// 更新用户个人资料
  Future<UserProfile> updateUserProfile(String userId, Map<String, dynamic> profileData, String accessToken);
  
  /// 获取用户偏好设置
  Future<UserPreferences> getUserPreferences(String userId, String accessToken);
  
  /// 更新用户偏好设置
  Future<UserPreferences> updateUserPreferences(String userId, Map<String, dynamic> preferencesData, String accessToken);
  
  /// 获取用户知识偏好
  Future<Map<String, dynamic>> getUserKnowledgePreferences(String userId, String accessToken);
  
  /// 更新用户知识偏好
  Future<Map<String, dynamic>> updateUserKnowledgePreferences(String userId, Map<String, dynamic> knowledgePrefs, String accessToken);
  
  /// 获取用户健康档案
  Future<Map<String, dynamic>> getUserHealthProfile(String userId, String accessToken);
  
  /// 更新用户健康档案
  Future<Map<String, dynamic>> updateUserHealthProfile(String userId, Map<String, dynamic> healthProfileData, String accessToken);
  
  /// 获取用户浏览历史
  Future<List<Map<String, dynamic>>> getUserViewHistory(String userId, String accessToken, {int limit = 10, int offset = 0});
  
  /// 记录用户内容浏览
  Future<bool> recordContentView(String userId, String contentId, String accessToken);
  
  /// 获取用户收藏内容
  Future<List<Map<String, dynamic>>> getUserFavorites(String userId, String accessToken, {int limit = 10, int offset = 0});
  
  /// 添加内容到收藏
  Future<bool> addToFavorites(String userId, String contentId, String accessToken);
  
  /// 从收藏中移除内容
  Future<bool> removeFromFavorites(String userId, String contentId, String accessToken);
  
  /// 获取用户社交分享
  Future<List<Map<String, dynamic>>> getUserSocialShares(String userId, String accessToken, {int limit = 10, int offset = 0});
  
  /// 创建社交分享
  Future<Map<String, dynamic>> createSocialShare(String userId, Map<String, dynamic> shareData, String accessToken);
}

/// 用户API服务实现
class UserApiServiceImpl implements UserApiService {
  final Dio _dio;
  final String _baseUrl = ApiConstants.userServiceUrl;
  
  UserApiServiceImpl({required Dio dio}) : _dio = dio;
  
  @override
  Future<User> getUserById(String userId, String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId',
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data['data']);
      } else {
        throw ServerException(message: '获取用户信息失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户信息失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户信息失败：$e');
    }
  }
  
  @override
  Future<UserProfile> getUserProfile(String userId, String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/profile',
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        // 假设有UserProfileModel来转换数据
        return UserProfile(
          userId: response.data['data']['userId'],
          displayName: response.data['data']['displayName'],
          bio: response.data['data']['bio'],
          avatarUrl: response.data['data']['avatarUrl'],
          contactEmail: response.data['data']['contactEmail'],
          phone: response.data['data']['phone'],
          address: response.data['data']['address'],
          birthday: DateTime.tryParse(response.data['data']['birthday'] ?? ''),
          gender: response.data['data']['gender'],
          occupation: response.data['data']['occupation'],
          education: response.data['data']['education'],
          socialLinks: Map<String, String>.from(response.data['data']['socialLinks'] ?? {}),
          createdAt: DateTime.parse(response.data['data']['createdAt']),
          updatedAt: DateTime.parse(response.data['data']['updatedAt']),
        );
      } else {
        throw ServerException(message: '获取用户个人资料失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户资料不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户资料失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户资料失败：$e');
    }
  }
  
  @override
  Future<UserProfile> updateUserProfile(String userId, Map<String, dynamic> profileData, String accessToken) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/$userId/profile',
        data: profileData,
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return UserProfile(
          userId: response.data['data']['userId'],
          displayName: response.data['data']['displayName'],
          bio: response.data['data']['bio'],
          avatarUrl: response.data['data']['avatarUrl'],
          contactEmail: response.data['data']['contactEmail'],
          phone: response.data['data']['phone'],
          address: response.data['data']['address'],
          birthday: DateTime.tryParse(response.data['data']['birthday'] ?? ''),
          gender: response.data['data']['gender'],
          occupation: response.data['data']['occupation'],
          education: response.data['data']['education'],
          socialLinks: Map<String, String>.from(response.data['data']['socialLinks'] ?? {}),
          createdAt: DateTime.parse(response.data['data']['createdAt']),
          updatedAt: DateTime.parse(response.data['data']['updatedAt']),
        );
      } else {
        throw ServerException(message: '更新用户个人资料失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 400) {
        throw InvalidInputException(message: '无效的个人资料数据: ${e.response?.data['message']}');
      } else {
        throw ServerException(message: '更新用户资料失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '更新用户资料失败：$e');
    }
  }
  
  @override
  Future<UserPreferences> getUserPreferences(String userId, String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/preferences',
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return UserPreferencesModel.fromJson(response.data['data']);
      } else {
        throw ServerException(message: '获取用户偏好设置失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户偏好设置不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户偏好设置失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户偏好设置失败：$e');
    }
  }
  
  @override
  Future<UserPreferences> updateUserPreferences(String userId, Map<String, dynamic> preferencesData, String accessToken) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/$userId/preferences',
        data: preferencesData,
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return UserPreferencesModel.fromJson(response.data['data']);
      } else {
        throw ServerException(message: '更新用户偏好设置失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 400) {
        throw InvalidInputException(message: '无效的偏好设置数据: ${e.response?.data['message']}');
      } else {
        throw ServerException(message: '更新用户偏好设置失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '更新用户偏好设置失败：$e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> getUserKnowledgePreferences(String userId, String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/knowledge-preferences',
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(message: '获取用户知识偏好失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户知识偏好不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户知识偏好失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户知识偏好失败：$e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> updateUserKnowledgePreferences(String userId, Map<String, dynamic> knowledgePrefs, String accessToken) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/$userId/knowledge-preferences',
        data: knowledgePrefs,
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(message: '更新用户知识偏好失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 400) {
        throw InvalidInputException(message: '无效的知识偏好数据: ${e.response?.data['message']}');
      } else {
        throw ServerException(message: '更新用户知识偏好失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '更新用户知识偏好失败：$e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> getUserHealthProfile(String userId, String accessToken) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/health-profile',
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(message: '获取用户健康档案失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户健康档案不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户健康档案失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户健康档案失败：$e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> updateUserHealthProfile(String userId, Map<String, dynamic> healthProfileData, String accessToken) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/$userId/health-profile',
        data: healthProfileData,
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(message: '更新用户健康档案失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 400) {
        throw InvalidInputException(message: '无效的健康档案数据: ${e.response?.data['message']}');
      } else {
        throw ServerException(message: '更新用户健康档案失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '更新用户健康档案失败：$e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserViewHistory(String userId, String accessToken, {int limit = 10, int offset = 0}) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/view-history',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> items = response.data['data'];
        return items.map((item) => Map<String, dynamic>.from(item)).toList();
      } else {
        throw ServerException(message: '获取用户浏览历史失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户浏览历史失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户浏览历史失败：$e');
    }
  }
  
  @override
  Future<bool> recordContentView(String userId, String contentId, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/view-history',
        data: {
          'userId': userId,
          'contentId': contentId,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      return response.statusCode == 200 || response.statusCode == 201;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '记录内容浏览失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '记录内容浏览失败：$e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserFavorites(String userId, String accessToken, {int limit = 10, int offset = 0}) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/favorites',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> items = response.data['data'];
        return items.map((item) => Map<String, dynamic>.from(item)).toList();
      } else {
        throw ServerException(message: '获取用户收藏内容失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户收藏内容失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户收藏内容失败：$e');
    }
  }
  
  @override
  Future<bool> addToFavorites(String userId, String contentId, String accessToken) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/favorites',
        data: {
          'userId': userId,
          'contentId': contentId,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      return response.statusCode == 200 || response.statusCode == 201;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户或内容不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 409) {
        throw ConflictException(message: '该内容已经被收藏');
      } else {
        throw ServerException(message: '添加收藏失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '添加收藏失败：$e');
    }
  }
  
  @override
  Future<bool> removeFromFavorites(String userId, String contentId, String accessToken) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/favorites/$contentId',
        queryParameters: {
          'userId': userId,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      return response.statusCode == 200 || response.statusCode == 204;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户或收藏内容不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '移除收藏失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '移除收藏失败：$e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserSocialShares(String userId, String accessToken, {int limit = 10, int offset = 0}) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/$userId/social-shares',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> items = response.data['data'];
        return items.map((item) => Map<String, dynamic>.from(item)).toList();
      } else {
        throw ServerException(message: '获取用户社交分享失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else {
        throw ServerException(message: '获取用户社交分享失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '获取用户社交分享失败：$e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> createSocialShare(String userId, Map<String, dynamic> shareData, String accessToken) async {
    try {
      final response = await _dio.post(
        ApiConstants.socialSharesPath,
        data: {
          'userId': userId,
          ...shareData,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
        ),
      );
      
      if (response.statusCode == 201 || response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(message: '创建社交分享失败：${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw UserNotFoundException(message: '用户不存在');
      } else if (e.response?.statusCode == 401) {
        throw UnauthorizedException(message: '未授权访问');
      } else if (e.response?.statusCode == 400) {
        throw InvalidInputException(message: '无效的分享数据: ${e.response?.data['message']}');
      } else {
        throw ServerException(message: '创建社交分享失败：${e.message}');
      }
    } catch (e) {
      throw ServerException(message: '创建社交分享失败：$e');
    }
  }
} 