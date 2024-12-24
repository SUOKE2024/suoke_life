import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class NotificationGroupService extends GetxService {
  final _storage = Get.find<StorageService>();
  final _tableName = 'notification_groups';

  Future<void> saveGroup(Map<String, dynamic> data) async {
    final id = data['id'] as String;
    await _storage.saveDB(_tableName, id, data);
  }

  Future<Map<String, dynamic>?> getGroup(String id) async {
    return await _storage.getDB(_tableName, id);
  }

  Future<List<Map<String, dynamic>>> getAllGroups() async {
    return await _storage.getAllDB(_tableName);
  }

  Future<void> updateGroup(String id, Map<String, dynamic> data) async {
    await _storage.updateDB(_tableName, id, data);
  }

  Future<void> deleteGroup(String id) async {
    await _storage.deleteDB(_tableName, id);
  }
} 