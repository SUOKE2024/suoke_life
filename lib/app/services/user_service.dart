import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'privacy_protection_service.dart';

class UserService extends GetxService {
  final StorageService _storageService = Get.find();
  final PrivacyProtectionService _privacyService = Get.find();

  final currentUser = Rx<Map<String, dynamic>?>(null);
  final userPreferences = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _loadUserData();
  }

  // 用户信息管理
  Future<void> updateUserProfile(Map<String, dynamic> data) async {
    try {
      if (currentUser.value == null) return;

      final updatedUser = {
        ...currentUser.value!,
        ...data,
        'updated_at': DateTime.now().toIso8601String(),
      };

      // 保存用户信息
      await _storageService.saveLocal('current_user', updatedUser);
      currentUser.value = updatedUser;

      // 同步到远程
      await _storageService.saveRemote('user_${updatedUser['id']}', updatedUser);
    } catch (e) {
      rethrow;
    }
  }

  // 用户偏好设置
  Future<void> updatePreferences(Map<String, dynamic> preferences) async {
    try {
      userPreferences.value = {
        ...userPreferences,
        ...preferences,
      };
      await _storageService.saveLocal('user_preferences', userPreferences);
    } catch (e) {
      rethrow;
    }
  }

  // 用户数据导出
  Future<Map<String, dynamic>> exportUserData() async {
    try {
      final userData = await _collectUserData();
      return _privacyService.anonymizeData(userData);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadUserData() async {
    try {
      // 加载用户信息
      final userData = await _storageService.getLocal('current_user');
      if (userData != null) {
        currentUser.value = Map<String, dynamic>.from(userData);
      }

      // 加载用户偏好
      final preferences = await _storageService.getLocal('user_preferences');
      if (preferences != null) {
        userPreferences.value = Map<String, dynamic>.from(preferences);
      }
    } catch (e) {
      // 处理错误
    }
  }

  Future<Map<String, dynamic>> _collectUserData() async {
    try {
      return {
        'profile': currentUser.value,
        'preferences': userPreferences.value,
        'health_records': await _getHealthRecords(),
        'life_records': await _getLifeRecords(),
        'exported_at': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getHealthRecords() async {
    try {
      final data = await _storageService.getLocal('health_records');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> _getLifeRecords() async {
    try {
      final data = await _storageService.getLocal('life_records');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 