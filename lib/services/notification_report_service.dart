import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';
import 'package:excel/excel.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

enum ReportType {
  daily,      // 日报
  weekly,     // 周报
  monthly,    // 月报
  custom,     // 自定义
}

enum ReportFormat {
  excel,      // Excel格式
  pdf,        // PDF格式
  csv,        // CSV格式
}

class NotificationReportService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;

  NotificationReportService(this._knowledgeDb, this._redisCache);

  // 生成报表
  Future<ReportResult> generateReport({
    required ReportType type,
    required ReportFormat format,
    DateTime? startTime,
    DateTime? endTime,
    NotificationType? notificationType,
    ChannelType? channel,
  }) async {
    // 1. 获取报表时间范围
    final dateRange = _getDateRange(type, startTime, endTime);
    
    // 2. 获取报表数据
    final data = await _getReportData(
      startTime: dateRange.start,
      endTime: dateRange.end,
      notificationType: notificationType,
      channel: channel,
    );

    // 3. 生成报表文件
    final report = switch (format) {
      ReportFormat.excel => await _generateExcelReport(data),
      ReportFormat.pdf => await _generatePdfReport(data),
      ReportFormat.csv => await _generateCsvReport(data),
    };

    // 4. 保存报表记录
    final reportId = await _saveReportRecord(
      type: type,
      format: format,
      startTime: dateRange.start,
      endTime: dateRange.end,
      filePath: report.filePath,
    );

    return ReportResult(
      id: reportId,
      filePath: report.filePath,
      fileSize: report.fileSize,
      format: format,
    );
  }

  // 获取报表列表
  Future<List<ReportRecord>> getReports({
    ReportType? type,
    DateTime? startTime,
    DateTime? endTime,
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT * FROM notification_reports
      WHERE 1=1
    ''';
    final params = <dynamic>[];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    if (startTime != null) {
      query += ' AND start_time >= ?';
      params.add(startTime.toIso8601String());
    }

    if (endTime != null) {
      query += ' AND end_time <= ?';
      params.add(endTime.toIso8601String());
    }

    query += ' ORDER BY created_at DESC';

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => ReportRecord.fromJson(r.fields)).toList();
  }

  // 获取报表数据
  Future<ReportData> _getReportData({
    required DateTime startTime,
    required DateTime endTime,
    NotificationType? notificationType,
    ChannelType? channel,
  }) async {
    // 1. 获取通知统计
    final stats = await _getNotificationStats(
      startTime: startTime,
      endTime: endTime,
      type: notificationType,
      channel: channel,
    );

    // 2. 获取渠道统计
    final channelStats = await _getChannelStats(
      startTime: startTime,
      endTime: endTime,
      type: notificationType,
    );

    // 3. 获取用户统计
    final userStats = await _getUserStats(
      startTime: startTime,
      endTime: endTime,
      type: notificationType,
      channel: channel,
    );

    // 4. 获取趋势数据
    final trends = await _getTrendData(
      startTime: startTime,
      endTime: endTime,
      type: notificationType,
      channel: channel,
    );

    return ReportData(
      stats: stats,
      channelStats: channelStats,
      userStats: userStats,
      trends: trends,
      startTime: startTime,
      endTime: endTime,
    );
  }

  // 生成Excel报表
  Future<GeneratedReport> _generateExcelReport(ReportData data) async {
    final excel = Excel.createExcel();

    // 1. 添加概览sheet
    final overviewSheet = excel['Overview'];
    overviewSheet.appendRow([
      '报表时间范围',
      '${data.startTime.toString()} - ${data.endTime.toString()}',
    ]);
    overviewSheet.appendRow([
      '总通知数',
      data.stats.totalCount.toString(),
    ]);
    // ... 添加更多概览数据

    // 2. 添加渠道统计sheet
    final channelSheet = excel['Channel Stats'];
    channelSheet.appendRow([
      '渠道',
      '发送数量',
      '送达率',
      '阅读率',
    ]);
    for (final entry in data.channelStats.entries) {
      channelSheet.appendRow([
        entry.key.toString(),
        entry.value.totalCount.toString(),
        '${(entry.value.deliveryRate * 100).toStringAsFixed(2)}%',
        '${(entry.value.readRate * 100).toStringAsFixed(2)}%',
      ]);
    }

    // 3. 添加趋势sheet
    final trendSheet = excel['Trends'];
    trendSheet.appendRow([
      '时间',
      '发送数量',
      '阅读数量',
    ]);
    for (final trend in data.trends) {
      trendSheet.appendRow([
        trend.timeSlot.toString(),
        trend.count.toString(),
        trend.readCount.toString(),
      ]);
    }

    // 4. 保存文件
    final bytes = excel.encode()!;
    final filePath = 'reports/notification_report_${DateTime.now().millisecondsSinceEpoch}.xlsx';
    // TODO: 保存文件到存储系统

    return GeneratedReport(
      filePath: filePath,
      fileSize: bytes.length,
    );
  }

  // 生成PDF报表
  Future<GeneratedReport> _generatePdfReport(ReportData data) async {
    final pdf = pw.Document();

    // 1. 添加封面
    pdf.addPage(
      pw.Page(
        build: (context) => pw.Center(
          child: pw.Column(
            mainAxisAlignment: pw.MainAxisAlignment.center,
            children: [
              pw.Text(
                '通知系统报表',
                style: pw.TextStyle(
                  fontSize: 24,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
              pw.SizedBox(height: 20),
              pw.Text(
                '${data.startTime.toString()} - ${data.endTime.toString()}',
              ),
            ],
          ),
        ),
      ),
    );

    // 2. 添加概览页
    pdf.addPage(
      pw.Page(
        build: (context) => pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.start,
          children: [
            pw.Text('统计概览', style: pw.TextStyle(fontSize: 18)),
            pw.SizedBox(height: 20),
            _buildPdfTable([
              ['指标', '数值'],
              ['总通知数', data.stats.totalCount.toString()],
              ['已读数', data.stats.readCount.toString()],
              ['用户数', data.stats.userCount.toString()],
              ['平均阅读时间', '${data.stats.avgReadTime?.toStringAsFixed(2) ?? "N/A"} 秒'],
            ]),
          ],
        ),
      ),
    );

    // 3. 添加渠道统计页
    // 4. 添加趋势图页
    // ... 添加更多页面

    // 5. 保存文件
    final bytes = await pdf.save();
    final filePath = 'reports/notification_report_${DateTime.now().millisecondsSinceEpoch}.pdf';
    // TODO: 保存文件到存储系统

    return GeneratedReport(
      filePath: filePath,
      fileSize: bytes.length,
    );
  }

  // 生成CSV报表
  Future<GeneratedReport> _generateCsvReport(ReportData data) async {
    final buffer = StringBuffer();

    // 1. 添加头信息
    buffer.writeln('通知系统报表');
    buffer.writeln('时间范围: ${data.startTime} - ${data.endTime}');
    buffer.writeln();

    // 2. 添加概览数据
    buffer.writeln('统计概览');
    buffer.writeln('总通知数,${data.stats.totalCount}');
    buffer.writeln('已读数,${data.stats.readCount}');
    buffer.writeln('用户数,${data.stats.userCount}');
    buffer.writeln('平均阅读时间,${data.stats.avgReadTime?.toStringAsFixed(2) ?? "N/A"}');
    buffer.writeln();

    // 3. 添加渠道统计
    buffer.writeln('渠道统计');
    buffer.writeln('渠道,发送数量,送达率,阅读率');
    for (final entry in data.channelStats.entries) {
      buffer.writeln(
        '${entry.key},'
        '${entry.value.totalCount},'
        '${(entry.value.deliveryRate * 100).toStringAsFixed(2)}%,'
        '${(entry.value.readRate * 100).toStringAsFixed(2)}%'
      );
    }
    buffer.writeln();

    // 4. 添加趋势数据
    buffer.writeln('趋势数据');
    buffer.writeln('时间,发送数量,阅读数量');
    for (final trend in data.trends) {
      buffer.writeln(
        '${trend.timeSlot},'
        '${trend.count},'
        '${trend.readCount}'
      );
    }

    // 5. 保存文件
    final bytes = buffer.toString().codeUnits;
    final filePath = 'reports/notification_report_${DateTime.now().millisecondsSinceEpoch}.csv';
    // TODO: 保存文件到存储系统

    return GeneratedReport(
      filePath: filePath,
      fileSize: bytes.length,
    );
  }

  // 构建PDF表格
  pw.Widget _buildPdfTable(List<List<String>> data) {
    return pw.Table(
      border: pw.TableBorder.all(),
      children: data.map((row) {
        return pw.TableRow(
          children: row.map((cell) {
            return pw.Padding(
              padding: const pw.EdgeInsets.all(8),
              child: pw.Text(cell),
            );
          }).toList(),
        );
      }).toList(),
    );
  }

  // 获取报表时间范围
  DateTimeRange _getDateRange(
    ReportType type,
    DateTime? startTime,
    DateTime? endTime,
  ) {
    if (type == ReportType.custom && startTime != null && endTime != null) {
      return DateTimeRange(start: startTime, end: endTime);
    }

    final now = DateTime.now();
    return switch (type) {
      ReportType.daily => DateTimeRange(
          start: DateTime(now.year, now.month, now.day),
          end: now,
        ),
      ReportType.weekly => DateTimeRange(
          start: now.subtract(Duration(days: now.weekday - 1)),
          end: now,
        ),
      ReportType.monthly => DateTimeRange(
          start: DateTime(now.year, now.month, 1),
          end: now,
        ),
      ReportType.custom => throw ArgumentError(
          'Custom report type requires startTime and endTime',
        ),
    };
  }

  // 保存报表记录
  Future<String> _saveReportRecord({
    required ReportType type,
    required ReportFormat format,
    required DateTime startTime,
    required DateTime endTime,
    required String filePath,
  }) async {
    final reportId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_reports (
        id, type, format, start_time, end_time,
        file_path, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, NOW())
    ''', [
      reportId,
      type.toString(),
      format.toString(),
      startTime.toIso8601String(),
      endTime.toIso8601String(),
      filePath,
    ]);

    return reportId;
  }
}

class ReportResult {
  final String id;
  final String filePath;
  final int fileSize;
  final ReportFormat format;

  ReportResult({
    required this.id,
    required this.filePath,
    required this.fileSize,
    required this.format,
  });
}

class GeneratedReport {
  final String filePath;
  final int fileSize;

  GeneratedReport({
    required this.filePath,
    required this.fileSize,
  });
}

class ReportRecord {
  final String id;
  final ReportType type;
  final ReportFormat format;
  final DateTime startTime;
  final DateTime endTime;
  final String filePath;
  final DateTime createdAt;

  ReportRecord({
    required this.id,
    required this.type,
    required this.format,
    required this.startTime,
    required this.endTime,
    required this.filePath,
    required this.createdAt,
  });

  factory ReportRecord.fromJson(Map<String, dynamic> json) {
    return ReportRecord(
      id: json['id'],
      type: ReportType.values.byName(json['type']),
      format: ReportFormat.values.byName(json['format']),
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      filePath: json['file_path'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class ReportData {
  final NotificationStats stats;
  final Map<ChannelType, ChannelStats> channelStats;
  final UserStats userStats;
  final List<NotificationTrend> trends;
  final DateTime startTime;
  final DateTime endTime;

  ReportData({
    required this.stats,
    required this.channelStats,
    required this.userStats,
    required this.trends,
    required this.startTime,
    required this.endTime,
  });
}

class DateTimeRange {
  final DateTime start;
  final DateTime end;

  DateTimeRange({
    required this.start,
    required this.end,
  });
} 