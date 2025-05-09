import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';

/// 四诊会话仓库接口
abstract class DiagnosisRepository {
  /// 创建新的四诊会话
  Future<DiagnosisSession> createSession({
    required String userId,
    DiagnosisType initialType = DiagnosisType.comprehensive,
  });
  
  /// 获取指定ID的会话
  Future<DiagnosisSession?> getSessionById(String sessionId);
  
  /// 获取用户最近的会话
  Future<DiagnosisSession?> getLatestSessionByUserId(String userId);
  
  /// 获取用户的所有会话
  Future<List<DiagnosisSession>> getSessionsByUserId(String userId);
  
  /// 获取用户的活跃会话（未完成的会话）
  Future<List<DiagnosisSession>> getActiveSessionsByUserId(String userId);
  
  /// 更新会话信息
  Future<DiagnosisSession> updateSession(DiagnosisSession session);
  
  /// 更新会话状态
  Future<DiagnosisSession> updateSessionStatus(
    String sessionId, 
    DiagnosisSessionStatus status
  );
  
  /// 更新会话当前步骤
  Future<DiagnosisSession> updateSessionStep(
    String sessionId, 
    DiagnosisStep step
  );
  
  /// 完成会话特定步骤并记录数据
  Future<DiagnosisSession> completeSessionStep(
    String sessionId,
    DiagnosisStep step,
    Map<String, dynamic> stepData,
    {DiagnosisStep? nextStep}
  );
  
  /// 删除会话
  Future<bool> deleteSession(String sessionId);
  
  /// 保存舌象分析结果
  Future<TongueAnalysis> saveTongueAnalysis(TongueAnalysis analysis);
  
  /// 获取指定ID的舌象分析
  Future<TongueAnalysis?> getTongueAnalysisById(String analysisId);
  
  /// 获取用户最新的舌象分析
  Future<TongueAnalysis?> getLatestTongueAnalysisByUserId(String userId);
  
  /// 获取用户的所有舌象分析
  Future<List<TongueAnalysis>> getTongueAnalysesByUserId(String userId);
  
  /// 获取特定时间段内的舌象分析
  Future<List<TongueAnalysis>> getTongueAnalysesByTimeRange(
    String userId,
    DateTime startDate,
    DateTime endDate,
  );
  
  /// 更新舌象分析
  Future<TongueAnalysis> updateTongueAnalysis(TongueAnalysis analysis);
  
  /// 删除舌象分析
  Future<bool> deleteTongueAnalysis(String analysisId);
  
  /// 为舌象分析生成描述
  Future<String> generateTongueAnalysisDescription(TongueAnalysis analysis);
  
  /// 根据舌象分析推断可能的体质倾向
  Future<List<String>> inferConstitutionFromTongueAnalysis(TongueAnalysis analysis);
} 