class UpdateManager {
  static final instance = UpdateManager._();
  UpdateManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  final _networkMonitor = Get.find<NetworkMonitor>();
  
  final _updateInfo = Rxn<UpdateInfo>();
  final _updateStatus = Rx<UpdateStatus>(UpdateStatus.none);
  final _downloadProgress = 0.0.obs;
  
  Timer? _checkTimer;
  bool _isChecking = false;

  static const _config = {
    'check_interval': Duration(hours: 12),
    'auto_download': false,
    'force_update_versions': <String>[],
  };

  Future<void> initialize() async {
    // 加载上次更新信息
    await _loadUpdateInfo();
    
    // 启动定期检查
    _startPeriodicCheck();
  }

  Future<void> _loadUpdateInfo() async {
    final info = await _storage.getObject<Map<String, dynamic>>(
      'update_info',
      (json) => json,
    );
    
    if (info != null) {
      _updateInfo.value = UpdateInfo.fromJson(info);
    }
  }

  void _startPeriodicCheck() {
    _checkTimer = Timer.periodic(
      _config['check_interval']!,
      (_) => checkForUpdates(),
    );
  }

  Future<void> checkForUpdates({bool force = false}) async {
    if (_isChecking || (!force && !_networkMonitor.isOnline)) return;

    _isChecking = true;
    _updateStatus.value = UpdateStatus.checking;

    try {
      final apiClient = Get.find<ApiClient>();
      final response = await apiClient.get<Map<String, dynamic>>(
        '/api/updates/check',
        queryParameters: {
          'version': Get.find<AppConfig>().version,
          'platform': Platform.operatingSystem,
        },
      );

      final updateInfo = UpdateInfo.fromJson(response);
      await _handleUpdateCheck(updateInfo);
    } catch (e) {
      _updateStatus.value = UpdateStatus.error;
      _eventBus.fire(UpdateCheckFailedEvent(e));
    } finally {
      _isChecking = false;
    }
  }

  Future<void> _handleUpdateCheck(UpdateInfo updateInfo) async {
    _updateInfo.value = updateInfo;
    await _storage.setObject('update_info', updateInfo.toJson());

    if (updateInfo.hasUpdate) {
      _updateStatus.value = UpdateStatus.available;
      _eventBus.fire(UpdateAvailableEvent(updateInfo));

      if (_config['auto_download'] && !updateInfo.isForceUpdate) {
        downloadUpdate();
      }
    } else {
      _updateStatus.value = UpdateStatus.upToDate;
    }
  }

  Future<void> downloadUpdate() async {
    if (_updateInfo.value == null || !_updateInfo.value!.hasUpdate) return;
    if (_updateStatus.value == UpdateStatus.downloading) return;

    _updateStatus.value = UpdateStatus.downloading;
    _downloadProgress.value = 0;
    _eventBus.fire(UpdateDownloadStartedEvent());

    try {
      final updateFile = await _downloadUpdateFile(
        _updateInfo.value!.downloadUrl,
        onProgress: (progress) {
          _downloadProgress.value = progress;
          _eventBus.fire(UpdateDownloadProgressEvent(progress));
        },
      );

      if (await _verifyUpdate(updateFile)) {
        _updateStatus.value = UpdateStatus.ready;
        _eventBus.fire(UpdateDownloadCompletedEvent(updateFile.path));
      } else {
        throw UpdateException('Update verification failed');
      }
    } catch (e) {
      _updateStatus.value = UpdateStatus.error;
      _eventBus.fire(UpdateDownloadFailedEvent(e));
      rethrow;
    }
  }

  Future<File> _downloadUpdateFile(
    String url, {
    void Function(double)? onProgress,
  }) async {
    final tempDir = await getTemporaryDirectory();
    final tempFile = File('${tempDir.path}/update.apk');

    final dio = Dio();
    await dio.download(
      url,
      tempFile.path,
      onReceiveProgress: (received, total) {
        if (total != -1) {
          onProgress?.call(received / total);
        }
      },
    );

    return tempFile;
  }

  Future<bool> _verifyUpdate(File updateFile) async {
    if (_updateInfo.value == null) return false;

    final checksum = _updateInfo.value!.checksum;
    final fileBytes = await updateFile.readAsBytes();
    final calculated = sha256.convert(fileBytes).toString();

    return checksum == calculated;
  }

  Future<void> installUpdate() async {
    if (_updateStatus.value != UpdateStatus.ready) return;

    _updateStatus.value = UpdateStatus.installing;
    _eventBus.fire(UpdateInstallStartedEvent());

    try {
      // 实现平台特定的安装逻辑
      if (Platform.isAndroid) {
        await _installAndroidUpdate();
      } else if (Platform.isIOS) {
        await _installIOSUpdate();
      }
    } catch (e) {
      _updateStatus.value = UpdateStatus.error;
      _eventBus.fire(UpdateInstallFailedEvent(e));
      rethrow;
    }
  }

  Future<void> _installAndroidUpdate() async {
    // 实现Android更新安装
  }

  Future<void> _installIOSUpdate() async {
    // 实现iOS更新安装
  }

  void dispose() {
    _checkTimer?.cancel();
  }

  UpdateInfo? get updateInfo => _updateInfo.value;
  UpdateStatus get status => _updateStatus.value;
  double get downloadProgress => _downloadProgress.value;
  bool get isForceUpdate => _updateInfo.value?.isForceUpdate ?? false;
}

class UpdateInfo {
  final String version;
  final String downloadUrl;
  final String checksum;
  final bool hasUpdate;
  final bool isForceUpdate;
  final String? releaseNotes;
  final int minOSVersion;
  final DateTime publishedAt;

  UpdateInfo({
    required this.version,
    required this.downloadUrl,
    required this.checksum,
    required this.hasUpdate,
    this.isForceUpdate = false,
    this.releaseNotes,
    required this.minOSVersion,
    required this.publishedAt,
  });

  Map<String, dynamic> toJson() => {
    'version': version,
    'downloadUrl': downloadUrl,
    'checksum': checksum,
    'hasUpdate': hasUpdate,
    'isForceUpdate': isForceUpdate,
    'releaseNotes': releaseNotes,
    'minOSVersion': minOSVersion,
    'publishedAt': publishedAt.toIso8601String(),
  };

  factory UpdateInfo.fromJson(Map<String, dynamic> json) => UpdateInfo(
    version: json['version'],
    downloadUrl: json['downloadUrl'],
    checksum: json['checksum'],
    hasUpdate: json['hasUpdate'],
    isForceUpdate: json['isForceUpdate'] ?? false,
    releaseNotes: json['releaseNotes'],
    minOSVersion: json['minOSVersion'],
    publishedAt: DateTime.parse(json['publishedAt']),
  );
}

enum UpdateStatus {
  none,
  checking,
  upToDate,
  available,
  downloading,
  ready,
  installing,
  error,
}

class UpdateException implements Exception {
  final String message;
  UpdateException(this.message);
}

// 更新相关事件
class UpdateCheckFailedEvent extends AppEvent {
  final dynamic error;
  UpdateCheckFailedEvent(this.error);
}

class UpdateAvailableEvent extends AppEvent {
  final UpdateInfo updateInfo;
  UpdateAvailableEvent(this.updateInfo);
}

class UpdateDownloadStartedEvent extends AppEvent {}

class UpdateDownloadProgressEvent extends AppEvent {
  final double progress;
  UpdateDownloadProgressEvent(this.progress);
}

class UpdateDownloadCompletedEvent extends AppEvent {
  final String filePath;
  UpdateDownloadCompletedEvent(this.filePath);
}

class UpdateDownloadFailedEvent extends AppEvent {
  final dynamic error;
  UpdateDownloadFailedEvent(this.error);
}

class UpdateInstallStartedEvent extends AppEvent {}

class UpdateInstallFailedEvent extends AppEvent {
  final dynamic error;
  UpdateInstallFailedEvent(this.error);
} 