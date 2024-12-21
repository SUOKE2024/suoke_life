import 'package:get/get.dart';
import '../data/models/life_record.dart';
import '../core/storage/storage_service.dart';

class LifeService extends GetxService {
  final StorageService _storageService = Get.find();

  Future<List<LifeRecord>> getLifeRecords() async {
    try {
      final data = await _storageService.getLocal('life_records');
      return (data as List).map((e) => LifeRecord.fromJson(e)).toList();
    } catch (e) {
      return [];
    }
  }

  Future<void> addLifeRecord(LifeRecord record) async {
    try {
      final records = await getLifeRecords();
      records.insert(0, record);
      await _storageService.saveLocal('life_records', records.map((e) => e.toJson()).toList());
      
      // 同步到远程
      if (record.isSync) {
        await _storageService.saveRemote('life_record_${record.id}', record.toJson());
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> deleteLifeRecord(String id) async {
    try {
      final records = await getLifeRecords();
      records.removeWhere((record) => record.id == id);
      await _storageService.saveLocal('life_records', records.map((e) => e.toJson()).toList());
      
      // 同步删除远程
      await _storageService.removeRemote('life_record_$id');
    } catch (e) {
      rethrow;
    }
  }
} 