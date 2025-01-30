import 'dart:convert';
import 'package:get/get.dart';
import '../models/sync_log.dart';
import 'storage_manager.dart';
import 'package:excel/excel.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

enum ExportFormat {
  csv,
  excel,
  json,
}

class SyncLogStorage extends GetxService {
  final _storage = Get.find<StorageManager>();
  static const _logsKey = 'sync_logs';
  static const _maxLogs = 1000; // 最多保存1000条日志

  Future<List<SyncLog>> getLogs() async {
    try {
      final json = _storage.getString(_logsKey);
      if (json == null) return [];

      final List<dynamic> list = jsonDecode(json);
      return list.map((item) => SyncLog.fromJson(item)).toList();
    } catch (e) {
      print('Failed to load sync logs: $e');
      return [];
    }
  }

  Future<void> addLog(SyncLog log) async {
    try {
      final logs = await getLogs();
      logs.insert(0, log);
      
      // 限制日志数量
      if (logs.length > _maxLogs) {
        logs.removeRange(_maxLogs, logs.length);
      }

      await _storage.setString(
        _logsKey,
        jsonEncode(logs.map((log) => log.toJson()).toList()),
      );
    } catch (e) {
      print('Failed to save sync log: $e');
    }
  }

  Future<void> clearLogs() async {
    try {
      await _storage.remove(_logsKey);
    } catch (e) {
      print('Failed to clear sync logs: $e');
    }
  }

  Future<String> exportLogs({ExportFormat format = ExportFormat.csv}) async {
    try {
      final logs = await getLogs();
      
      switch (format) {
        case ExportFormat.csv:
          return _exportToCsv(logs);
        case ExportFormat.excel:
          return _exportToExcel(logs);
        case ExportFormat.json:
          return _exportToJson(logs);
      }
    } catch (e) {
      throw Exception('导出日志失败: $e');
    }
  }

  String _exportToCsv(List<SyncLog> logs) {
    final csv = StringBuffer();
    
    // 添加CSV头
    csv.writeln('时间,类型,状态,记录数,详情');
    
    // 添加日志数据
    for (final log in logs) {
      csv.writeln([
        log.timestamp.toIso8601String(),
        log.type,
        log.status,
        log.recordCount,
        log.details.replaceAll(',', '，'), // 避免CSV分隔符冲突
      ].join(','));
    }
    
    return csv.toString();
  }

  Future<String> _exportToExcel(List<SyncLog> logs) async {
    final excel = Excel.createExcel();
    final sheet = excel['同步日志'];
    
    // 添加表头
    sheet.appendRow(['时间', '类型', '状态', '记录数', '详情']);
    
    // 添加数据
    for (final log in logs) {
      sheet.appendRow([
        log.timestamp.toIso8601String(),
        log.type,
        log.status,
        log.recordCount,
        log.details,
      ]);
    }
    
    // 保存为临时文件
    final tempDir = await getTemporaryDirectory();
    final file = File('${tempDir.path}/sync_logs_${DateTime.now().millisecondsSinceEpoch}.xlsx');
    await file.writeAsBytes(excel.encode()!);
    return file.path;
  }

  String _exportToJson(List<SyncLog> logs) {
    return const JsonEncoder.withIndent('  ').convert(
      logs.map((log) => log.toJson()).toList(),
    );
  }

  Future<SyncLogStats> getStats() async {
    final logs = await getLogs();
    return SyncLogStats.fromLogs(logs);
  }
} 