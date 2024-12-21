import '../models/network_connection_record.dart';
import '../providers/database_provider.dart';

class NetworkHistoryRepository {
  final DatabaseProvider _db;

  NetworkHistoryRepository(this._db);

  Future<List<NetworkConnectionRecord>> getRecords({
    String? type,
    bool? isConnected,
    DateTime? startTime,
    DateTime? endTime,
    int? limit,
  }) async {
    final records = await _db.query(
      'network_history',
      where: _buildWhereClause(type, isConnected, startTime, endTime),
      whereArgs: _buildWhereArgs(type, isConnected, startTime, endTime),
      orderBy: 'timestamp DESC',
      limit: limit,
    );
    return records.map((json) => NetworkConnectionRecord.fromJson(json)).toList();
  }

  Future<void> addRecord(NetworkConnectionRecord record) async {
    await _db.insert('network_history', record.toJson());
  }

  Future<void> clearHistory() async {
    await _db.delete('network_history');
  }

  String? _buildWhereClause(
    String? type,
    bool? isConnected,
    DateTime? startTime,
    DateTime? endTime,
  ) {
    final conditions = <String>[];
    
    if (type != null) conditions.add('type = ?');
    if (isConnected != null) conditions.add('is_connected = ?');
    if (startTime != null) conditions.add('timestamp >= ?');
    if (endTime != null) conditions.add('timestamp <= ?');
    
    return conditions.isEmpty ? null : conditions.join(' AND ');
  }

  List<Object?> _buildWhereArgs(
    String? type,
    bool? isConnected,
    DateTime? startTime,
    DateTime? endTime,
  ) {
    final args = <Object?>[];
    
    if (type != null) args.add(type);
    if (isConnected != null) args.add(isConnected ? 1 : 0);
    if (startTime != null) args.add(startTime.toIso8601String());
    if (endTime != null) args.add(endTime.toIso8601String());
    
    return args;
  }
} 