import '../models/life_record.dart';

abstract class LifeService {
  Future<List<LifeRecord>> getRecords();
  Future<void> addRecord({required LifeRecord record});
  Future<void> deleteRecord({required String id});
  Future<void> updateRecord({required LifeRecord record});
  Future<LifeRecord?> getRecord({required String id});
} 