import 'package:injectable/injectable.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'dart:io';

@singleton
class DeviceInfoService {
  final DeviceInfoPlugin _deviceInfo;
  late final PackageInfo _packageInfo;
  Map<String, dynamic>? _deviceData;

  DeviceInfoService(this._deviceInfo);

  Future<void> init() async {
    _packageInfo = await PackageInfo.fromPlatform();
    _deviceData = await _getDeviceInfo();
  }

  Future<Map<String, dynamic>> _getDeviceInfo() async {
    if (Platform.isAndroid) {
      final info = await _deviceInfo.androidInfo;
      return {
        'platform': 'android',
        'version': info.version.release,
        'sdkInt': info.version.sdkInt,
        'manufacturer': info.manufacturer,
        'model': info.model,
        'device': info.device,
        'product': info.product,
      };
    } else if (Platform.isIOS) {
      final info = await _deviceInfo.iosInfo;
      return {
        'platform': 'ios',
        'systemName': info.systemName,
        'systemVersion': info.systemVersion,
        'model': info.model,
        'localizedModel': info.localizedModel,
        'identifierForVendor': info.identifierForVendor,
        'isPhysicalDevice': info.isPhysicalDevice,
      };
    }
    return {};
  }

  String get appVersion => _packageInfo.version;
  String get buildNumber => _packageInfo.buildNumber;
  String get packageName => _packageInfo.packageName;
  String get appName => _packageInfo.appName;

  Map<String, dynamic> get deviceInfo => Map.from(_deviceData ?? {});

  bool get isAndroid => Platform.isAndroid;
  bool get isIOS => Platform.isIOS;
} 