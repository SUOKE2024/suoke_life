import '../data/remote/mysql/knowledge_database.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

enum AuditAction {
  create,     // 创建通知
  send,       // 发送通知
  deliver,    // 投递通知
  read,       // 阅读通知
  delete,     // 删除通知
  archive,    // 归档通知
  restore,    // 恢复通知
}

class ESClient {
  final String baseUrl;
  final http.Client _client;

  ESClient({
    required this.baseUrl,
    http.Client? client,
  }) : _client = client ?? http.Client();

  Future<Map<String, dynamic>> search({
    required String index,
    required Map<String, dynamic> body,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/$index/_search'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to search ES: ${response.body}');
    }
  }

  Future<void> index({
    required String index,
    required Map<String, dynamic> body,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/$index/_doc'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode != 201) {
      throw Exception('Failed to index document: ${response.body}');
    }
  }
}

class NotificationAuditService {
  final KnowledgeDatabase _knowledgeDb;
  final ESClient _esClient;

  NotificationAuditService(this._knowledgeDb, this._esClient);

  // 记录审计日志
  Future<void> logAudit({
    required String notificationId,
    required AuditAction action,
    required String userId,
    String? details,
    Map<String, dynamic>? metadata,
  }) async {
    final auditLog = {
      'notification_id': notificationId,
      'action': action.toString(),
      'user_id': userId,
      'details': details,
      'metadata': metadata,
      'ip_address': await _getClientIp(),
      'user_agent': await _getUserAgent(),
      'timestamp': DateTime.now().toIso8601String(),
    };

    // 1. 写入数据库
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_audit_logs (
        notification_id, action, user_id, details,
        metadata, ip_address, user_agent, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      notificationId,
      action.toString(),
      userId,
      details,
      metadata != null ? jsonEncode(metadata) : null,
      auditLog['ip_address'],
      auditLog['user_agent'],
    ]);

    // 2. 写入ES便于搜索
    await _esClient.index(
      index: 'notification_audit_logs',
      body: auditLog,
    );
  }

  // 查询审计日志
  Future<List<AuditLog>> queryAuditLogs({
    String? notificationId,
    AuditAction? action,
    String? userId,
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
          'fields': ['details', 'metadata.*'],
        }
      });
    }

    if (notificationId != null) {
      query['bool']['filter'].add({
        'term': {'notification_id': notificationId}
      });
    }

    if (action != null) {
      query['bool']['filter'].add({
        'term': {'action': action.toString()}
      });
    }

    if (userId != null) {
      query['bool']['filter'].add({
        'term': {'user_id': userId}
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
      index: 'notification_audit_logs',
      body: {
        'query': query,
        'from': from,
        'size': size,
        'sort': [{'timestamp': 'desc'}],
      },
    );

    return (response['hits']['hits'] as List)
        .map((hit) => AuditLog.fromJson(hit['_source']))
        .toList();
  }

  // 获取操作统计
  Future<Map<AuditAction, int>> getActionStats({
    DateTime? startTime,
    DateTime? endTime,
    String? userId,
  }) async {
    var query = '''
      SELECT action, COUNT(*) as count
      FROM notification_audit_logs
      WHERE 1=1
    ''';
    final params = <String>[];

    if (startTime != null) {
      query += ' AND created_at >= ?';
      params.add(startTime.toIso8601String());
    }

    if (endTime != null) {
      query += ' AND created_at <= ?';
      params.add(endTime.toIso8601String());
    }

    if (userId != null) {
      query += ' AND user_id = ?';
      params.add(userId);
    }

    query += ' GROUP BY action';

    final results = await _knowledgeDb._conn.query(query, params);
    
    return Map.fromEntries(
      results.map((r) => MapEntry(
        AuditAction.values.byName(r['action']),
        r['count'] as int,
      )),
    );
  }

  // 获取用户操作历史
  Future<List<AuditLog>> getUserActionHistory(
    String userId, {
    int limit = 20,
    int offset = 0,
  }) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_audit_logs
      WHERE user_id = ?
      ORDER BY created_at DESC
      LIMIT ? OFFSET ?
    ''', [userId, limit, offset]);

    return results.map((r) => AuditLog.fromJson(r.fields)).toList();
  }

  // 获取客户端IP
  Future<String> _getClientIp() async {
    // TODO: 实现获取客户端IP的逻辑
    return '127.0.0.1';
  }

  // 获取User Agent
  Future<String> _getUserAgent() async {
    // TODO: 实现获取User Agent的逻辑
    return 'Unknown';
  }
}

class AuditLog {
  final String notificationId;
  final AuditAction action;
  final String userId;
  final String? details;
  final Map<String, dynamic>? metadata;
  final String ipAddress;
  final String userAgent;
  final DateTime createdAt;

  AuditLog({
    required this.notificationId,
    required this.action,
    required this.userId,
    this.details,
    this.metadata,
    required this.ipAddress,
    required this.userAgent,
    required this.createdAt,
  });

  factory AuditLog.fromJson(Map<String, dynamic> json) {
    return AuditLog(
      notificationId: json['notification_id'],
      action: AuditAction.values.byName(json['action']),
      userId: json['user_id'],
      details: json['details'],
      metadata: json['metadata'],
      ipAddress: json['ip_address'],
      userAgent: json['user_agent'],
      createdAt: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'notification_id': notificationId,
      'action': action.toString(),
      'user_id': userId,
      'details': details,
      'metadata': metadata,
      'ip_address': ipAddress,
      'user_agent': userAgent,
      'timestamp': createdAt.toIso8601String(),
    };
  }
} 