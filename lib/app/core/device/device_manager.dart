import 'package:get/get.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';

class DeviceManager extends GetxService {
  late final PackageInfo packageInfo;
  late final String deviceId;
  late final String osVersion;
  
  final _deviceInfo = DeviceInfoPlugin();

  Future<void> initialize() async {
    packageInfo = await PackageInfo.fromPlatform();
    
    if (GetPlatform.isAndroid) {
      final androidInfo = await _deviceInfo.androidInfo;
      deviceId = androidInfo.id;
      osVersion = androidInfo.version.release;
    } else if (GetPlatform.isIOS) {
      final iosInfo = await _deviceInfo.iosInfo;
      deviceId = iosInfo.identifierForVendor ?? '';
      osVersion = iosInfo.systemVersion;
    } else {
      deviceId = 'unknown';
      osVersion = 'unknown';
    }
  }
} 