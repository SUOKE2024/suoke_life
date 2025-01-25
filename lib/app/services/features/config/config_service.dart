import 'package:injectable/injectable.dart';

@lazySingleton
class ConfigService {
  final StorageService _storage;
  final NetworkService _network;

  ConfigService(this._storage, this._network);

  Future<Map<String, dynamic>> getConfig() async {
    // 先读取本地配置
    final localConfig = await _storage.get<Map<String, dynamic>>('app_config');
    if (localConfig != null) return localConfig;

    // 获取远程配置
    final remoteConfig = (await _network.get('/config')).data;
    await _storage.set('app_config', remoteConfig);
    return remoteConfig;
  }
} 