import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'storage_interface.dart';

class GetStorageService extends GetxService implements IStorageService {
  late final GetStorage _box;
  
  @override
  Future<void> init() async {
    await GetStorage.init();
    _box = GetStorage();
  }
  
  @override
  Future<void> write(String key, dynamic value) async {
    await _box.write(key, value);
  }
  
  @override
  T? read<T>(String key) {
    return _box.read<T>(key);
  }
  
  @override
  Future<void> remove(String key) async {
    await _box.remove(key);
  }
  
  @override
  Future<void> clear() async {
    await _box.erase();
  }
} 