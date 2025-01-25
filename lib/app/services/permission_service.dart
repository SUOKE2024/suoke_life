import 'package:get/get.dart';
import 'package:permission_handler/permission_handler.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class PermissionService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final permissionStatus = <Permission, PermissionStatus>{}.obs;
  final permissionHistory = <Map<String, dynamic>>[].obs;

  final requiredPermissions = <Permission>[
    Permission.camera,
    Permission.microphone,
    Permission.storage,
    Permission.location,
    Permission.notification,
  ];

  @override
  void onInit() {
    super.onInit();
    _initPermissions();
  }

  Future<void> _initPermissions() async {
    try {
      await _loadPermissionHistory();
      await _checkPermissions();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize permissions', data: {'error': e.toString()});
    }
  }

  // 检查权限
  Future<bool> checkPermission(Permission permission) async {
    try {
      final status = await permission.status;
      permissionStatus[permission] = status;
      return status.isGranted;
    } catch (e) {
      await _loggingService.log('error', 'Failed to check permission', data: {'permission': permission.toString(), 'error': e.toString()});
      return false;
    }
  }

  // 请求权限
  Future<bool> requestPermission(Permission permission) async {
    try {
      final status = await permission.request();
      permissionStatus[permission] = status;
      
      await _recordPermissionRequest(permission, status);
      
      return status.isGranted;
    } catch (e) {
      await _loggingService.log('error', 'Failed to request permission', data: {'permission': permission.toString(), 'error': e.toString()});
      return false;
    }
  }

  // 请求多个权限
  Future<Map<Permission, bool>> requestPermissions(List<Permission> permissions) async {
    try {
      final results = <Permission, bool>{};
      
      for (final permission in permissions) {
        results[permission] = await requestPermission(permission);
      }
      
      return results;
    } catch (e) {
      await _loggingService.log('error', 'Failed to request permissions', data: {'error': e.toString()});
      return {};
    }
  }

  // 检查是否有所有必需权限
  Future<bool> hasRequiredPermissions() async {
    try {
      for (final permission in requiredPermissions) {
        if (!await checkPermission(permission)) {
          return false;
        }
      }
      return true;
    } catch (e) {
      await _loggingService.log('error', 'Failed to check required permissions', data: {'error': e.toString()});
      return false;
    }
  }

  // 打开设置
  Future<bool> openSettings() async {
    try {
      return await openAppSettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to open settings', data: {'error': e.toString()});
      return false;
    }
  }

  Future<void> _checkPermissions() async {
    try {
      for (final permission in requiredPermissions) {
        await checkPermission(permission);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordPermissionRequest(
    Permission permission,
    PermissionStatus status,
  ) async {
    try {
      final record = {
        'permission': permission.toString(),
        'status': status.toString(),
        'timestamp': DateTime.now().toIso8601String(),
      };

      permissionHistory.insert(0, record);
      
      // 只保留最近100条记录
      if (permissionHistory.length > 100) {
        permissionHistory.removeRange(100, permissionHistory.length);
      }
      
      await _savePermissionHistory();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadPermissionHistory() async {
    try {
      final history = await _storageService.getLocal('permission_history');
      if (history != null) {
        permissionHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _savePermissionHistory() async {
    try {
      await _storageService.saveLocal('permission_history', permissionHistory);
    } catch (e) {
      rethrow;
    }
  }

  String _getPermissionDescription(Permission permission) {
    switch (permission) {
      case Permission.camera:
        return '用于拍照和视频录制';
      case Permission.microphone:
        return '用于语音录制和通话';
      case Permission.storage:
        return '用于保存和读取文件';
      case Permission.location:
        return '用于获取位置信息';
      case Permission.notification:
        return '用于接收通知消息';
      default:
        return '应用功能所需权限';
    }
  }

  String _getPermissionDeniedMessage(Permission permission) {
    return '${_getPermissionDescription(permission)}\n请在设置中开启权限';
  }

  Future<void> showPermissionDialog(Permission permission) async {
    try {
      final result = await Get.dialog(
        AlertDialog(
          title: Text('权限申请'),
          content: Text(_getPermissionDescription(permission)),
          actions: [
            TextButton(
              onPressed: () => Get.back(result: false),
              child: Text('暂不开启'),
            ),
            TextButton(
              onPressed: () => Get.back(result: true),
              child: Text('立即开启'),
            ),
          ],
        ),
      );

      if (result == true) {
        await requestPermission(permission);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to show permission dialog', data: {'permission': permission.toString(), 'error': e.toString()});
    }
  }

  Future<void> showPermissionDeniedDialog(Permission permission) async {
    try {
      final result = await Get.dialog(
        AlertDialog(
          title: Text('权限未开启'),
          content: Text(_getPermissionDeniedMessage(permission)),
          actions: [
            TextButton(
              onPressed: () => Get.back(result: false),
              child: Text('取消'),
            ),
            TextButton(
              onPressed: () => Get.back(result: true),
              child: Text('去设置'),
            ),
          ],
        ),
      );

      if (result == true) {
        await openSettings();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to show permission denied dialog', data: {'permission': permission.toString(), 'error': e.toString()});
    }
  }
} 