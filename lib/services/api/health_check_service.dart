import 'dart:io';
import 'base_api_service.dart';
import '../../core/config/api_config.dart';

class HealthCheckService extends BaseApiService {
  final ApiConfig _config = ApiConfig.instance;
  
  HealthCheckService() : super(
    appKey: ApiConfig.instance.appKey,
    appSecret: ApiConfig.instance.appSecret,
    appCode: ApiConfig.instance.appCode,
  );

  // 舌诊面诊分析
  Future<Map<String, dynamic>> analyzeTongueAndFace({
    required File tongueImage,
    required File faceImage,
  }) async {
    final body = {
      'tongue_image': await _encodeImage(tongueImage),
      'face_image': await _encodeImage(faceImage),
    };
    
    return await post(_config.tongueFaceDiagnoseUrl, body);
  }

  // 获取舌诊面诊报告
  Future<Map<String, dynamic>> getTongueAndFaceReport(String diagnosisId) async {
    return await get('${_config.tongueFaceReportUrl}?diagnosis_id=$diagnosisId');
  }

  // 生命体征检测
  Future<Map<String, dynamic>> checkLifeSigns(File videoFile) async {
    final body = {
      'video': await _encodeVideo(videoFile),
    };
    
    return await post(_config.lifeSignsCheckUrl, body);
  }

  // 获取生命体征报告
  Future<Map<String, dynamic>> getLifeSignsReport(String checkId) async {
    return await get('${_config.lifeSignsReportUrl}?check_id=$checkId');
  }

  // 胆固醇检测
  Future<Map<String, dynamic>> getCholesterolReport(File faceImage) async {
    final body = {
      'face_image': await _encodeImage(faceImage),
    };
    
    return await post(_config.cholesterolReportUrl, body);
  }

  // 血压检测
  Future<Map<String, dynamic>> getBloodPressureReport(File videoFile) async {
    final body = {
      'video': await _encodeVideo(videoFile),
    };
    
    return await post(_config.bloodPressureReportUrl, body);
  }

  // 抑郁检测报告
  Future<Map<String, dynamic>> getDepressionReport(File videoFile) async {
    final body = {
      'video': await _encodeVideo(videoFile),
    };
    
    return await post(_config.depressionReportUrl, body);
  }

  // 失眠问题评估
  Future<Map<String, dynamic>> getInsomniaAssessment(Map<String, dynamic> answers) async {
    return await post(_config.depressionInsomniaUrl, answers);
  }

  // 工具方法：编码图片文件为base64
  Future<String> _encodeImage(File file) async {
    List<int> imageBytes = await file.readAsBytes();
    return base64Encode(imageBytes);
  }

  // 工具方法：编码视频文件为base64
  Future<String> _encodeVideo(File file) async {
    List<int> videoBytes = await file.readAsBytes();
    return base64Encode(videoBytes);
  }
} 