class DeviceManager {
  static final instance = DeviceManager._();
  DeviceManager._();

  late final DeviceInfo _deviceInfo;
  late final PackageInfo _packageInfo;
  final _storage = Get.find<StorageManager>();
  
  String? _deviceId;
  Map<String, dynamic>? _deviceMetadata;

  Future<void> initialize() async {
    // 初始化设备信息
    final deviceInfoPlugin = DeviceInfoPlugin();
    if (Platform.isAndroid) {
      final info = await deviceInfoPlugin.androidInfo;
      _deviceInfo = DeviceInfo.fromAndroidInfo(info);
    } else if (Platform.isIOS) {
      final info = await deviceInfoPlugin.iosInfo;
      _deviceInfo = DeviceInfo.fromIosInfo(info);
    }

    // 初始化应用信息
    _packageInfo = await PackageInfo.fromPlatform();
    
    // 获取或生成设备ID
    await _initializeDeviceId();
    
    // 收集设备元数据
    await _collectDeviceMetadata();
  }

  Future<void> _initializeDeviceId() async {
    _deviceId = await _storage.getSecureString('device_id');
    if (_deviceId == null) {
      _deviceId = const Uuid().v4();
      await _storage.setSecureString('device_id', _deviceId!);
    }
  }

  Future<void> _collectDeviceMetadata() async {
    _deviceMetadata = {
      'platform': Platform.operatingSystem,
      'version': Platform.operatingSystemVersion,
      'model': _deviceInfo.model,
      'manufacturer': _deviceInfo.manufacturer,
      'appVersion': _packageInfo.version,
      'buildNumber': _packageInfo.buildNumber,
      'locale': Platform.localeName,
      'timezone': DateTime.now().timeZoneName,
    };
  }

  String get deviceId => _deviceId!;
  DeviceInfo get deviceInfo => _deviceInfo;
  PackageInfo get packageInfo => _packageInfo;
  Map<String, dynamic> get metadata => Map.unmodifiable(_deviceMetadata!);

  bool get isPhysicalDevice => _deviceInfo.isPhysicalDevice;
  String get deviceModel => _deviceInfo.model;
  String get osVersion => _deviceInfo.osVersion;
}

class DeviceInfo {
  final String model;
  final String manufacturer;
  final String osVersion;
  final bool isPhysicalDevice;
  final Map<String, dynamic> additionalInfo;

  DeviceInfo({
    required this.model,
    required this.manufacturer,
    required this.osVersion,
    required this.isPhysicalDevice,
    this.additionalInfo = const {},
  });

  factory DeviceInfo.fromAndroidInfo(AndroidDeviceInfo info) {
    return DeviceInfo(
      model: info.model,
      manufacturer: info.manufacturer,
      osVersion: info.version.release,
      isPhysicalDevice: info.isPhysicalDevice,
      additionalInfo: {
        'androidId': info.androidId,
        'brand': info.brand,
        'device': info.device,
        'hardware': info.hardware,
        'sdkInt': info.version.sdkInt,
      },
    );
  }

  factory DeviceInfo.fromIosInfo(IosDeviceInfo info) {
    return DeviceInfo(
      model: info.model,
      manufacturer: 'Apple',
      osVersion: info.systemVersion,
      isPhysicalDevice: info.isPhysicalDevice,
      additionalInfo: {
        'name': info.name,
        'systemName': info.systemName,
        'utsname': info.utsname.sysname,
        'identifierForVendor': info.identifierForVendor,
      },
    );
  }
} 