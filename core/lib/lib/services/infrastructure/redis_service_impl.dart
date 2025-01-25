import 'package:core/services/infrastructure/redis_service.dart';
import 'package:redis/redis.dart';
import 'package:core/config/app_config.dart';
import 'package:get_it/get_it.dart';

class RedisServiceImpl implements RedisService {
  final AppConfig _appConfig = GetIt.instance<AppConfig>();
  Command? _command;
  PubSub? _pubSub;

  @override
  Future<void> init() async {
    final conn = RedisConnection();
    _command = await conn.connect(_appConfig.redisHost, _appConfig.redisPort);
    _pubSub = PubSub(_command!);
  }

  @override
  Future<void> set(String key, String value, {Duration? expiry}) async {
    if (_command == null) throw Exception('RedisService not initialized');
    await _command!.send_object(['SET', key, value]);
    if (expiry != null) {
      await _command!.send_object(['EXPIRE', key, expiry.inSeconds]);
    }
  }

  @override
  Future<String?> get(String key) async {
    if (_command == null) throw Exception('RedisService not initialized');
    final result = await _command!.get(key);
    return result;
  }

  @override
  Future<void> delete(String key) async {
    if (_command == null) throw Exception('RedisService not initialized');
    await _command!.send_object(['DEL', key]);
  }

  @override
  Future<bool> exists(String key) async {
    if (_command == null) throw Exception('RedisService not initialized');
    final result = await _command!.send_object(['EXISTS', key]);
    return result == 1;
  }

  @override
  Future<void> publish(String channel, String message) async {
    if (_command == null) throw Exception('RedisService not initialized');
    await _command!.send_object(['PUBLISH', channel, message]);
  }

  @override
  Stream<String> subscribe(String channel) {
    if (_pubSub == null) throw Exception('RedisService not initialized');
    _pubSub!.subscribe([channel]);
    return _pubSub!.getStream().map((message) => message.toString());
  }
} 