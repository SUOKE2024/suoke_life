import 'package:flutter_dotenv/flutter_dotenv.dart';

enum Environment {
  dev,
  staging,
  prod,
}

class EnvConfig {
  static Environment environment = Environment.dev;

  static Future<void> load() async {
    final envFile = _getEnvFileName();
    await dotenv.load(fileName: envFile);
  }

  static String _getEnvFileName() {
    switch (environment) {
      case Environment.dev:
        return '.env.dev';
      case Environment.staging:
        return '.env.staging';
      case Environment.prod:
        return '.env.prod';
    }
  }

  // HTTP 配置
  static bool get enableHttp2 => dotenv.get('ENABLE_HTTP2', fallback: 'false') == 'true';
  static bool get allowSelfSigned => dotenv.get('ALLOW_SELF_SIGNED', fallback: 'false') == 'true';
  static Duration get timeout => Duration(
    seconds: int.parse(dotenv.get('TIMEOUT', fallback: '30'))
  );

  // API 配置
  static String get apiUrl => dotenv.get('API_URL');
  static String get aiEndpoint => dotenv.get('AI_ENDPOINT');
  static String get doubaoApiUrl => dotenv.get('DOUBAO_API_URL');
  static String get doubaoApiKey => dotenv.get('DOUBAO_API_KEY');

  // Agent 配置
  static bool get enableAgent => dotenv.get('ENABLE_AGENT', fallback: 'false') == 'true';
  static String get agentEndpoint => dotenv.get('AGENT_ENDPOINT');
  static String get agentMode => dotenv.get('AGENT_MODE', fallback: 'production');

  // 日志配置
  static bool get enableLogging => dotenv.get('ENABLE_LOGGING', fallback: 'false') == 'true';
  static bool get enableNetworkLogging => dotenv.get('ENABLE_NETWORK_LOGGING', fallback: 'false') == 'true';
} 