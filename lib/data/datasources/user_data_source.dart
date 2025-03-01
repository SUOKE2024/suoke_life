import '../models/user_model.dart';

/// 用户数据源接口
/// 定义用户数据的获取和持久化方法
abstract class UserDataSource {
  /// 获取当前登录用户
  Future<UserModel?> getCurrentUser();
  
  /// 通过ID获取用户信息
  Future<UserModel> getUserById(String userId);
  
  /// 通过用户名获取用户信息
  Future<UserModel?> getUserByUsername(String username);
  
  /// 通过电子邮件获取用户信息
  Future<UserModel?> getUserByEmail(String email);
  
  /// 保存或更新用户信息
  Future<void> saveUser(UserModel user);
  
  /// 删除用户信息
  Future<void> deleteUser(String userId);
  
  /// 获取用户列表
  Future<List<UserModel>> getUsers({int limit = 20, int offset = 0});
  
  /// 用户登录
  Future<UserModel> login(String username, String password);
  
  /// 用户注册
  Future<UserModel> register(UserModel user, String password);
  
  /// 用户登出
  Future<void> logout();
  
  /// 更新用户密码
  Future<void> updatePassword(String userId, String currentPassword, String newPassword);
  
  /// 更新用户头像
  Future<String> updateAvatar(String userId, String filePath);
} 