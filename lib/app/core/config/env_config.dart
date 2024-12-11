import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig {
  static final instance = EnvConfig._();
  EnvConfig._();
  
  late final String apiUrl;
  late final String aiEndpoint;
  late final bool enableLogging;
  
  Future<void> load() async {
    final env = await dotenv.load();
    apiUrl = env['API_URL'] ?? 'https://api.default.com';
    aiEndpoint = env['AI_ENDPOINT'] ?? 'https://ai.default.com';
    enableLogging = env['ENABLE_LOGGING'] == 'true';
  }
} 