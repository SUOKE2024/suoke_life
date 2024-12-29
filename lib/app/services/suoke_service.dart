import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class SuokeService extends GetxService {
  final StorageService _storageService;

  SuokeService({required StorageService storageService})
      : _storageService = storageService;

  Future<List<Map<String, dynamic>>> getServices(String type) async {
    final data = await _storageService.getLocal('${type}_services');
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(data as List);
  }
} 