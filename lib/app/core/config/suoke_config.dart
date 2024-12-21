class SuokeConfig {
  // 健康服务 API
  static const String healthApiUrl = 'https://api.suoke.health/v1';
  static const String healthApiKey = 'your_health_api_key';
  
  // 农产品服务 API
  static const String agriApiUrl = 'https://api.suoke.agri/v1';
  static const String agriApiKey = 'your_agri_api_key';
  
  // 第三方 API 服务
  static const Map<String, Map<String, String>> thirdPartyApis = {
    'ali_health': {
      'url': 'https://api.alihealth.cn/v1',
      'key': 'your_ali_health_key',
    },
    'tcm_diagnosis': {
      'url': 'https://api.tcm.cn/v1',
      'key': 'your_tcm_key',
    },
  };

  // 服务类型配置
  static const Map<String, Map<String, dynamic>> services = {
    'health_survey': {
      'name': '健康问卷',
      'type': 'health',
      'api': 'health',
      'icon': 'assets/icons/health_survey.png',
    },
    'tcm_constitution': {
      'name': '体质检测',
      'type': 'health',
      'api': 'tcm_diagnosis',
      'icon': 'assets/icons/tcm.png',
    },
    'agri_product': {
      'name': '农产品预制',
      'type': 'agri',
      'api': 'agri',
      'icon': 'assets/icons/agri.png',
    },
  };

  // API 请求配置
  static const Duration timeout = Duration(seconds: 30);
  static const int maxRetries = 3;
} 