// 注意：该文件在非Web平台运行，但实际上不会被使用
// 仅用于满足条件导入的需求

/// 移动平台的权限工具类（仅为了满足条件导入的需求）
class WebPermissionUtils {
  /// 请求相机权限
  static Future<bool> requestCameraPermission() async {
    return false;
  }

  /// 请求麦克风权限
  static Future<bool> requestMicrophonePermission() async {
    return false;
  }

  /// 请求位置权限
  static Future<bool> requestLocationPermission() async {
    return false;
  }

  /// 检查相机权限
  static Future<bool> checkCameraPermission() async {
    return false;
  }

  /// 检查麦克风权限
  static Future<bool> checkMicrophonePermission() async {
    return false;
  }

  /// 检查位置权限
  static Future<bool> checkLocationPermission() async {
    return false;
  }

  /// 请求所有Web平台支持的权限
  static Future<void> requestAllPermissions() async {
    // 在移动平台上不会被调用
  }
}
