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
      // TODO: 实现登录逻辑
      final encryptedPassword = _privacyService.encrypt(password);
      
      // 模拟登录
      final user = User(
        id: DateTime.now().toString(),
        name: 'Test User',
        email: email,
        phone: '1234567890',
        settings: {},
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await _storageService.saveLocal('current_user', user.toJson());
      currentUser.value = user;
      isLoggedIn.value = true;
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