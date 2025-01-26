import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  final String knowledgeGraphApiBaseUrl;
  final String llmApiBaseUrl;
  final String multimodalApiBaseUrl;

  AppConfig({
    required this.knowledgeGraphApiBaseUrl,
    required this.llmApiBaseUrl,
    required this.multimodalApiBaseUrl,
  });

  static String get appName => dotenv.env['APP_NAME'] ?? 'SuokeLife';
  static String get apiBaseUrl =>
      dotenv.env['API_BASE_URL'] ?? 'http://localhost:3000';
  static String get apiKey => dotenv.env['API_KEY'] ?? 'default_api_key';
  static String get redisHost => dotenv.env['REDIS_HOST'] ?? 'localhost';
  static int get redisPort => int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
  static String get redisPassword => dotenv.env['REDIS_PASSWORD'] ?? '';
  static String get llmServiceUrl =>
      dotenv.env['LLM_SERVICE_URL'] ??
      'http://localhost:5000/api/v1/llm/generate';
  static String get mysqlHost => dotenv.env['MYSQL_HOST'] ?? 'localhost';
  static int get mysqlPort => int.parse(dotenv.env['MYSQL_PORT'] ?? '3306');
  static String get mysqlUser => dotenv.env['MYSQL_USER'] ?? 'root';
  static String get mysqlDatabase =>
      dotenv.env['MYSQL_DATABASE'] ?? 'suoke_life';
  static const String baseUrl = 'http://118.31.223.213:8080';
  static const String dbName = 'suoke_life.db';
  static const int dbVersion = 1;
  static const bool dbEncryption = true;
  static const String dbPassword = 'your_db_password';
  static const bool enableDataContribution = false;
  static const String dataContributionApiEndpoint =
      'https://your-data-contribution-api.com/api/v1/contribute';
  static const String defaultLocalDataRetentionPeriod = '30d';
  static const bool enableKnowledgeGraph = true;
  // 其他配置项
}
