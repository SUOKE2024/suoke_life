import 'package:get/get.dart';
import '../../core/services/base_service.dart';
import '../../../data/models/life_record.dart';

class LifeService extends GetxService implements BaseService {
  final records = <LifeRecord>[].obs;
  
  @override
  Future<void> init() async {
    await loadRecords();
  }

  @override
  Future<void> dispose() async {
    records.clear();
  }

  Future<void> loadRecords() async {
    // TODO: 从存储加载记录
  }

  Future<void> addRecord(LifeRecord record) async {
    records.add(record);
    // TODO: 保存到存储
  }

  Future<void> deleteRecord(String id) async {
    records.removeWhere((record) => record.id == id);
    // TODO: 从存储删除
  }
} 