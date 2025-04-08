import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/four_diagnostic_data.dart';

/// 四诊数据存储库接口
///
/// 定义中医四诊数据的存储和查询操作
abstract class DiagnosticRepository {
  /// 保存四诊数据
  Future<void> saveDiagnosticData(FourDiagnosticData data);
  
  /// 通过ID获取四诊数据
  Future<FourDiagnosticData> getDiagnosticDataById(String id);
  
  /// 获取用户的所有四诊数据
  Future<List<FourDiagnosticData>> getUserDiagnosticData(String userId);
  
  /// 删除四诊数据
  Future<void> deleteDiagnosticData(String id);
  
  /// 通过日期范围检索用户的四诊数据
  Future<List<FourDiagnosticData>> getUserDiagnosticDataByDateRange(
      String userId, DateTime startDate, DateTime endDate);
  
  /// 获取最新的四诊数据
  Future<FourDiagnosticData?> getLatestDiagnosticData(String userId);
  
  /// 上传四诊照片（如舌诊、面诊照片）
  Future<List<String>> uploadDiagnosticImages(String diagnosisId, List<String> localImagePaths);
  
  /// 分析四诊数据，生成诊断结论
  Future<String> analyzeDiagnosticData(FourDiagnosticData data);
  
  /// 获取舌诊分析结果
  Future<Map<String, dynamic>> analyzeTongueImage(String imagePath);
  
  /// 获取面诊分析结果
  Future<Map<String, dynamic>> analyzeFacialImage(String imagePath);
  
  /// 语音转文字（用于问诊记录）
  Future<String> speechToText(String audioPath);
}

/// 四诊数据存储库provider
final diagnosticRepositoryProvider = Provider<DiagnosticRepository>((ref) {
  throw UnimplementedError('DiagnosticRepository必须由数据层实现提供');
}); 