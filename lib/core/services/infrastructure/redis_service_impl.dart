import 'package:redis/redis.dart' as redis;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/lib/core/services/infrastructure/redis_service.dart';

import 'dart:async';

// RedisServiceImpl 是 RedisService 接口的实现类
//
// 提供了连接 Redis, 设置/获取/删除 key-value 对等操作的具体实现
class RedisServiceImpl implements RedisService {
  redis.RedisConnection? _connection;
  bool _isConnected = false;

  RedisServiceImpl() {
    init();
  }

  @override
  Future<void> init() async {
    if (_isConnected && _connection != null)
      return;
    final host = dotenv.env['REDIS_HOST'] ?? 'localhost';
    final port = int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
    try {
      _connection = await redis.RedisConnection.connect(host, port);
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
    if (_isConnected && _connection != null)
      try {
        await _connection!.close();
        _isConnected = false;
        _connection = null;
        print('Redis disconnected');
      } catch (e) {
        print('Error disconnecting from Redis: $e');
      }
  }

  Future<redis.RedisConnection> get connection async {
    if (!_isConnected || _connection == null)
      await init();
    if (!_isConnected || _connection == null)
      throw Exception('Redis is not connected');

    return _connection!;
  }

  @override
  // 实现 RedisService 接口的 get 方法
  //
  // 根据 key 获取 Redis 中存储的 value
  //
  // [key] 要获取的 key
  Future<String?> get(String key) async {
    final conn = await connection;
    final command = await conn.sendObject(['GET', key]);
    return command as String?;
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
    final conn = await connection;
    if (conn == null) throw Exception('Redis connection not established');
    if (expiry != null) {
      await conn.sendObject(['SETEX', key, expiry.inSeconds, value]);
    } else {
      await conn.sendObject(['SET', key, value]);
    }
  }

  @override
  // 实现 RedisService 接口的 delete 方法
  //
  // 根据 key 删除 Redis 中存储的 key-value 对
  //
  // [key] 要删除的 key
  Future<void> delete(String key) async {
    final conn = await connection;
    if (conn == null) throw Exception('Redis connection not established');
    await conn.sendObject(['DEL', key]);
  }

  @override
  Future<void> hset(String key, String field, String value) async {
    final conn = await connection;
    if (conn == null) throw Exception('Redis connection not established');
    await conn.sendObject(['HSET', key, field, value]);
  }

  @override
  Future<String?> hget(String key, String field) async {
    final conn = await connection;
    if (conn == null) throw Exception('Redis connection not established');
    final response = await conn.sendObject(['HGET', key, field]);
    return response as String?;
  }

  @override
  Future<void> hdel(String key, String field) async {
    final conn = await connection;
    if (conn == null) throw Exception('Redis connection not established');
    await conn.sendObject(['HDEL', key, field]);
  }
}
