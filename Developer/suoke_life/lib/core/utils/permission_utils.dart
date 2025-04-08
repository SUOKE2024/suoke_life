import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart'
    hide openAppSettings;
import 'package:permission_handler/permission_handler.dart'
    as permission_handler show openAppSettings;
import 'package:flutter/foundation.dart' show kIsWeb;

// 对dart:html进行条件导入，只在web平台使用
import 'permission_utils_web.dart'
    if (dart.library.io) 'permission_utils_mobile.dart';

/// 权限工具类，用于请求和检查应用所需的各种权限
class PermissionUtils {
  /// 请求相机权限
  static Future<bool> requestCameraPermission() async {
    if (kIsWeb) {
      // Web平台使用媒体设备API请求相机权限
      return WebPermissionUtils.requestCameraPermission();
    }

    try {
      // 获取当前权限状态
      PermissionStatus status = await Permission.camera.status;

      // 如果已经被永久拒绝，则返回false
      if (status.isPermanentlyDenied) {
        return false;
      }

      // 如果还未请求或被拒绝但不是永久拒绝，请求权限
      if (status.isDenied || status.isRestricted) {
        // 请求摄像头权限
        status = await Permission.camera.request();
      }

      // 返回是否获得权限
      return status.isGranted;
    } catch (e) {
      debugPrint('请求摄像头权限失败: $e');
      return false;
    }
  }

  /// 请求麦克风权限
  static Future<bool> requestMicrophonePermission(
      {bool forceRequest = false}) async {
    if (kIsWeb) {
      // Web平台使用媒体设备API请求麦克风权限
      return WebPermissionUtils.requestMicrophonePermission();
    }

    try {
      // 获取当前权限状态
      PermissionStatus status = await Permission.microphone.status;

      // 如果已经被永久拒绝，且不是强制请求模式，则返回false
      if (status.isPermanentlyDenied && !forceRequest) {
        return false;
      }

      // 如果还未请求或被拒绝但不是永久拒绝，请求权限
      if (status.isDenied || status.isRestricted || forceRequest) {
        // 请求麦克风权限
        status = await Permission.microphone.request();
      }

      // 返回是否获得权限
      return status.isGranted;
    } catch (e) {
      debugPrint('请求麦克风权限失败: $e');
      return false;
    }
  }

  /// 请求相册权限
  static Future<bool> requestPhotosPermission() async {
    if (kIsWeb) {
      // Web平台通过文件选择器间接实现，不需要显式权限
      debugPrint('Web平台使用文件选择器，无需显式请求相册权限');
      return true;
    }
    try {
      // 获取当前权限状态
      PermissionStatus status = await Permission.photos.status;

      // 如果已经被永久拒绝，则返回false
      if (status.isPermanentlyDenied) {
        return false;
      }

      // 如果还未请求或被拒绝但不是永久拒绝，请求权限
      if (status.isDenied || status.isRestricted) {
        // 请求照片库权限
        status = await Permission.photos.request();
      }

      // 返回是否获得权限
      return status.isGranted;
    } catch (e) {
      debugPrint('请求照片库权限失败: $e');
      return false;
    }
  }

  /// 请求位置权限
  static Future<bool> requestLocationPermission() async {
    if (kIsWeb) {
      // Web平台请求位置权限
      return WebPermissionUtils.requestLocationPermission();
    }
    try {
      // 获取当前权限状态
      PermissionStatus status = await Permission.location.status;

      // 如果已经被永久拒绝，则返回false
      if (status.isPermanentlyDenied) {
        return false;
      }

      // 如果还未请求或被拒绝但不是永久拒绝，请求权限
      if (status.isDenied || status.isRestricted) {
        // 请求位置权限
        status = await Permission.location.request();
      }

      // 返回是否获得权限
      return status.isGranted;
    } catch (e) {
      debugPrint('请求位置权限失败: $e');
      return false;
    }
  }

  /// 检查相机权限
  static Future<bool> checkCameraPermission() async {
    if (kIsWeb) {
      // Web平台检查相机权限
      return WebPermissionUtils.checkCameraPermission();
    }
    return await Permission.camera.isGranted;
  }

  /// 检查麦克风权限
  static Future<bool> checkMicrophonePermission() async {
    if (kIsWeb) {
      // Web平台检查麦克风权限
      return WebPermissionUtils.checkMicrophonePermission();
    }

    try {
      final status = await Permission.microphone.status;
      return status.isGranted;
    } catch (e) {
      debugPrint('检查麦克风权限错误: $e');
      return false;
    }
  }

  /// 检查相册权限
  static Future<bool> checkPhotosPermission() async {
    if (kIsWeb) {
      // Web平台通过文件选择器间接实现，不需要显式权限
      return true;
    }
    return await Permission.photos.isGranted;
  }

  /// 检查位置权限
  static Future<bool> checkLocationPermission() async {
    if (kIsWeb) {
      // Web平台检查位置权限
      return WebPermissionUtils.checkLocationPermission();
    }
    return await Permission.location.isGranted;
  }

  /// 请求所有必要权限
  static Future<Map<Permission, PermissionStatus>>
      requestAllPermissions() async {
    try {
      // Web平台特殊处理
      if (kIsWeb) {
        debugPrint('Web平台初始化权限请求');

        // 请求各种权限
        await WebPermissionUtils.requestAllPermissions();
        return {};
      }

      return await [
        Permission.camera,
        Permission.microphone,
        Permission.photos,
        Permission.storage,
      ].request();
    } catch (e) {
      debugPrint('权限请求失败: $e');
      // 返回空映射，而不是抛出异常
      return {};
    }
  }

  /// 显示权限请求对话框
  static Future<void> showPermissionDialog(
    BuildContext context, {
    required String title,
    required String content,
    required String permissionName,
    required Future<void> Function() onRequestPermission,
  }) async {
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              await onRequestPermission();
            },
            child: const Text('授权'),
          ),
        ],
      ),
    );
  }

  /// 打开应用设置页面
  static Future<void> openAppSettings() async {
    try {
      await permission_handler.openAppSettings();
    } catch (e) {
      debugPrint('打开应用设置页面失败: $e');
    }
  }
}
