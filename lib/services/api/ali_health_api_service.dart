import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../core/config/api_config.dart';

class AliHealthApiService {
  final ApiConfig _config = ApiConfig.instance;

  // 舌诊面诊分析
  Future<Map<String, dynamic>> analyzeTongueAndFace({
    required File tongueImage,
    required File faceImage,
  }) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_config.tongueFaceDiagnoseUrl),
      );

      request.headers.addAll({
        'Authorization': 'APPCODE ${_config.appCode}',
      });

      request.files.add(await http.MultipartFile.fromPath(
        'tongue_image',
        tongueImage.path,
      ));

      request.files.add(await http.MultipartFile.fromPath(
        'face_image',
        faceImage.path,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        throw Exception('舌诊面诊分析失败: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('舌诊面诊分析请求失败: $e');
    }
  }

  // 生命体征检测
  Future<Map<String, dynamic>> checkLifeSigns(File videoFile) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_config.lifeSignsCheckUrl),
      );

      request.headers.addAll({
        'Authorization': 'APPCODE ${_config.appCode}',
      });

      request.files.add(await http.MultipartFile.fromPath(
        'video',
        videoFile.path,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        throw Exception('生命体征检测失败: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('生命体征检测请求失败: $e');
    }
  }

  // 胆固醇检测
  Future<Map<String, dynamic>> checkCholesterol(File faceImage) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_config.cholesterolReportUrl),
      );

      request.headers.addAll({
        'Authorization': 'APPCODE ${_config.appCode}',
      });

      request.files.add(await http.MultipartFile.fromPath(
        'face_image',
        faceImage.path,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        throw Exception('胆固醇检测失败: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('胆固醇检测请求失败: $e');
    }
  }

  // 血压检测
  Future<Map<String, dynamic>> checkBloodPressure(File videoFile) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_config.bloodPressureReportUrl),
      );

      request.headers.addAll({
        'Authorization': 'APPCODE ${_config.appCode}',
      });

      request.files.add(await http.MultipartFile.fromPath(
        'video',
        videoFile.path,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        throw Exception('血压检测失败: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('血压检测请求失败: $e');
    }
  }

  // 抑郁检测
  Future<Map<String, dynamic>> checkDepression(File videoFile) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse(_config.depressionReportUrl),
      );

      request.headers.addAll({
        'Authorization': 'APPCODE ${_config.appCode}',
      });

      request.files.add(await http.MultipartFile.fromPath(
        'video',
        videoFile.path,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        throw Exception('抑郁检测失败: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('抑郁检测请求失败: $e');
    }
  }

  // 失眠问题评估
  Future<Map<String, dynamic>> assessInsomnia(Map<String, dynamic> answers) async {
    try {
      final response = await http.post(
        Uri.parse(_config.depressionInsomniaUrl),
        headers: {
          'Authorization': 'APPCODE ${_config.appCode}',
          'Content-Type': 'application/json',
        },
        body: json.encode(answers),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('失眠评估失败: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('失眠评估请求失败: $e');
    }
  }

  // 健康报告生成
  Future<Map<String, dynamic>> generateHealthReport(String diagnosisId) async {
    try {
      final response = await http.get(
        Uri.parse('${_config.tongueFaceReportUrl}?diagnosis_id=$diagnosisId'),
        headers: {
          'Authorization': 'APPCODE ${_config.appCode}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('健康报告生成失败: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('健康报告生成请求失败: $e');
    }
  }

  // 生命体征报告
  Future<Map<String, dynamic>> getLifeSignsReport(String checkId) async {
    try {
      final response = await http.get(
        Uri.parse('${_config.lifeSignsReportUrl}?check_id=$checkId'),
        headers: {
          'Authorization': 'APPCODE ${_config.appCode}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('生命体征报告获取失败: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('生命体征报告请求失败: $e');
    }
  }
} 