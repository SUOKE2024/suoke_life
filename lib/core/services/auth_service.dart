import 'package:get/get.dart';
import '../data/models/user.dart';
import '../core/storage/storage_service.dart';
import 'privacy_service.dart';

class AuthService extends GetxService {
  final StorageService _storageService = Get.find();
  final PrivacyService _privacyService = Get.find();
  
  final currentUser = Rx<User?>(null);
  final isLoggedIn = false.obs;

  Future<AuthService> init() async {
    await _loadSavedUser();
    return this;
  }

  Future<void> _loadSavedUser() async {
    try {
      final userData = await _storageService.getLocal('current_user');
      if (userData != null) {
        currentUser.value = User.fromJson(userData);
        isLoggedIn.value = true;
      }
    } catch (e) {
      // 处理错误
    }
  }

  Future<void> login(String email, String password) async {
    try {
      // 检查隐私设置
      if (!_privacyService.getSetting('data_collection')) {
        throw Exception('Data collection is not allowed');
      }
      
      print('Attempting to log in user with email: $email');
      // 示例：调用后端服务进行用户认证
      // 实际实现中需要根据具体认证服务进行调用
      // 例如：final response = await _authApi.login(email, password);
      // if (response.isSuccessful) {
      //   final user = User.fromJson(response.data);
      //   await _storageService.saveLocal('current_user', user.toJson());
      //   currentUser.value = user;
      //   isLoggedIn.value = true;
      // } else {
      //   throw Exception('Login failed');
      // }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> logout() async {
    try {
      await _storageService.removeLocal('current_user');
      currentUser.value = null;
      isLoggedIn.value = false;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> updateProfile(Map<String, dynamic> data) async {
    try {
      if (currentUser.value == null) return;
      
      final updatedUser = User.fromJson({
        ...currentUser.value!.toJson(),
        ...data,
        'updated_at': DateTime.now().toIso8601String(),
      });

      await _storageService.saveLocal('current_user', updatedUser.toJson());
      currentUser.value = updatedUser;
    } catch (e) {
      rethrow;
    }
  }
} 