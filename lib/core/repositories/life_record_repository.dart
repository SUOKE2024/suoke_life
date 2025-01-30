import 'package:suoke_life/lib/core/models/life_record.dart';

abstract class LifeRecordRepository {
  Future<List<LifeRecord>> getLifeRecords(String userId);
  Future<void> saveLifeRecord(LifeRecord record);
} 