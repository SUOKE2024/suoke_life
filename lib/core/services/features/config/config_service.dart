// import 'package:injectable/injectable.dart';
import 'package:logger/logger.dart';

class ConfigService {
  final StorageService _storage;
  final NetworkService _network;
  final Logger _logger = Logger();

  ConfigService(this._storage, this._network);

  Future<Map<String, dynamic>> getConfig() async {
    _logger.i('Fetching configuration');
    // 先读取本地配置
    final localConfig = await _storage.get<Map<String, dynamic>>('app_config');
    if (localConfig != null) {
      _logger.i('Local configuration found: $localConfig');
      return localConfig;
    }

    // 获取远程配置
    final remoteConfig = (await _network.get('/config')).data;
    _logger.i('Remote configuration fetched: $remoteConfig');
    await _storage.set('app_config', remoteConfig);
    return remoteConfig;
  }
} 