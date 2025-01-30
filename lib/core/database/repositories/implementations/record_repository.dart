import '../models/record.dart';
import '../providers/database_provider.dart';

class RecordRepository {
  final DatabaseProvider _db;

  RecordRepository(this._db);

  Future<List<Record>> getRecentRecords({int limit = 10}) async {
    final records = await _db.query(
      'records',
      orderBy: 'created_at DESC',
      limit: limit,
    );
    return records.map((json) => Record.fromJson(json)).toList();
  }

  Future<Record> getRecord(String id) async {
    final record = await _db.queryOne(
      'records',
      where: 'id = ?',
      whereArgs: [id],
    );
    return Record.fromJson(record);
  }

  Future<void> saveRecord(Record record) async {
    await _db.insert('records', record.toJson());
  }

  Future<void> updateRecord(Record record) async {
    await _db.update(
      'records',
      record.toJson(),
      where: 'id = ?',
      whereArgs: [record.id],
    );
  }

  Future<void> deleteRecord(String id) async {
    await _db.delete(
      'records',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Record>> searchRecords(String keyword) async {
    final records = await _db.query(
      'records',
      where: 'title LIKE ? OR content LIKE ?',
      whereArgs: ['%$keyword%', '%$keyword%'],
      orderBy: 'created_at DESC',
    );
    return records.map((json) => Record.fromJson(json)).toList();
  }
} 