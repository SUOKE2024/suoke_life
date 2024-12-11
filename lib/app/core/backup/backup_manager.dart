class BackupManager {
  static final instance = BackupManager._();
  BackupManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _backupHistory = <BackupInfo>[];
  final _backupInProgress = false.obs;
  
  static const _config = {
    'max_backups': 5,
    'backup_path': 'backups',
    'temp_path': 'temp',
  };

  Future<void> initialize() async {
    // 加载备份历史
    await _loadBackupHistory();
    
    // 清理过期备份
    await _cleanupOldBackups();
  }

  Future<void> _loadBackupHistory() async {
    final history = await _storage.getObject<List>(
      'backup_history',
      (json) => (json['backups'] as List)
          .map((e) => BackupInfo.fromJson(e))
          .toList(),
    );
    
    if (history != null) {
      _backupHistory.addAll(history);
    }
  }

  Future<void> createBackup({String? description}) async {
    if (_backupInProgress.value) {
      throw BackupException('Backup already in progress');
    }

    _backupInProgress.value = true;
    _eventBus.fire(BackupStartedEvent());

    try {
      final backupInfo = await _performBackup(description);
      _backupHistory.add(backupInfo);
      await _saveBackupHistory();
      
      _eventBus.fire(BackupCompletedEvent(backupInfo));
    } catch (e) {
      _eventBus.fire(BackupFailedEvent(e));
      rethrow;
    } finally {
      _backupInProgress.value = false;
    }
  }

  Future<BackupInfo> _performBackup(String? description) async {
    final timestamp = DateTime.now();
    final backupId = const Uuid().v4();
    
    // 创建临时目录
    final tempDir = await _createTempDirectory(backupId);
    
    try {
      // 备份数据库
      await _backupDatabase(tempDir);
      
      // 备份用户文件
      await _backupUserFiles(tempDir);
      
      // 备份应用设置
      await _backupSettings(tempDir);
      
      // 创建备份文件
      final backupFile = await _createBackupArchive(tempDir, backupId);
      
      return BackupInfo(
        id: backupId,
        timestamp: timestamp,
        description: description,
        size: await backupFile.length(),
        path: backupFile.path,
      );
    } finally {
      // 清理临时目录
      await tempDir.delete(recursive: true);
    }
  }

  Future<Directory> _createTempDirectory(String backupId) async {
    final appDir = await getApplicationDocumentsDirectory();
    final tempPath = '${appDir.path}/${_config['temp_path']}/$backupId';
    return Directory(tempPath).create(recursive: true);
  }

  Future<void> _backupDatabase(Directory tempDir) async {
    // 实现数据库备份逻辑
  }

  Future<void> _backupUserFiles(Directory tempDir) async {
    // 实现用户文件备份逻辑
  }

  Future<void> _backupSettings(Directory tempDir) async {
    // 实现设置备份逻辑
  }

  Future<File> _createBackupArchive(Directory tempDir, String backupId) async {
    final appDir = await getApplicationDocumentsDirectory();
    final backupPath = '${appDir.path}/${_config['backup_path']}/$backupId.zip';
    
    // 创建ZIP文件
    final encoder = ZipEncoder();
    final output = OutputFileStream(backupPath);
    await encoder.zipDirectory(tempDir, output: output);
    await output.close();
    
    return File(backupPath);
  }

  Future<void> restore(String backupId) async {
    final backup = _backupHistory.firstWhere(
      (b) => b.id == backupId,
      orElse: () => throw BackupException('Backup not found'),
    );

    _eventBus.fire(RestoreStartedEvent(backup));

    try {
      await _performRestore(backup);
      _eventBus.fire(RestoreCompletedEvent(backup));
    } catch (e) {
      _eventBus.fire(RestoreFailedEvent(backup, e));
      rethrow;
    }
  }

  Future<void> _performRestore(BackupInfo backup) async {
    // 创建临时目录
    final tempDir = await _createTempDirectory('restore_${backup.id}');
    
    try {
      // 解压备份文件
      await _extractBackup(backup.path, tempDir);
      
      // 恢复数据库
      await _restoreDatabase(tempDir);
      
      // 恢复用户文件
      await _restoreUserFiles(tempDir);
      
      // 恢复应用设置
      await _restoreSettings(tempDir);
    } finally {
      // 清理临时目录
      await tempDir.delete(recursive: true);
    }
  }

  Future<void> _extractBackup(String backupPath, Directory tempDir) async {
    final input = InputFileStream(backupPath);
    final archive = ZipDecoder().decodeBuffer(input);
    await extractArchiveToDisk(archive, tempDir.path);
  }

  Future<void> _restoreDatabase(Directory tempDir) async {
    // 实现数据库恢复逻辑
  }

  Future<void> _restoreUserFiles(Directory tempDir) async {
    // 实现用户文件恢复逻辑
  }

  Future<void> _restoreSettings(Directory tempDir) async {
    // 实现设置恢复逻辑
  }

  Future<void> deleteBackup(String backupId) async {
    final backup = _backupHistory.firstWhere(
      (b) => b.id == backupId,
      orElse: () => throw BackupException('Backup not found'),
    );

    final file = File(backup.path);
    if (await file.exists()) {
      await file.delete();
    }

    _backupHistory.removeWhere((b) => b.id == backupId);
    await _saveBackupHistory();
    
    _eventBus.fire(BackupDeletedEvent(backup));
  }

  Future<void> _cleanupOldBackups() async {
    if (_backupHistory.length <= _config['max_backups']) return;

    final backupsToDelete = _backupHistory
        .sorted((a, b) => b.timestamp.compareTo(a.timestamp))
        .skip(_config['max_backups'])
        .toList();

    for (final backup in backupsToDelete) {
      await deleteBackup(backup.id);
    }
  }

  Future<void> _saveBackupHistory() async {
    await _storage.setObject('backup_history', {
      'backups': _backupHistory.map((b) => b.toJson()).toList(),
    });
  }

  List<BackupInfo> get backupHistory => List.unmodifiable(_backupHistory);
  bool get isBackupInProgress => _backupInProgress.value;
}

class BackupInfo {
  final String id;
  final DateTime timestamp;
  final String? description;
  final int size;
  final String path;

  BackupInfo({
    required this.id,
    required this.timestamp,
    this.description,
    required this.size,
    required this.path,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp.toIso8601String(),
    'description': description,
    'size': size,
    'path': path,
  };

  factory BackupInfo.fromJson(Map<String, dynamic> json) => BackupInfo(
    id: json['id'],
    timestamp: DateTime.parse(json['timestamp']),
    description: json['description'],
    size: json['size'],
    path: json['path'],
  );
}

class BackupException implements Exception {
  final String message;
  BackupException(this.message);
}

// 备份相关事件
class BackupStartedEvent extends AppEvent {}

class BackupCompletedEvent extends AppEvent {
  final BackupInfo backup;
  BackupCompletedEvent(this.backup);
}

class BackupFailedEvent extends AppEvent {
  final dynamic error;
  BackupFailedEvent(this.error);
}

class BackupDeletedEvent extends AppEvent {
  final BackupInfo backup;
  BackupDeletedEvent(this.backup);
}

class RestoreStartedEvent extends AppEvent {
  final BackupInfo backup;
  RestoreStartedEvent(this.backup);
}

class RestoreCompletedEvent extends AppEvent {
  final BackupInfo backup;
  RestoreCompletedEvent(this.backup);
}

class RestoreFailedEvent extends AppEvent {
  final BackupInfo backup;
  final dynamic error;
  RestoreFailedEvent(this.backup, this.error);
} 