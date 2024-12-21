import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/elasticsearch/es_client.dart';

enum LogLevel {
  debug,
  info,
  warning,
  error,
  critical,
}

enum LogType {
  system,    // 系统日志
  business,  // 业务日志
  security,  // 安全日志
  operation, // 操作日志
}

class LogService {
  final KnowledgeDatabase _knowledgeDb;
  final ESClient _esClient;

  LogService(this._knowledgeDb, this._esClient);

  // 记录日志
  Future<void> log({
    required String message,
    required LogLevel level,
    required LogType type,
    String? userId,
    String? action,
    Map<String, dynamic>? metadata,
  }) async {
    final logEntry = {
      'message': message,
      'level': level.toString(),
      'type': type.toString(),
      'user_id': userId,
      'action': action,
      'metadata': metadata,
      'timestamp': DateTime.now().toIso8601String(),
    };

    // 1. 写入数据库
    await _knowledgeDb._conn.query('''
      INSERT INTO system_logs (
        message, level, type, user_id, action, metadata,
        created_at
      ) VALUES (?, ?, ?, ?, ?, ?, NOW())
    ''', [
      message,
      level.toString(),
      type.toString(),
      userId,
      action,
      metadata != null ? jsonEncode(metadata) : null,
    ]);

    // 2. 写入ES便于搜索
    await _esClient.index(
      index: 'logs',
      body: logEntry,
    );
  }

  // 查询日志
  Future<List<LogEntry>> queryLogs({
    LogLevel? level,
    LogType? type,
    String? userId,
    String? action,
    DateTime? startTime,
    DateTime? endTime,
    String? keyword,
    int from = 0,
    int size = 20,
  }) async {
    // 构建ES查询
    final query = {
      'bool': {
        'must': [],
        'filter': [],
      }
    };

    if (keyword != null) {
      query['bool']['must'].add({
        'multi_match': {
          'query': keyword,
          'fields': ['message', 'metadata.*'],
        }
      });
    }

    if (level != null) {
      query['bool']['filter'].add({
        'term': {'level': level.toString()}
      });
    }

    if (type != null) {
      query['bool']['filter'].add({
        'term': {'type': type.toString()}
      });
    }

    if (userId != null) {
      query['bool']['filter'].add({
        'term': {'user_id': userId}
      });
    }

    if (action != null) {
      query['bool']['filter'].add({
        'term': {'action': action}
      });
    }

    if (startTime != null || endTime != null) {
      final range = <String, String>{};
      if (startTime != null) {
        range['gte'] = startTime.toIso8601String();
      }
      if (endTime != null) {
        range['lte'] = endTime.toIso8601String();
      }
      query['bool']['filter'].add({
        'range': {'timestamp': range}
      });
    }

    final response = await _esClient.search(
      index: 'logs',
      body: {
        'query': query,
        'from': from,
        'size': size,
        'sort': [{'timestamp': 'desc'}],
      },
    );

    return (response['hits']['hits'] as List)
        .map((hit) => LogEntry.fromJson(hit['_source']))
        .toList();
  }

  // 清理过期日志
  Future<void> cleanupLogs(Duration retention) async {
    final cutoff = DateTime.now().subtract(retention);

    // 1. 清理数据库
    await _knowledgeDb._conn.query('''
      DELETE FROM system_logs 
      WHERE created_at < ?
    ''', [cutoff.toIso8601String()]);

    // 2. 清理ES
    await _esClient.deleteByQuery(
      index: 'logs',
      body: {
        'query': {
          'range': {
            'timestamp': {
              'lt': cutoff.toIso8601String(),
            }
          }
        }
      },
    );
  }
}

class LogEntry {
  final String message;
  final LogLevel level;
  final LogType type;
  final String? userId;
  final String? action;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  LogEntry({
    required this.message,
    required this.level,
    required this.type,
    this.userId,
    this.action,
    this.metadata,
    required this.timestamp,
  });

  factory LogEntry.fromJson(Map<String, dynamic> json) {
    return LogEntry(
      message: json['message'],
      level: LogLevel.values.byName(json['level']),
      type: LogType.values.byName(json['type']),
      userId: json['user_id'],
      action: json['action'],
      metadata: json['metadata'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
} 