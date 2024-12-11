import 'package:permission_handler/permission_handler.dart';

enum PermissionStatus {
  granted,
  denied,
  restricted,
  permanentlyDenied
}

class PermissionManagerService {
  Future<Map<Permission, PermissionStatus>> checkPermissions() async {
    final permissions = <Permission, PermissionStatus>{};
    
    // 检查相机权限
    final cameraStatus = await Permission.camera.status;
    permissions[Permission.camera] = _mapStatus(cameraStatus);
    
    // 检查麦克风权限
    final microphoneStatus = await Permission.microphone.status;
    permissions[Permission.microphone] = _mapStatus(microphoneStatus);
    
    return permissions;
  }

  Future<bool> requestVideoConferencePermissions() async {
    // 请求相机和麦克风权限
    Map<Permission, PermissionStatus> statuses = await [
      Permission.camera,
      Permission.microphone,
    ].request();

    // 检查是否所有权限都已授予
    bool allGranted = statuses.values.every(
      (status) => status == PermissionStatus.granted
    );

    return allGranted;
  }

  Future<bool> requestCameraPermission() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<bool> requestMicrophonePermission() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<void> openAppSettings() async {
    await openAppSettings();
  }

  PermissionStatus _mapStatus(permission_handler.PermissionStatus status) {
    switch (status) {
      case permission_handler.PermissionStatus.granted:
        return PermissionStatus.granted;
      case permission_handler.PermissionStatus.denied:
        return PermissionStatus.denied;
      case permission_handler.PermissionStatus.restricted:
        return PermissionStatus.restricted;
      case permission_handler.PermissionStatus.permanentlyDenied:
        return PermissionStatus.permanentlyDenied;
      default:
        return PermissionStatus.denied;
    }
  }
} 