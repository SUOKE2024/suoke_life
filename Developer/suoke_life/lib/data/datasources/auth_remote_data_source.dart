import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/auth_token_model.dart';
import '../../core/error/exceptions.dart';

/// 认证远程数据源接口
abstract class AuthRemoteDataSource {
  /// 登录
  /// 
  /// [email] 邮箱
  /// [password] 密码
  ///
  /// 成功时返回(UserModel, AuthTokenModel)元组，失败时抛出[ServerException]
  Future<(UserModel, AuthTokenModel)> login(String email, String password);

  /// 注册
  /// 
  /// [userData] 用户注册数据
  ///
  /// 成功时返回(UserModel, AuthTokenModel)元组，失败时抛出[ServerException]
  Future<(UserModel, AuthTokenModel)> register(Map<String, dynamic> userData);

  /// 刷新令牌
  /// 
  /// [refreshToken] 刷新令牌
  ///
  /// 成功时返回新的[AuthTokenModel]，失败时抛出[ServerException]
  Future<AuthTokenModel> refreshToken(String refreshToken);

  /// 登出
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> logout();

  /// 验证邮箱
  /// 
  /// [email] 邮箱地址
  /// [code] 验证码
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> verifyEmail(String email, String code);

  /// 发送重置密码邮件
  /// 
  /// [email] 邮箱地址
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> sendPasswordResetEmail(String email);

  /// 重置密码
  /// 
  /// [email] 邮箱地址
  /// [code] 验证码
  /// [newPassword] 新密码
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> resetPassword(String email, String code, String newPassword);

  /// 更改密码
  /// 
  /// [oldPassword] 旧密码
  /// [newPassword] 新密码
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> changePassword(String oldPassword, String newPassword);

  /// 发送手机验证码
  /// 
  /// [phoneNumber] 手机号
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> sendPhoneVerificationCode(String phoneNumber);

  /// 验证手机号
  /// 
  /// [phoneNumber] 手机号
  /// [code] 验证码
  ///
  /// 成功时返回true，失败时抛出[ServerException]
  Future<bool> verifyPhone(String phoneNumber, String code);
} 