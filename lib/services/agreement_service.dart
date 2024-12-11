import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences.dart';
import '../core/network/http_client.dart';
import '../core/error/app_error.dart';
import '../models/agreement_update.dart';

class AgreementService {
  static final AgreementService _instance = AgreementService._internal();
  static AgreementService get instance => _instance;

  final _httpClient = HttpClient.instance;
  late final SharedPreferences _prefs;
  final Map<String, String> _cache = {};
  final _updateController = StreamController<AgreementUpdate>.broadcast();

  static const _cachePrefix = 'agreement_';
  static const _versionPrefix = 'agreement_version_';
  static const _updatePrefix = 'agreement_update_';
  
  Stream<AgreementUpdate> get updateStream => _updateController.stream;
  
  AgreementService._internal();

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    // 启动时检查所有协议更新
    _checkAllUpdates();
  }

  Future<void> _checkAllUpdates() async {
    try {
      final response = await _httpClient.get<List<dynamic>>(
        '/agreements/updates',
      );
      
      for (final item in response) {
        final update = AgreementUpdate.fromJson(item as Map<String, dynamic>);
        final localVersion = _prefs.getInt('$_versionPrefix${update.type}') ?? 0;
        
        if (update.version > localVersion) {
          // 检查是否已经提醒过这个版本
          final notifiedVersion = _prefs.getInt('$_updatePrefix${update.type}') ?? 0;
          if (update.version > notifiedVersion) {
            _updateController.add(update);
            // 记录已提醒的版本
            await _prefs.setInt('$_updatePrefix${update.type}', update.version);
          }
        }
      }
    } catch (e) {
      print('检查协议更新失败: $e');
    }
  }

  Future<String> getAgreement(String type) async {
    // 1. 先检查内存缓存
    if (_cache.containsKey(type)) {
      return _cache[type]!;
    }

    // 2. 检查本地存储
    final cachedContent = _prefs.getString('$_cachePrefix$type');
    if (cachedContent != null) {
      _cache[type] = cachedContent;
      
      // 异步检查更新
      _checkForUpdate(type);
      
      return cachedContent;
    }

    // 3. 从服务器加载
    return _fetchFromServer(type);
  }

  Future<void> _checkForUpdate(String type) async {
    try {
      final localVersion = _prefs.getInt('$_versionPrefix$type') ?? 0;
      
      final response = await _httpClient.get<Map<String, dynamic>>(
        '/agreements/$type/version',
      );
      
      final update = AgreementUpdate.fromJson(response);
      if (update.version > localVersion) {
        // 检查是否已经提醒过这个版本
        final notifiedVersion = _prefs.getInt('$_updatePrefix$type') ?? 0;
        if (update.version > notifiedVersion) {
          _updateController.add(update);
          // 记录已提醒的版本
          await _prefs.setInt('$_updatePrefix$type', update.version);
          // 有新版本,异步更新缓存
          _fetchFromServer(type);
        }
      }
    } catch (e) {
      print('检查协议更新失败: $e');
    }
  }

  Future<String> _fetchFromServer(String type) async {
    try {
      final response = await _httpClient.get<Map<String, dynamic>>(
        '/agreements/$type',
      );
      
      final content = response['content'] as String;
      final version = response['version'] as int;
      
      // 更新缓存
      _cache[type] = content;
      await _prefs.setString('$_cachePrefix$type', content);
      await _prefs.setInt('$_versionPrefix$type', version);
      
      return content;
    } catch (e) {
      throw BusinessError('加载协议内容失败: $e');
    }
  }

  Future<void> clearCache() async {
    _cache.clear();
    final keys = _prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith(_cachePrefix) || 
          key.startsWith(_versionPrefix) ||
          key.startsWith(_updatePrefix)) {
        await _prefs.remove(key);
      }
    }
  }

  void dispose() {
    _updateController.close();
  }
} 