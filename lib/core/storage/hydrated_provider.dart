import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 可持久化的Provider状态接口
abstract class HydratedState {
  /// 将状态转换为JSON
  Map<String, dynamic> toJson();
  
  /// 从JSON创建状态
  static HydratedState fromJson(Map<String, dynamic> json) {
    throw UnimplementedError('必须在子类中实现fromJson');
  }
}

/// 可持久化的StateNotifier
abstract class HydratedStateNotifier<T extends HydratedState> extends StateNotifier<T> {
  /// 存储键前缀
  static const String _keyPrefix = 'hydrated_state_';
  
  /// 共享首选项实例
  static SharedPreferences? _preferences;
  
  /// 初始化共享首选项
  static Future<void> initialize() async {
    _preferences ??= await SharedPreferences.getInstance();
  }
  
  /// 构造函数
  HydratedStateNotifier(super.state) {
    // 尝试从存储中恢复状态
    _loadState();
  }
  
  /// 获取存储键
  String get storageKey => '$_keyPrefix${runtimeType.toString()}';
  
  /// 从JSON创建状态
  T? fromJson(Map<String, dynamic> json);
  
  /// 将状态转换为JSON
  Map<String, dynamic> toJson(T state) => state.toJson();
  
  /// 加载状态
  Future<void> _loadState() async {
    await initialize();
    
    final jsonString = _preferences?.getString(storageKey);
    if (jsonString != null) {
      try {
        final json = jsonDecode(jsonString) as Map<String, dynamic>;
        final loadedState = fromJson(json);
        if (loadedState != null) {
          state = loadedState;
        }
      } catch (e) {
        print('加载持久化状态失败: $e');
      }
    }
  }
  
  /// 保存状态
  Future<void> _saveState() async {
    await initialize();
    
    try {
      final json = toJson(state);
      final jsonString = jsonEncode(json);
      await _preferences?.setString(storageKey, jsonString);
    } catch (e) {
      print('保存持久化状态失败: $e');
    }
  }
  
  @override
  set state(T value) {
    super.state = value;
    _saveState();
  }
  
  /// 清除持久化状态
  Future<void> clearPersistedState() async {
    await initialize();
    await _preferences?.remove(storageKey);
  }
  
  /// 清除所有持久化状态
  static Future<void> clearAllPersistedState() async {
    await initialize();
    
    final keys = _preferences?.getKeys() ?? {};
    for (final key in keys) {
      if (key.startsWith(_keyPrefix)) {
        await _preferences?.remove(key);
      }
    }
  }
} 