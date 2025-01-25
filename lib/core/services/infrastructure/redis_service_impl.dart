import 'package:redis/redis.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';

import 'dart:async';

class RedisServiceImpl implements RedisService {
  RedisConnection? _connection;
  RedisCommander? _commander;

  @override
  Future<void> connect() async {
    _connection = await RedisConnection.connect(AppConfig.redisHost, AppConfig.redisPort);
    if (_connection != null) {
      _commander = RedisCommander(_connection!);
    }
  }

  @override
  Future<void> close() async {
    await _connection?.close();
    _connection = null;
    _commander = null;
  }

  @override
  Future<String?> get(String key) async {
    if (_connection == null) {
      await connect();
    }
    return await _connection?.get(key);
  }

  @override
  Future<void> set(String key, String value, {int? seconds}) async {
    if (_connection == null) {
      await connect();
    }
    if (seconds != null) {
      await _connection?.setex(key, seconds, value);
    } else {
      await _connection?.set(key, value);
    }
  }

  @override
  Future<void> delete(String key) async {
    if (_connection == null) {
      await connect();
    }
    await _connection?.del(key);
  }

  @override
  Future<void> hset(String key, String field, String value) async {
    if (_commander == null) {
      await connect();
    }
    await _commander?.hset(key, field, value);
  }

  @override
  Future<String?> hget(String key, String field) async {
    if (_commander == null) {
      await connect();
    }
    final response = await _commander?.hget(key, field);
    if (response != null) {
      return response.toString();
    }
    return null;
  }

  @override
  Future<void> hdel(String key, String field) async {
    if (_commander == null) {
      await connect();
    }
    await _commander?.hdel(key, field);
  }
} 