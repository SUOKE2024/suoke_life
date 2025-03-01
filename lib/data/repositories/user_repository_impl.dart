import 'package:logger/logger.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/user_repository.dart';
import '../datasources/user_data_source.dart';
import '../models/user_model.dart';

/// 用户仓库实现
/// 实现领域层定义的用户仓库接口，连接数据源和领域层
class UserRepositoryImpl implements UserRepository {
  final UserDataSource remoteDataSource;
  final UserDataSource localDataSource;
  final Logger logger;

  UserRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.logger,
  });

  @override
  Future<User?> getCurrentUser() async {
    try {
      final userModel = await localDataSource.getCurrentUser();
      return userModel?.toEntity();
    } catch (e) {
      logger.e('获取当前用户失败: $e');
      return null;
    }
  }

  @override
  Future<User> getUserById(String userId) async {
    try {
      // 首先尝试从本地获取
      try {
        final localUser = await localDataSource.getUserById(userId);
        return localUser.toEntity();
      } catch (_) {
        // 本地不存在，从远程获取
        final remoteUser = await remoteDataSource.getUserById(userId);
        // 保存到本地
        await localDataSource.saveUser(remoteUser);
        return remoteUser.toEntity();
      }
    } catch (e) {
      logger.e('获取用户信息失败: $e');
      throw Exception('获取用户信息失败');
    }
  }

  @override
  Future<User?> getUserByUsername(String username) async {
    try {
      final userModel = await remoteDataSource.getUserByUsername(username);
      if (userModel != null) {
        await localDataSource.saveUser(userModel);
        return userModel.toEntity();
      }
      return null;
    } catch (e) {
      logger.e('通过用户名获取用户失败: $e');
      return null;
    }
  }

  @override
  Future<User?> getUserByEmail(String email) async {
    try {
      final userModel = await remoteDataSource.getUserByEmail(email);
      if (userModel != null) {
        await localDataSource.saveUser(userModel);
        return userModel.toEntity();
      }
      return null;
    } catch (e) {
      logger.e('通过邮箱获取用户失败: $e');
      return null;
    }
  }

  @override
  Future<void> saveUser(User user) async {
    try {
      final userModel = UserModel.fromEntity(user);
      await remoteDataSource.saveUser(userModel);
      await localDataSource.saveUser(userModel);
    } catch (e) {
      logger.e('保存用户信息失败: $e');
      throw Exception('保存用户信息失败');
    }
  }

  @override
  Future<void> deleteUser(String userId) async {
    try {
      await remoteDataSource.deleteUser(userId);
      await localDataSource.deleteUser(userId);
    } catch (e) {
      logger.e('删除用户失败: $e');
      throw Exception('删除用户失败');
    }
  }

  @override
  Future<List<User>> getUsers({int limit = 20, int offset = 0}) async {
    try {
      final userModels = await remoteDataSource.getUsers(limit: limit, offset: offset);
      return userModels.map((model) => model.toEntity()).toList();
    } catch (e) {
      logger.e('获取用户列表失败: $e');
      throw Exception('获取用户列表失败');
    }
  }

  @override
  Future<User> login(String username, String password) async {
    try {
      final userModel = await remoteDataSource.login(username, password);
      await localDataSource.saveUser(userModel);
      return userModel.toEntity();
    } catch (e) {
      logger.e('用户登录失败: $e');
      throw Exception('用户登录失败: 用户名或密码错误');
    }
  }

  @override
  Future<User> register(User user, String password) async {
    try {
      final userModel = UserModel.fromEntity(user);
      final registeredUser = await remoteDataSource.register(userModel, password);
      await localDataSource.saveUser(registeredUser);
      return registeredUser.toEntity();
    } catch (e) {
      logger.e('用户注册失败: $e');
      throw Exception('用户注册失败: $e');
    }
  }

  @override
  Future<void> logout() async {
    try {
      await remoteDataSource.logout();
      // 清除本地用户数据
      final currentUser = await localDataSource.getCurrentUser();
      if (currentUser != null) {
        await localDataSource.deleteUser(currentUser.id);
      }
    } catch (e) {
      logger.e('用户登出失败: $e');
      throw Exception('用户登出失败');
    }
  }

  @override
  Future<void> updatePassword(String userId, String currentPassword, String newPassword) async {
    try {
      await remoteDataSource.updatePassword(userId, currentPassword, newPassword);
    } catch (e) {
      logger.e('更新密码失败: $e');
      throw Exception('更新密码失败: $e');
    }
  }

  @override
  Future<String> updateAvatar(String userId, String filePath) async {
    try {
      final avatarUrl = await remoteDataSource.updateAvatar(userId, filePath);
      // 更新本地用户数据
      final userModel = await localDataSource.getUserById(userId);
      final updatedUser = userModel.copyWith(avatarUrl: avatarUrl);
      await localDataSource.saveUser(updatedUser);
      return avatarUrl;
    } catch (e) {
      logger.e('更新头像失败: $e');
      throw Exception('更新头像失败');
    }
  }

  @override
  Future<bool> isAuthenticated() async {
    try {
      final currentUser = await localDataSource.getCurrentUser();
      return currentUser != null;
    } catch (e) {
      logger.e('检查认证状态失败: $e');
      return false;
    }
  }

  @override
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      // 假设远程数据源提供此功能
      // await remoteDataSource.sendPasswordResetEmail(email);
      throw UnimplementedError('发送密码重置邮件功能尚未实现');
    } catch (e) {
      logger.e('发送密码重置邮件失败: $e');
      throw Exception('发送密码重置邮件失败: $e');
    }
  }

  @override
  Future<void> verifyEmail(String userId, String code) async {
    try {
      // 假设远程数据源提供此功能
      // await remoteDataSource.verifyEmail(userId, code);
      throw UnimplementedError('验证邮箱功能尚未实现');
    } catch (e) {
      logger.e('验证邮箱失败: $e');
      throw Exception('验证邮箱失败: $e');
    }
  }

  @override
  Future<Map<String, dynamic>> getUserPreferences(String userId) async {
    try {
      final user = await getUserById(userId);
      return user.preferences ?? {};
    } catch (e) {
      logger.e('获取用户偏好设置失败: $e');
      throw Exception('获取用户偏好设置失败');
    }
  }

  @override
  Future<void> updateUserPreferences(String userId, Map<String, dynamic> preferences) async {
    try {
      final user = await getUserById(userId);
      final updatedUser = user.copyWith(
        preferences: {...user.preferences ?? {}, ...preferences},
      );
      await saveUser(updatedUser);
    } catch (e) {
      logger.e('更新用户偏好设置失败: $e');
      throw Exception('更新用户偏好设置失败');
    }
  }
} 