import 'package:redis/redis.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';

import 'dart:async';

// RedisServiceImpl 是 RedisService 接口的实现类
//
// 提供了连接 Redis, 设置/获取/删除 key-value 对等操作的具体实现
class RedisServiceImpl implements RedisService {
  RedisConnection? _connection;
  bool _isConnected = false;

  RedisServiceImpl();

  @override
  Future<void> connect() async {
    if (_isConnected) {
      return;
    }
    final host = dotenv.env['REDIS_HOST'] ?? 'localhost';
    final port = int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
    try {
      _connection = RedisConnection();
      await _connection!.connect(host, port);
      _isConnected = true;
      print('Redis connected to $host:$port');
    } catch (e) {
      print('Redis connection error: $e');
      _isConnected = false;
      _connection = null;
    }
  }

  @override
  Future<void> disconnect() async {
    if (_isConnected && _connection != null) {
      await _connection!.close();
      _isConnected = false;
      _connection = null;
      print('Redis disconnected');
    }
  }

  @override
  // 实现 RedisService 接口的 get 方法
  //
  // 根据 key 获取 Redis 中存储的 value
  //
  // [key] 要获取的 key
  Future<String?> get(String key) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform GET operation.');
        return null;
      }
    }
    try {
      final command = await _connection!.get(key);
      return command?.toString();
    } catch (e) {
      print('Redis GET error: $e');
      return null;
    }
  }

  @override
  // 实现 RedisService 接口的 set 方法
  //
  // 在 Redis 中设置 key-value 对，并可以设置过期时间
  //
  // [key] 要设置的 key
  // [value] 要设置的 value
  // [expiry] 可选的过期时间
  Future<void> set(String key, String value, {Duration? expiry}) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform SET operation.');
        return;
      }
    }
    try {
      if (expiry != null) {
        await _connection!.setex(key, expiry.inSeconds, value);
      } else {
        await _connection!.set(key, value);
      }
    } catch (e) {
      print('Redis SET error: $e');
    }
  }

  @override
  // 实现 RedisService 接口的 delete 方法
  //
  // 根据 key 删除 Redis 中存储的 key-value 对
  //
  // [key] 要删除的 key
  Future<void> delete(String key) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform DELETE operation.');
        return;
      }
    }
    try {
      await _connection!.del(key);
    } catch (e) {
      print('Redis DELETE error: $e');
    }
  }

  @override
  Future<void> hset(String key, String field, String value) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform HSET operation.');
        return;
      }
    }
    try {
      await _connection!.hset(key, field, value);
    } catch (e) {
      print('Redis HSET error: $e');
    }
  }

  @override
  Future<String?> hget(String key, String field) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform HGET operation.');
        return null;
      }
    }
    try {
      final command = await _connection!.hget(key, field);
      return command.toString();
    } catch (e) {
      print('Redis HGET error: $e');
      return null;
    }
  }

  @override
  Future<void> hdel(String key, String field) async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        print('Redis is not connected, cannot perform HDEL operation.');
        return;
      }
    }
    try {
      await _connection!.hdel(key, field);
    } catch (e) {
      print('Redis HDEL error: $e');
    }
  }
}
