import 'env_config.dart';

class ApiConfig {
  final String appKey;
  final String appSecret;
  final String appCode;
  
  // 舌诊面诊API
  final String tongueFaceDiagnoseUrl;
  final String tongueFaceReportUrl;
  
  // 生命体征检测API
  final String lifeSignsCheckUrl;
  final String lifeSignsReportUrl;
  
  // 胆固醇检测API
  final String cholesterolReportUrl;
  
  // 血压检测API
  final String bloodPressureReportUrl;
  
  // 心理检测API
  final String depressionReportUrl;
  final String depressionInsomniaUrl;

  ApiConfig._({
    required this.appKey,
    required this.appSecret,
    required this.appCode,
    required this.tongueFaceDiagnoseUrl,
    required this.tongueFaceReportUrl,
    required this.lifeSignsCheckUrl,
    required this.lifeSignsReportUrl,
    required this.cholesterolReportUrl,
    required this.bloodPressureReportUrl,
    required this.depressionReportUrl,
    required this.depressionInsomniaUrl,
  });

  static ApiConfig? _instance;

  static ApiConfig get instance {
    _instance ??= ApiConfig._fromEnv();
    return _instance!;
  }

  factory ApiConfig._fromEnv() {
    return ApiConfig._(
      appKey: EnvConfig.get('ALI_APP_KEY'),
      appSecret: EnvConfig.get('ALI_APP_SECRET'),
      appCode: EnvConfig.get('ALI_APP_CODE'),
      tongueFaceDiagnoseUrl: EnvConfig.get('TONGUE_FACE_DIAGNOSE_URL'),
      tongueFaceReportUrl: EnvConfig.get('TONGUE_FACE_REPORT_URL'),
      lifeSignsCheckUrl: EnvConfig.get('LIFE_SIGNS_CHECK_URL'),
      lifeSignsReportUrl: EnvConfig.get('LIFE_SIGNS_REPORT_URL'),
      cholesterolReportUrl: EnvConfig.get('CHOLESTEROL_REPORT_URL'),
      bloodPressureReportUrl: EnvConfig.get('BLOOD_PRESSURE_REPORT_URL'),
      depressionReportUrl: EnvConfig.get('DEPRESSION_REPORT_URL'),
      depressionInsomniaUrl: EnvConfig.get('DEPRESSION_INSOMNIA_URL'),
    );
  }
} 