import 'package:get/get.dart';
import 'dart:io';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'file_manager_service.dart';

class BackupService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final FileManagerService _fileManager = Get.find();

  final isBackingUp = false.obs;
  final backupProgress = 0.0.obs;
  final lastBackupTime = Rx<DateTime?>(null);

  // 创建备份
  Future<void> createBackup({String? description}) async {
    if (isBackingUp.value) return;

    try {
      isBackingUp.value = true;
      backupProgress.value = 0;

      // 收集需要备份的数据
      final backupData = await _collectBackupData();
      backupProgress.value = 0.3;

      // 压缩数据
      final compressedData = await _compressBackupData(backupData);
      backupProgress.value = 0.6;

      // 保存备份
      await _saveBackup(compressedData, description);
      backupProgress.value = 1.0;

      // 更新备份时间
      await _updateLastBackupTime();
    } catch (e) {
      await _loggingService.log('error', 'Failed to create backup', data: {'error': e.toString()});
      rethrow;
    } finally {
      isBackingUp.value = false;
    }
  }

  // 恢复备份
  Future<void> restoreBackup(String backupId) async {
    try {
      // 加载备份数据
      final backupData = await _loadBackup(backupId);
      
      // 解压数据
      final decompressedData = await _decompressBackupData(backupData);
      
      // 恢复数据
      await _restoreData(decompressedData);
      
      await _loggingService.log('info', 'Backup restored successfully', data: {'backup_id': backupId});
    } catch (e) {
      await _loggingService.log('error', 'Failed to restore backup', data: {'backup_id': backupId, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取备份列表
  Future<List<Map<String, dynamic>>> getBackupList() async {
    try {
      final data = await _storageService.getLocal('backups');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      await _loggingService.log('error', 'Failed to get backup list', data: {'error': e.toString()});
      return [];
    }
  }

  // 删除备份
  Future<void> deleteBackup(String backupId) async {
    try {
      final backups = await getBackupList();
      backups.removeWhere((backup) => backup['id'] == backupId);
      await _storageService.saveLocal('backups', backups);
      
      // 删除备份文件
      await _fileManager.delete(File('${(await _getBackupDirectory()).path}/$backupId.zip'));
    } catch (e) {
      await _loggingService.log('error', 'Failed to delete backup', data: {'backup_id': backupId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _collectBackupData() async {
    try {
      return {
        'user_data': await _storageService.getLocal('user_data'),
        'settings': await _storageService.getLocal('app_settings'),
        'health_records': await _storageService.getLocal('health_records'),
        'life_records': await _storageService.getLocal('life_records'),
        'chat_history': await _storageService.getLocal('chat_history'),
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> _compressBackupData(Map<String, dynamic> data) async {
    // TODO: 实现数据压缩
    return [];
  }

  Future<void> _saveBackup(List<int> data, String? description) async {
    try {
      final backupId = DateTime.now().millisecondsSinceEpoch.toString();
      final backupDir = await _getBackupDirectory();
      
      // 保存备份文件
      final backupFile = File('${backupDir.path}/$backupId.zip');
      await backupFile.writeAsBytes(data);
      
      // 更新备份记录
      final backups = await getBackupList();
      backups.add({
        'id': backupId,
        'description': description,
        'size': data.length,
        'created_at': DateTime.now().toIso8601String(),
      });
      
      await _storageService.saveLocal('backups', backups);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> _loadBackup(String backupId) async {
    try {
      final backupDir = await _getBackupDirectory();
      final backupFile = File('${backupDir.path}/$backupId.zip');
      return await backupFile.readAsBytes();
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _decompressBackupData(List<int> data) async {
    // TODO: 实现数据解压
    return {};
  }

  Future<void> _restoreData(Map<String, dynamic> data) async {
    try {
      for (final entry in data.entries) {
        await _storageService.saveLocal(entry.key, entry.value);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<Directory> _getBackupDirectory() async {
    final appDir = await _fileManager.currentDirectory.value;
    final backupDir = Directory('${appDir!.path}/backups');
    if (!await backupDir.exists()) {
      await backupDir.create();
    }
    return backupDir;
  }

  Future<void> _updateLastBackupTime() async {
    try {
      final now = DateTime.now();
      lastBackupTime.value = now;
      await _storageService.saveLocal('last_backup_time', now.toIso8601String());
    } catch (e) {
      rethrow;
    }
  }
} 