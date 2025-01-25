import 'package:flutter/services.dart';

class MockAssetBundle extends AssetBundle {
  @override
  Future<ByteData> load(String key) async {
    // 返回一个空的 ByteData
    return ByteData(0);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    return '';
  }

  @override
  Future<T> loadStructuredData<T>(String key, Future<T> Function(String value) parser) async {
    return parser('');
  }
} 