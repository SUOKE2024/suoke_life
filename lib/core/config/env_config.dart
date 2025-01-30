import 'package:envied/envied.dart';
import 'env_config_base.dart';

part 'env_config.g.dart';

@Envied(path: '.env', requireEnvFile: true)
abstract class EnvConfig implements EnvConfigBase {
  @EnviedField(varName: 'API_URL', defaultValue: 'https://api.suoke.life')
  static const String apiUrl = _EnvConfig.apiUrl;
  
  @EnviedField(varName: 'API_KEY')
  static const String apiKey = _EnvConfig.apiKey;
  
  @EnviedField(varName: 'AI_SERVICE_URL')
  static const String aiServiceUrl = _EnvConfig.aiServiceUrl;
  
  @EnviedField(varName: 'AI_API_KEY')
  static const String aiApiKey = _EnvConfig.aiApiKey;
  
  @EnviedField(varName: 'DB_NAME', defaultValue: 'suoke_life.db')
  static const String dbName = _EnvConfig.dbName;
  
  @EnviedField(varName: 'DB_VERSION', defaultValue: '1')
  static const String _dbVersion = _EnvConfig._dbVersion;
  
  @EnviedField(varName: 'ENV', defaultValue: 'development')
  static const String env = _EnvConfig.env;
  
  @EnviedField(varName: 'ENCRYPTION_KEY')
  static const String encryptionKey = _EnvConfig.encryptionKey;
  
  @override
  int get dbVersion => int.parse(_dbVersion);
}
