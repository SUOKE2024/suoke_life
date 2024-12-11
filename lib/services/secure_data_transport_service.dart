import 'dart:async';
import 'dart:convert';
import 'package:encrypt/encrypt.dart';
import '../core/network/websocket_client.dart';
import '../core/network/http_client.dart';

class SecureDataTransportService {
  final WebSocketClient _wsClient;
  final HttpClient _httpClient;
  late final Encrypter _encrypter;
  late final IV _iv;
  
  final StreamController<Map<String, dynamic>> _secureDataController = 
      StreamController<Map<String, dynamic>>.broadcast();

  SecureDataTransportService({
    required WebSocketClient wsClient,
    required HttpClient httpClient,
    required String encryptionKey,
  }) : _wsClient = wsClient,
       _httpClient = httpClient {
    _initializeEncryption(encryptionKey);
  }

  void _initializeEncryption(String key) {
    // 使用AES-256加密
    final keyBytes = Key.fromUtf8(key.padRight(32, '0'));
    _iv = IV.fromLength(16);
    _encrypter = Encrypter(AES(keyBytes));
  }

  Future<void> sendSecureData({
    required String endpoint,
    required Map<String, dynamic> data,
    required String dataType,
    Map<String, String>? headers,
  }) async {
    try {
      // 添加元数据
      final payload = {
        'type': dataType,
        'timestamp': DateTime.now().toIso8601String(),
        'data': data,
      };

      // 加密数据
      final jsonStr = jsonEncode(payload);
      final encrypted = _encrypter.encrypt(jsonStr, iv: _iv);

      // 构建安全头部
      final secureHeaders = {
        'Content-Type': 'application/octet-stream',
        'X-Encryption-IV': base64.encode(_iv.bytes),
        'X-Data-Type': dataType,
        ...?headers,
      };

      // 发送加密数据
      if (endpoint.startsWith('ws')) {
        await _sendViaWebSocket(endpoint, encrypted, secureHeaders);
      } else {
        await _sendViaHttp(endpoint, encrypted, secureHeaders);
      }
    } catch (e) {
      print('发送加密数据失败: $e');
      rethrow;
    }
  }

  Future<void> _sendViaWebSocket(
    String endpoint,
    Encrypted encrypted,
    Map<String, String> headers,
  ) async {
    final message = {
      'payload': encrypted.base64,
      'headers': headers,
    };
    await _wsClient.send(message);
  }

  Future<void> _sendViaHttp(
    String endpoint,
    Encrypted encrypted,
    Map<String, String> headers,
  ) async {
    final response = await _httpClient.post(
      Uri.parse(endpoint),
      headers: headers,
      body: encrypted.bytes,
    );

    if (response.statusCode != 200) {
      throw Exception('发送失败: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> receiveSecureData(
    List<int> encryptedData,
    String ivBase64,
  ) async {
    try {
      // 解密数据
      final iv = IV.fromBase64(ivBase64);
      final encrypted = Encrypted(Uint8List.fromList(encryptedData));
      final decrypted = _encrypter.decrypt(encrypted, iv: iv);

      // 解析JSON
      final data = jsonDecode(decrypted);
      _secureDataController.add(data);
      
      return data;
    } catch (e) {
      print('解密数据失败: $e');
      rethrow;
    }
  }

  // 用于批量加密
  Future<List<Map<String, dynamic>>> encryptBatch(
    List<Map<String, dynamic>> dataList,
  ) async {
    return Future.wait(
      dataList.map((data) async {
        final jsonStr = jsonEncode(data);
        final encrypted = _encrypter.encrypt(jsonStr, iv: _iv);
        
        return {
          'payload': encrypted.base64,
          'iv': base64.encode(_iv.bytes),
          'timestamp': DateTime.now().toIso8601String(),
        };
      }),
    );
  }

  // 用于批量解密
  Future<List<Map<String, dynamic>>> decryptBatch(
    List<Map<String, dynamic>> encryptedDataList,
  ) async {
    return Future.wait(
      encryptedDataList.map((encryptedData) async {
        final encrypted = Encrypted.fromBase64(encryptedData['payload']);
        final iv = IV.fromBase64(encryptedData['iv']);
        final decrypted = _encrypter.decrypt(encrypted, iv: iv);
        
        return jsonDecode(decrypted);
      }),
    );
  }

  void dispose() {
    _secureDataController.close();
  }

  // Getters
  Stream<Map<String, dynamic>> get secureDataStream => 
      _secureDataController.stream;
} 