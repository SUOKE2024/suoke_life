import 'package:suoke_life/core/models/life_record.dart';

abstract class LifeService {
  Future<List<LifeRecord>> getLifeRecords(String userId);
  Future<void> saveLifeRecord(LifeRecord record);
  // 这里可以定义 LifeService 接口的方法，例如：
  // Future<LifeData> getLifeData(String userId);
  // Future<LifeRecord> getLifeRecord(String recordId);
  // Future<void> recordLifeActivity(LifeActivity activity);
} 