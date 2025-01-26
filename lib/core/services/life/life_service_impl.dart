import 'package:suoke_life/core/services/infrastructure/database_service.dart';
import '../../models/life_record.dart';
import 'life_service.dart';

class LifeServiceImpl implements LifeService {
  final DatabaseService _databaseService;

  LifeServiceImpl(this._databaseService);

  static const String _lifeRecordTable = 'life_records';

  @override
  Future<List<LifeRecord>> getLifeRecords(String userId) async {
    final db = await _databaseService.database;
    final maps = await db.query(
      _lifeRecordTable,
      where: 'userId = ?',
      whereArgs: [userId],
    );
    return maps.map((map) => LifeRecord.fromMap(map)).toList();
  }

  @override
  Future<void> saveLifeRecord(LifeRecord record) async {
    final db = await _databaseService.database;
    await db.insert(_lifeRecordTable, record.toMap());
  }

  // LifeServiceImpl 的其他实现将在后续添加 (例如，如果 LifeService 接口有更多方法)
} 