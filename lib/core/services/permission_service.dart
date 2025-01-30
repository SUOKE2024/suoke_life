import 'package:permission_handler/permission_handler.dart';

class PermissionService {
  Future<bool> requestCamera() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<bool> requestMicrophone() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<bool> requestPhotos() async {
    final status = await Permission.photos.request();
    return status.isGranted;
  }

  Future<bool> requestLocation() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  Future<bool> requestNotifications() async {
    final status = await Permission.notification.request();
    return status.isGranted;
  }

  Future<bool> checkPermission(Permission permission) async {
    return await permission.status.isGranted;
  }

  Future<void> openSettings() async {
    await openAppSettings();
  }
} 