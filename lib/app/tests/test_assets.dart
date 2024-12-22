import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

class TestAssets {
  static Future<void> loadTestImages() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    
    final defaultImage = Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, // PNG signature
      // ... 更多PNG图片数据
    ]);

    TestDefaultBinaryMessengerBinding.instance!.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (ByteData? message) async {
      final String key = utf8.decode(message!.buffer.asUint8List());
      
      switch (key) {
        case 'assets/images/xiaoai_avatar.png':
        case 'assets/images/laoke_avatar.png':
        case 'assets/images/xiaoke_avatar.png':
          return ByteData.view(defaultImage.buffer);
        default:
          return null;
      }
    });
  }
} 