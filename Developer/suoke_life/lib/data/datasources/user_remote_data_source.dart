import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/user_preferences_model.dart';
import 'package:suoke_life/data/models/health_data_model.dart';
import '../../core/error/exceptions.dart';

/// 用户远程数据源接口
abstract class UserRemoteDataSource {
  /// 获取用户资料
  /// 
  /// [userId] 用户ID
  ///
  /// 成功时返回[UserModel]，失败时抛出[ServerException]
  Future<UserModel> getUserProfile(String userId);

  /// 更新用户资料
  /// 
  /// [userId] 用户ID
  /// [profileData] 更新的资料数据
  ///
  /// 成功时返回更新后的[UserModel]，失败时抛出[ServerException]
  Future<UserModel> updateUserProfile(String userId, Map<String, dynamic> profileData);

  /// 获取用户偏好设置
  /// 
  /// [userId] 用户ID
  ///
  /// 成功时返回[UserPreferencesModel]，失败时抛出[ServerException]
  Future<UserPreferencesModel> getUserPreferences(String userId);

  /// 更新用户偏好设置
  /// 
  /// [userId] 用户ID
  /// [preferences] 更新的偏好设置数据
  ///
  /// 成功时返回更新后的[UserPreferencesModel]，失败时抛出[ServerException]
  Future<UserPreferencesModel> updateUserPreferences(String userId, Map<String, dynamic> preferences);

  /// 获取用户健康数据
  /// 
  /// [userId] 用户ID
  /// [period] 可选的时间周期，例如 'day', 'week', 'month', 'year'
  ///
  /// 成功时返回[HealthDataModel]，失败时抛出[ServerException]
  Future<HealthDataModel> getUserHealthData(String userId, {String? period});
} 