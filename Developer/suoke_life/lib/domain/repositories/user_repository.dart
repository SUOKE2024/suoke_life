import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';
import 'package:suoke_life/domain/entities/user_profile.dart';

/// 用户仓库接口
/// 
/// 提供用户相关的所有操作接口，包括用户信息获取、用户偏好设置管理等
abstract class UserRepository {
  /// 获取用户信息
  Future<Either<Failure, User>> getUserById(String userId);
  
  /// 获取用户个人资料
  Future<Either<Failure, UserProfile>> getUserProfile(String userId);
  
  /// 更新用户个人资料
  Future<Either<Failure, UserProfile>> updateUserProfile(String userId, Map<String, dynamic> profileData);
  
  /// 获取用户偏好设置
  Future<Either<Failure, UserPreferences>> getUserPreferences(String userId);
  
  /// 更新用户偏好设置
  Future<Either<Failure, UserPreferences>> updateUserPreferences(String userId, Map<String, dynamic> preferencesData);
  
  /// 获取用户知识偏好
  Future<Either<Failure, Map<String, dynamic>>> getUserKnowledgePreferences(String userId);
  
  /// 更新用户知识偏好
  Future<Either<Failure, Map<String, dynamic>>> updateUserKnowledgePreferences(String userId, Map<String, dynamic> knowledgePrefs);
  
  /// 获取用户健康档案
  Future<Either<Failure, Map<String, dynamic>>> getUserHealthProfile(String userId);
  
  /// 更新用户健康档案
  Future<Either<Failure, Map<String, dynamic>>> updateUserHealthProfile(String userId, Map<String, dynamic> healthProfileData);
  
  /// 获取用户浏览历史
  Future<Either<Failure, List<Map<String, dynamic>>>> getUserViewHistory(String userId, {int limit = 10, int offset = 0});
  
  /// 记录用户内容浏览
  Future<Either<Failure, bool>> recordContentView(String userId, String contentId);
  
  /// 获取用户收藏内容
  Future<Either<Failure, List<Map<String, dynamic>>>> getUserFavorites(String userId, {int limit = 10, int offset = 0});
  
  /// 添加内容到收藏
  Future<Either<Failure, bool>> addToFavorites(String userId, String contentId);
  
  /// 从收藏中移除内容
  Future<Either<Failure, bool>> removeFromFavorites(String userId, String contentId);
  
  /// 获取用户社交分享
  Future<Either<Failure, List<Map<String, dynamic>>>> getUserSocialShares(String userId, {int limit = 10, int offset = 0});
  
  /// 创建社交分享
  Future<Either<Failure, Map<String, dynamic>>> createSocialShare(String userId, Map<String, dynamic> shareData);
}
