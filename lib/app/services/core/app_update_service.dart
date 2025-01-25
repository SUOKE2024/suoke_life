import 'package:get/get.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'notification_service.dart';

class AppUpdateService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final NotificationService _notificationService = Get.find();

  final currentVersion = ''.obs;
  final latestVersion = ''.obs;
  final updateInfo = Rx<Map<String, dynamic>?>(null);
  final isChecking = false.obs;
  final isDownloading = false.obs;
  final downloadProgress = 0.0.obs;

  @override
  void onInit() {
    super.onInit();
    _initUpdateService();
  }

  Future<void> _initUpdateService() async {
    try {
      await _loadCurrentVersion();
      await _checkUpdate();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize update service', data: {'error': e.toString()});
    }
  }

  // 检查更新
  Future<bool> checkUpdate() async {
    if (isChecking.value) return false;

    try {
      isChecking.value = true;
      final hasUpdate = await _checkUpdate();
      
      if (hasUpdate) {
        await _notifyUpdate();
      }
      
      return hasUpdate;
    } catch (e) {
      await _loggingService.log('error', 'Failed to check update', data: {'error': e.toString()});
      return false;
    } finally {
      isChecking.value = false;
    }
  }

  // 下载更新
  Future<bool> downloadUpdate() async {
    if (isDownloading.value || updateInfo.value == null) return false;

    try {
      isDownloading.value = true;
      downloadProgress.value = 0;

      final downloadUrl = updateInfo.value!['download_url'];
      final success = await _downloadUpdatePackage(downloadUrl);
      
      if (success) {
        await _verifyUpdatePackage();
        await _prepareUpdate();
      }
      
      return success;
    } catch (e) {
      await _loggingService.log('error', 'Failed to download update', data: {'error': e.toString()});
      return false;
    } finally {
      isDownloading.value = false;
    }
  }

  // 安装更新
  Future<bool> installUpdate() async {
    try {
      if (!await _verifyUpdatePackage()) {
        throw Exception('Update package verification failed');
      }

      final success = await _installUpdatePackage();
      if (success) {
        await _cleanupOldVersion();
      }
      
      return success;
    } catch (e) {
      await _loggingService.log('error', 'Failed to install update', data: {'error': e.toString()});
      return false;
    }
  }

  Future<void> _loadCurrentVersion() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      currentVersion.value = packageInfo.version;
    } catch (e) {
      rethrow;
    }
  }

  Future<bool> _checkUpdate() async {
    try {
      // TODO: 实现检查更新逻辑
      final response = await _fetchUpdateInfo();
      
      if (response != null) {
        updateInfo.value = response;
        latestVersion.value = response['version'];
        return _shouldUpdate(currentVersion.value, latestVersion.value);
      }
      
      return false;
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> _fetchUpdateInfo() async {
    try {
      // TODO: 实现获取更新信息
      return null;
    } catch (e) {
      rethrow;
    }
  }

  bool _shouldUpdate(String currentVersion, String latestVersion) {
    try {
      final current = currentVersion.split('.');
      final latest = latestVersion.split('.');
      
      for (var i = 0; i < 3; i++) {
        final currentNum = int.parse(current[i]);
        final latestNum = int.parse(latest[i]);
        
        if (latestNum > currentNum) {
          return true;
        } else if (latestNum < currentNum) {
          return false;
        }
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> _notifyUpdate() async {
    try {
      await _notificationService.showNotification(
        title: '发现新版本',
        body: '新版本 ${updateInfo.value!['version']} 已经发布,点击查看详情',
        payload: 'app_update',
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<bool> _downloadUpdatePackage(String url) async {
    try {
      // TODO: 实现下载更新包
      return false;
    } catch (e) {
      rethrow;
    }
  }

  Future<bool> _verifyUpdatePackage() async {
    try {
      // TODO: 实现更新包验证
      return false;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _prepareUpdate() async {
    try {
      // TODO: 实现更新准备
    } catch (e) {
      rethrow;
    }
  }

  Future<bool> _installUpdatePackage() async {
    try {
      // TODO: 实现更新包安装
      return false;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _cleanupOldVersion() async {
    try {
      // TODO: 实现旧版本清理
    } catch (e) {
      rethrow;
    }
  }
} 