import 'package:get/get.dart';

class AppConfig {
  static const String appName = 'SuoKe Life';
  static const String version = '1.0.0';
  
  // AI配置
  static const Map<String, dynamic> aiConfig = {
    'models': ['doubao-pro-32k', 'doubao-pro-128k', 'doubao-embedding'],
    'assistants': {
      'xiaoi': '生活管家和健康服务',
      'laoke': '知识顾问',
      'xiaoke': '商务助手'
    }
  };

  // 存储配置
  static const Map<String, dynamic> storageConfig = {
    'local': {
      'sqlite': {
        'name': 'suoke_life.db',
        'version': 1
      },
      'redis': {
        'host': 'localhost',
        'port': 6379
      }
    },
    'remote': {
      'mysql': {
        'host': 'rm-xxx.mysql.rds.aliyuncs.com',
        'port': 3306,
        'database': 'suoke_life'
      },
      'oss': {
        'endpoint': 'oss-cn-hangzhou.aliyuncs.com',
        'bucket': 'suoke-life'
      }
    }
  };
} 