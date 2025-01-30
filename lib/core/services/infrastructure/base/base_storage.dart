import 'package:get/get.dart';
import 'package:hive/hive.dart';

abstract class BaseStorage<T> extends GetxService {
  late Box<T> _box;
  
  // 初始化存储
  Future<void> init(String boxName) async {
    _box = await Hive.openBox<T>(boxName);
  }
  
  // 获取所有数据
  List<T> getAll() {
    return _box.values.toList();
  }
  
  // 添加数据
  Future<void> add(T item) async {
    await _box.add(item);
  }
  
  // 更新数据
  Future<void> update(int index, T item) async {
    await _box.putAt(index, item);
  }
  
  // 删除数据
  Future<void> delete(int index) async {
    await _box.deleteAt(index);
  }
  
  // 清空数据
  Future<void> clear() async {
    await _box.clear();
  }
} 