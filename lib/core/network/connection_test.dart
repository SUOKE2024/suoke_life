import 'dart:async';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:mysql1/mysql1.dart';
import '../config/app_config.dart';
import '../utils/logger.dart';

class ConnectionTest {
  static final Logger _logger = Logger('ConnectionTest');
  final String serverUrl;
  final String wsUrl;
  final String dbHost;
  final int dbPort;
  final String dbUser;
  final String dbPassword;
  final String dbName;

  ConnectionTest({
    this.serverUrl = 'http://118.31.223.213:8000',
    this.wsUrl = 'ws://118.31.223.213:8000/ws',
    this.dbHost = '118.31.223.213',
    this.dbPort = 3306,
    this.dbUser = 'suoke',
    this.dbPassword = 'Ht123!@#',
    this.dbName = 'suoke',
  });

  /// 测试HTTP连接
  Future<bool> testHttpConnection() async {
    try {
      final dio = Dio();
      dio.options.connectTimeout = const Duration(seconds: 5);
      dio.options.receiveTimeout = const Duration(seconds: 5);
      
      final response = await dio.get('$serverUrl/api/v1/health');
      _logger.info('HTTP连接测试结果: ${response.statusCode}');
      return response.statusCode == 200;
    } catch (e) {
      _logger.error('HTTP连接测试失败: $e');
      return false;
    }
  }

  /// 测试WebSocket连接
  Future<bool> testWebSocketConnection() async {
    try {
      final channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      await channel.ready.timeout(const Duration(seconds: 5));
      _logger.info('WebSocket连接成功');
      await channel.sink.close();
      return true;
    } catch (e) {
      _logger.error('WebSocket连接测试失败: $e');
      return false;
    }
  }

  /// 测试数据库连接
  Future<bool> testDatabaseConnection() async {
    try {
      final conn = await MySqlConnection.connect(
        ConnectionSettings(
          host: dbHost,
          port: dbPort,
          user: dbUser,
          password: dbPassword,
          db: dbName,
          timeout: const Duration(seconds: 5),
        ),
      );
      final results = await conn.query('SELECT 1');
      _logger.info('数据库连接成功: ${results.length} 行数据');
      await conn.close();
      return true;
    } catch (e) {
      _logger.error('数据库连接测试失败: $e');
      return false;
    }
  }

  /// 运行所有连接测试
  Future<Map<String, bool>> runAllTests() async {
    final results = <String, bool>{};
    
    _logger.info('开始连接测试...');
    
    // HTTP测试
    results['http'] = await testHttpConnection();
    _logger.info('HTTP连接状态: ${results['http']}');
    
    // WebSocket测试
    results['websocket'] = await testWebSocketConnection();
    _logger.info('WebSocket连接状态: ${results['websocket']}');
    
    // 数据库测试
    results['database'] = await testDatabaseConnection();
    _logger.info('数据库连接状态: ${results['database']}');
    
    return results;
  }
} 