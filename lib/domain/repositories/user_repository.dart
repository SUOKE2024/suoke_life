import 'package:dio/dio.dart';
import '../entities/user.dart';

/// 用户仓库接口
/// 定义应用中用户数据相关的业务操作
abstract class UserRepository {
  /// 获取当前登录用户
  Future<User?> getCurrentUser();
  
  /// 通过ID获取用户信息
  Future<User> getUserById(String userId);
  
  /// 通过用户名获取用户信息
  Future<User?> getUserByUsername(String username);
  
  /// 通过电子邮件获取用户信息
  Future<User?> getUserByEmail(String email);
  
  /// 保存或更新用户信息
  Future<void> saveUser(User user);
  
  /// 删除用户账户
  Future<void> deleteUser(String userId);
  
  /// 获取用户列表
  Future<List<User>> getUsers({int limit = 20, int offset = 0});
  
  /// 用户登录
  Future<User> login(String username, String password);
  
  /// 用户注册
  Future<User> register(User user, String password);
  
  /// 用户登出
  Future<void> logout();
  
  /// 更新用户密码
  Future<void> updatePassword(String userId, String currentPassword, String newPassword);
  
  /// 更新用户头像
  Future<String> updateAvatar(String userId, String filePath);
  
  /// 获取用户认证状态
  Future<bool> isAuthenticated();
  
  /// 发送密码重置邮件
  Future<void> sendPasswordResetEmail(String email);
  
  /// 验证用户邮箱
  Future<void> verifyEmail(String userId, String code);
  
  /// 获取用户偏好设置
  Future<Map<String, dynamic>> getUserPreferences(String userId);
  
  /// 更新用户偏好设置
  Future<void> updateUserPreferences(String userId, Map<String, dynamic> preferences);
  
  /// 根据ID获取用户
  Future<User?> getUserById(String userId);
  
  /// 获取所有用户
  Future<List<User>> getAllUsers();
  
  /// 更新用户信息
  Future<bool> updateUser(User user);
  
  /// 上传用户头像
  Future<String?> uploadAvatar(FormData formData);
} 