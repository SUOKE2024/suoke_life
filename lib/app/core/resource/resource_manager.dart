class ResourceManager {
  static final instance = ResourceManager._();
  ResourceManager._();

  final _storage = Get.find<StorageManager>();
  final _networkMonitor = Get.find<NetworkMonitor>();
  final _eventBus = Get.find<EventBus>();
  
  final _resources = <String, ResourceInfo>{};
  final _downloadQueue = Queue<ResourceDownloadTask>();
  final _downloadStatus = <String, DownloadStatus>{};
  
  bool _isProcessing = false;

  static const _config = {
    'max_concurrent_downloads': 3,
    'chunk_size': 1024 * 1024,  // 1MB
    'retry_count': 3,
    'cleanup_threshold': 0.9,    // 90%存储使用率时清理
  };

  Future<void> initialize() async {
    // 加载资源信息
    await _loadResourceInfo();
    
    // 检查存储空间
    await _checkStorage();
    
    // 启动下载处理
    _startDownloadProcessing();
  }

  Future<void> _loadResourceInfo() async {
    final info = await _storage.getObject<Map<String, dynamic>>(
      'resource_info',
      (json) => json,
    );

    if (info != null) {
      for (final entry in info.entries) {
        _resources[entry.key] = ResourceInfo.fromJson(entry.value);
      }
    }
  }

  Future<void> _checkStorage() async {
    final usage = await _getStorageUsage();
    if (usage > _config['cleanup_threshold']!) {
      await _cleanupResources();
    }
  }

  Future<double> _getStorageUsage() async {
    final info = await PathProvider.getApplicationDocumentsDirectory();
    final total = await DiskSpace.getTotalDiskSpace();
    final free = await DiskSpace.getFreeDiskSpace();
    return (total - free) / total;
  }

  Future<void> _cleanupResources() async {
    // 按最后访问时间排序
    final sortedResources = _resources.values.toList()
      ..sort((a, b) => a.lastAccess.compareTo(b.lastAccess));

    // 删除最旧的资源直到存储使用率降低
    for (final resource in sortedResources) {
      if (await _getStorageUsage() <= _config['cleanup_threshold']! * 0.8) {
        break;
      }
      await deleteResource(resource.id);
    }
  }

  Future<String?> getResourcePath(String resourceId) async {
    final resource = _resources[resourceId];
    if (resource == null) return null;

    final file = File(resource.localPath);
    if (await file.exists()) {
      resource.lastAccess = DateTime.now();
      await _saveResourceInfo();
      return resource.localPath;
    }

    return null;
  }

  Future<void> downloadResource(String resourceId, String url) async {
    if (_resources.containsKey(resourceId)) return;

    final task = ResourceDownloadTask(
      resourceId: resourceId,
      url: url,
      retryCount: _config['retry_count']!,
    );

    _downloadQueue.add(task);
    _downloadStatus[resourceId] = DownloadStatus.queued;
    _eventBus.fire(ResourceQueuedEvent(resourceId));
    
    _processDownloads();
  }

  Future<void> _processDownloads() async {
    if (_isProcessing || _downloadQueue.isEmpty) return;
    if (_getActiveDownloads().length >= _config['max_concurrent_downloads']!) return;

    _isProcessing = true;
    try {
      while (_downloadQueue.isNotEmpty && 
             _getActiveDownloads().length < _config['max_concurrent_downloads']!) {
        final task = _downloadQueue.removeFirst();
        _startDownload(task);
      }
    } finally {
      _isProcessing = false;
    }
  }

  Future<void> _startDownload(ResourceDownloadTask task) async {
    _downloadStatus[task.resourceId] = DownloadStatus.downloading;
    _eventBus.fire(ResourceDownloadStartedEvent(task.resourceId));

    try {
      final tempPath = await _downloadToTemp(task);
      final finalPath = await _moveToFinal(task.resourceId, tempPath);
      
      _resources[task.resourceId] = ResourceInfo(
        id: task.resourceId,
        url: task.url,
        localPath: finalPath,
        size: await File(finalPath).length(),
        downloadTime: DateTime.now(),
        lastAccess: DateTime.now(),
      );

      await _saveResourceInfo();
      _downloadStatus[task.resourceId] = DownloadStatus.completed;
      _eventBus.fire(ResourceDownloadCompletedEvent(task.resourceId));
    } catch (e) {
      if (task.retryCount > 0) {
        task.retryCount--;
        _downloadQueue.add(task);
        _downloadStatus[task.resourceId] = DownloadStatus.queued;
      } else {
        _downloadStatus[task.resourceId] = DownloadStatus.failed;
        _eventBus.fire(ResourceDownloadFailedEvent(task.resourceId, e));
      }
    }
  }

  Future<String> _downloadToTemp(ResourceDownloadTask task) async {
    final tempDir = await PathProvider.getTemporaryDirectory();
    final tempFile = File('${tempDir.path}/${task.resourceId}_temp');
    
    final client = HttpClient();
    final request = await client.getUrl(Uri.parse(task.url));
    final response = await request.close();
    
    final sink = tempFile.openWrite();
    await response.pipe(sink);
    await sink.close();
    
    return tempFile.path;
  }

  Future<String> _moveToFinal(String resourceId, String tempPath) async {
    final docsDir = await PathProvider.getApplicationDocumentsDirectory();
    final finalPath = '${docsDir.path}/resources/$resourceId';
    
    final finalFile = File(finalPath);
    await finalFile.parent.create(recursive: true);
    await File(tempPath).rename(finalPath);
    
    return finalPath;
  }

  Future<void> deleteResource(String resourceId) async {
    final resource = _resources.remove(resourceId);
    if (resource != null) {
      final file = File(resource.localPath);
      if (await file.exists()) {
        await file.delete();
      }
      await _saveResourceInfo();
      _eventBus.fire(ResourceDeletedEvent(resourceId));
    }
  }

  Future<void> _saveResourceInfo() async {
    final info = <String, dynamic>{};
    for (final entry in _resources.entries) {
      info[entry.key] = entry.value.toJson();
    }
    await _storage.setObject('resource_info', info);
  }

  List<String> _getActiveDownloads() {
    return _downloadStatus.entries
        .where((e) => e.value == DownloadStatus.downloading)
        .map((e) => e.key)
        .toList();
  }

  ResourceInfo? getResourceInfo(String resourceId) => _resources[resourceId];
  DownloadStatus? getDownloadStatus(String resourceId) => _downloadStatus[resourceId];
}

class ResourceInfo {
  final String id;
  final String url;
  final String localPath;
  final int size;
  final DateTime downloadTime;
  DateTime lastAccess;

  ResourceInfo({
    required this.id,
    required this.url,
    required this.localPath,
    required this.size,
    required this.downloadTime,
    required this.lastAccess,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'url': url,
    'localPath': localPath,
    'size': size,
    'downloadTime': downloadTime.toIso8601String(),
    'lastAccess': lastAccess.toIso8601String(),
  };

  factory ResourceInfo.fromJson(Map<String, dynamic> json) => ResourceInfo(
    id: json['id'],
    url: json['url'],
    localPath: json['localPath'],
    size: json['size'],
    downloadTime: DateTime.parse(json['downloadTime']),
    lastAccess: DateTime.parse(json['lastAccess']),
  );
}

class ResourceDownloadTask {
  final String resourceId;
  final String url;
  int retryCount;

  ResourceDownloadTask({
    required this.resourceId,
    required this.url,
    required this.retryCount,
  });
}

enum DownloadStatus {
  queued,
  downloading,
  completed,
  failed,
}

// 资源相关事件
class ResourceQueuedEvent extends AppEvent {
  final String resourceId;
  ResourceQueuedEvent(this.resourceId);
}

class ResourceDownloadStartedEvent extends AppEvent {
  final String resourceId;
  ResourceDownloadStartedEvent(this.resourceId);
}

class ResourceDownloadCompletedEvent extends AppEvent {
  final String resourceId;
  ResourceDownloadCompletedEvent(this.resourceId);
}

class ResourceDownloadFailedEvent extends AppEvent {
  final String resourceId;
  final dynamic error;
  ResourceDownloadFailedEvent(this.resourceId, this.error);
}

class ResourceDeletedEvent extends AppEvent {
  final String resourceId;
  ResourceDeletedEvent(this.resourceId);
} 