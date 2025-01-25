import 'package:suoke_life/core/models/life_record.dart';

abstract class LifeService {
  Future<List<LifeRecord>> getLifeRecords(String userId);
  Future<void> saveLifeRecord(LifeRecord record);
} 