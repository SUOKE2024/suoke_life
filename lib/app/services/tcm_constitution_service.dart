import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class TcmConstitutionService extends GetxService {
  final _storage = Get.find<StorageService>();
  final _tableName = 'tcm_constitutions';

  Future<void> saveConstitution(Map<String, dynamic> data) async {
    final id = data['id'] as String;
    await _storage.saveDB(_tableName, id, data);
  }

  Future<Map<String, dynamic>?> getConstitution(String id) async {
    return await _storage.getDB(_tableName, id);
  }

  Future<List<Map<String, dynamic>>> getAllConstitutions() async {
    return await _storage.getAllDB(_tableName);
  }

  Future<void> updateConstitution(String id, Map<String, dynamic> data) async {
    await _storage.updateDB(_tableName, id, data);
  }

  Future<void> deleteConstitution(String id) async {
    await _storage.deleteDB(_tableName, id);
  }
} 