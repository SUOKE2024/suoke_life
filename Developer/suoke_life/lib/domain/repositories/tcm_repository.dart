import 'package:suoke_life/domain/entities/tcm/tcm_diagnosis_result.dart';

abstract class TcmRepository {
  /// 提交多模态诊断
  /// 
  /// [tongueImage] 舌诊图像（Base64编码）
  /// [faceImage] 面诊图像（Base64编码）
  /// [audioData] 语音数据（Base64编码）
  /// [description] 文字描述
  Future<TcmDiagnosisResult> submitMultimodalDiagnosis({
    String? tongueImage,
    String? faceImage,
    String? audioData,
    String? description,
  });

  /// 获取诊断历史
  Future<List<TcmDiagnosisResult>> getDiagnosisHistory({
    required int page,
    required int pageSize,
  });

  /// 获取特定诊断结果
  Future<TcmDiagnosisResult> getDiagnosisById(String id);
}