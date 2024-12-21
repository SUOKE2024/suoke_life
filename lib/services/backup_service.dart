import 'package:get/get.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'dart:io';
import 'dart:convert';
import 'package:archive/archive.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'package:suoke_life/services/tag_service.dart';
import 'package:suoke_life/services/settings_service.dart';

class BackupService extends GetxService {
  final LifeRecordService _recordService = Get.find();
  final TagService _tagService = Get.find();
  final SettingsService _settingsService = Get.find();

  // 创建备份
  Future<File> createBackup() async {
    final backupData = {
      'records': _recordService.getAllRecords(),
      'tags': _tagService.getCustomTags(),
      'settings': {
        'theme': _settingsService.getThemeMode().toString(),
        'locale': _settingsService.getLocale()?.toString(),
        'notifications': _settingsService.getNotificationSettings(),
      },
      'timestamp': DateTime.now().toIso8601String(),
    };

    // 转换为JSON
    final jsonData = json.encode(backupData);
    
    // 压缩数据
    final encoder = ZipEncoder();
    final archive = Archive();
    archive.addFile(
      ArchiveFile('backup.json', jsonData.length, jsonData.codeUnits),
    );
    final zipData = encoder.encode(archive);

    // 保存到文件
    final dir = await getApplicationDocumentsDirectory();
    final backupFile = File('${dir.path}/backup.zip');
    await backupFile.writeAsBytes(zipData!);

    return backupFile;
  }

  // 恢复备份
  Future<void> restoreBackup(File backupFile) async {
    try {
      // 读取并解压文件
      final bytes = await backupFile.readAsBytes();
      final archive = ZipDecoder().decodeBytes(bytes);
      final jsonData = String.fromCharCodes(archive.first.content);
      final data = json.decode(jsonData);

      // 恢复记录
      await _recordService.clearAll();
      for (var record in data['records']) {
        await _recordService.addRecord(record);
      }

      // 恢复标签
      await _tagService.clearAll();
      for (var tag in data['tags']) {
        await _tagService.addCustomTag(tag);
      }

      // 恢复设置
      final settings = data['settings'];
      if (settings != null) {
        await _settingsService.setThemeMode(ThemeMode.values.firstWhere(
          (e) => e.toString() == settings['theme'],
          orElse: () => ThemeMode.system,
        ));
        if (settings['locale'] != null) {
          final parts = settings['locale'].split('_');
          await _settingsService.setLocale(
            Locale(parts[0], parts.length > 1 ? parts[1] : null),
          );
        }
        await _settingsService.setNotificationSettings(
          Map<String, bool>.from(settings['notifications']),
        );
      }

      Get.snackbar('成功', '备份恢复成功');
    } catch (e) {
      Get.snackbar('错误', '备份恢复失败: $e');
    }
  }

  // 分享备份
  Future<void> shareBackup() async {
    try {
      final backupFile = await createBackup();
      await Share.shareXFiles(
        [XFile(backupFile.path)],
        text: '索克生活数据备份',
      );
    } catch (e) {
      Get.snackbar('错误', '备份分享失败: $e');
    }
  }
} 