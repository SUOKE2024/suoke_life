import 'package:ali_oss/ali_oss.dart';

class OssStorage {
  late OSSClient _client;
  
  Future<void> init() async {
    _client = OSSClient(
      endpoint: 'your-endpoint',
      accessKeyId: 'your-access-key',
      accessKeySecret: 'your-secret-key',
      bucket: 'suoke-life'
    );
  }

  // 上传多媒体资源
  Future<String> uploadMedia(String filePath, String category) async {
    final key = 'media/$category/${DateTime.now().millisecondsSinceEpoch}';
    await _client.putObject(key, filePath);
    return key;
  }

  // 上传应用资源
  Future<String> uploadAppResource(String filePath, String type) async {
    final key = 'app/$type/${DateTime.now().millisecondsSinceEpoch}';
    await _client.putObject(key, filePath);
    return key;
  }
} 