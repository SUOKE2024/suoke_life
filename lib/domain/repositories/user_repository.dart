import '../models/user_model.dart';

/// 用户仓库接口
///
/// 定义与用户相关的数据访问方法
abstract class UserRepository {
  /// 获取当前登录用户信息
  Future<User?> getCurrentUser();

  /// 用户登录
  Future<User> login({
    required String username,
    required String password,
  });

  /// 用户注册
  Future<User> register({
    required String username,
    required String password,
    required String phone,
    String? email,
  });

  /// 更新用户信息
  Future<User> updateUserInfo(User user);

  /// 更新用户头像
  Future<String> updateAvatar(String filePath);

  /// 退出登录
  Future<void> logout();

  /// 重置密码
  Future<bool> resetPassword({
    required String phone,
    required String newPassword,
    required String verificationCode,
  });

  /// 发送短信验证码
  Future<bool> sendVerificationCode(String phone);

  /// 检查用户是否已登录
  Future<bool> isLoggedIn();
}
