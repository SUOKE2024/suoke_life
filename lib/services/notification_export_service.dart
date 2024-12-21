import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/s3/s3_storage.dart';
import 'dart:convert';

class NotificationExportService {
  final KnowledgeDatabase _knowledgeDb;
  final S3Storage _s3Storage;

  NotificationExportService(this._knowledgeDb, this._s3Storage);

  // 导出通知数据
  Future<ExportResult> exportNotifications({
    DateTime? startTime,
    DateTime? endTime,
    NotificationType? type,
    String? format = 'json',
  }) async {
    // 获取通知数据
    final notifications = await _getNotifications(
      startTime: startTime,
      endTime: endTime,
      type: type,
    );

    // 转换数据格式
    final data = _convertFormat(notifications, format);

    // 上传到S3
    final key = _generateExportKey(format);
    await _s3Storage.putObject(
      bucket: 'notifications-export',
      key: key,
      data: data,
    );

    return ExportResult(
      fileUrl: await _s3Storage.getSignedUrl(
        bucket: 'notifications-export',
        key: key,
      ),
      format: format,
      count: notifications.length,
    );
  }

  // 获取通知数据
  Future<List<Notification>> _getNotifications({
    DateTime? startTime,
    DateTime? endTime,
    NotificationType? type,
  }) async {
    var query = 'SELECT * FROM notifications WHERE 1=1';
    final params = <dynamic>[];

    if (startTime != null) {
      query += ' AND created_at >= ?';
      params.add(startTime.toIso8601String());
    }

    if (endTime != null) {
      query += ' AND created_at <= ?';
      params.add(endTime.toIso8601String());
    }

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    query += ' ORDER BY created_at DESC';

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Notification.fromJson(r.fields)).toList();
  }

  // 转换数据格式
  dynamic _convertFormat(List<Notification> notifications, String? format) {
    return switch (format) {
      'json' => jsonEncode(notifications.map((n) => n.toJson()).toList()),
      'csv' => _convertToCsv(notifications),
      'xml' => _convertToXml(notifications),
      _ => throw ArgumentError('Unsupported format: $format'),
    };
  }

  // 生成导出键
  String _generateExportKey(String? format) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return 'exports/notifications_$timestamp.$format';
  }
}

class ExportResult {
  final String fileUrl;
  final String? format;
  final int count;

  ExportResult({
    required this.fileUrl,
    this.format,
    required this.count,
  });
} 