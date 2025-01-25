import 'package:injectable/injectable.dart';
import 'package:permission_handler/permission_handler.dart';

@singleton
class PermissionHandler {
  Future<bool> requestCamera() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<bool> requestMicrophone() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<bool> requestStorage() async {
    final status = await Permission.storage.request();
    return status.isGranted;
  }

  Future<bool> requestLocation() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  Future<bool> requestNotification() async {
    final status = await Permission.notification.request();
    return status.isGranted;
  }

  Future<bool> checkCamera() async {
    return Permission.camera.isGranted;
  }

  Future<bool> checkMicrophone() async {
    return Permission.microphone.isGranted;
  }

  Future<bool> checkStorage() async {
    return Permission.storage.isGranted;
  }

  Future<bool> checkLocation() async {
    return Permission.location.isGranted;
  }

  Future<bool> checkNotification() async {
    return Permission.notification.isGranted;
  }

  Future<void> openSettings() async {
    await openAppSettings();
  }
} 