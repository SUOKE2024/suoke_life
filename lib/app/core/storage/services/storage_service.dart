import 'package:get/get.dart';
import 'package:hive/hive.dart';
import 'package:path_provider/path_provider.dart';

/// 存储服务接口
abstract class IStorageService {
  /// 初始化存储服务
  Future<void> init();

  /// 读取字符串
  Future<String?> getString(String key);

  /// 写入字符串
  Future<void> setString(String key, String value);

  /// 读取布尔值
  Future<bool?> getBool(String key);
}

/// Hive存储服务实现
class StorageService extends GetxService implements IStorageService {
  // 初始化存储服务
  @override
  Future<void> init() async {
    final appDir = await getApplicationDocumentsDirectory();
    Hive.init(appDir.path);
  }
  
  // 注册适配器
  void registerAdapter<T>(TypeAdapter<T> adapter) {
    if (!Hive.isAdapterRegistered(adapter.typeId)) {
      Hive.registerAdapter(adapter);
    }
  }
  
  // 打开Box
  Future<Box<T>> openBox<T>(String name) async {
    if (Hive.isBoxOpen(name)) {
      return Hive.box<T>(name);
    }
    return await Hive.openBox<T>(name);
  }
  
  // 关闭Box
  Future<void> closeBox(String name) async {
    if (Hive.isBoxOpen(name)) {
      await Hive.box(name).close();
    }
  }
  
  // 关闭所有Box
  Future<void> closeAll() async {
    await Hive.close();
  }

  @override
  Future<String?> getString(String key) async {
    final box = await openBox<String>('settings');
    return box.get(key);
  }

  @override
  Future<void> setString(String key, String value) async {
    final box = await openBox<String>('settings');
    await box.put(key, value);
  }

  @override
  Future<bool?> getBool(String key) async {
    final box = await openBox<bool>('settings');
    return box.get(key);
  }
} 