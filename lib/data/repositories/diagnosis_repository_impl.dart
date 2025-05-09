import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';
import 'package:suoke_life/domain/repositories/diagnosis_repository.dart';
import 'package:uuid/uuid.dart';
import 'package:logger/logger.dart';

/// 四诊会话仓库实现
class DiagnosisRepositoryImpl implements DiagnosisRepository {
  /// 本地存储的会话数据
  final Map<String, DiagnosisSession> _localSessions = {};
  
  /// 本地存储的舌象分析数据
  final Map<String, TongueAnalysis> _localTongueAnalyses = {};
  
  /// 日志记录器
  final Logger _logger = Logger();

  /// 构造函数
  DiagnosisRepositoryImpl();

  @override
  Future<DiagnosisSession> createSession({
    required String userId,
    DiagnosisType initialType = DiagnosisType.comprehensive,
  }) async {
    try {
      // 创建新会话
      final session = DiagnosisSession.create(
        userId: userId,
        initialType: initialType,
      );
      
      // 存储到本地
      _localSessions[session.id] = session;
      
      // TODO: 同步到远程数据库
      
      return session;
    } catch (e) {
      _logger.e('创建四诊会话失败', error: e);
      throw Exception('创建四诊会话失败: $e');
    }
  }

  @override
  Future<DiagnosisSession?> getSessionById(String sessionId) async {
    try {
      // 先从本地查找
      if (_localSessions.containsKey(sessionId)) {
        return _localSessions[sessionId];
      }
      
      // TODO: 从远程数据库获取
      
      return null;
    } catch (e) {
      _logger.e('获取四诊会话失败', error: e);
      return null;
    }
  }

  @override
  Future<DiagnosisSession?> getLatestSessionByUserId(String userId) async {
    try {
      // 从本地查找用户的所有会话
      final userSessions = _localSessions.values
          .where((session) => session.userId == userId)
          .toList();
      
      // 按创建时间排序
      userSessions.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      
      // 返回最新的会话
      return userSessions.isNotEmpty ? userSessions.first : null;
    } catch (e) {
      _logger.e('获取用户最新四诊会话失败', error: e);
      return null;
    }
  }

  @override
  Future<List<DiagnosisSession>> getSessionsByUserId(String userId) async {
    try {
      // 从本地查找用户的所有会话
      final userSessions = _localSessions.values
          .where((session) => session.userId == userId)
          .toList();
      
      // 按创建时间排序
      userSessions.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      
      return userSessions;
    } catch (e) {
      _logger.e('获取用户所有四诊会话失败', error: e);
      return [];
    }
  }

  @override
  Future<List<DiagnosisSession>> getActiveSessionsByUserId(String userId) async {
    try {
      // 从本地查找用户的所有活跃会话
      final activeSessions = _localSessions.values
          .where((session) => 
              session.userId == userId && 
              (session.status == DiagnosisSessionStatus.inProgress || 
               session.status == DiagnosisSessionStatus.paused))
          .toList();
      
      // 按更新时间排序
      activeSessions.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
      
      return activeSessions;
    } catch (e) {
      _logger.e('获取用户活跃四诊会话失败', error: e);
      return [];
    }
  }

  @override
  Future<DiagnosisSession> updateSession(DiagnosisSession session) async {
    try {
      // 确保会话ID存在
      if (!_localSessions.containsKey(session.id)) {
        throw Exception('四诊会话不存在');
      }
      
      // 更新本地会话数据
      _localSessions[session.id] = session.copyWith(
        updatedAt: DateTime.now(),
      );
      
      // TODO: 同步到远程数据库
      
      return _localSessions[session.id]!;
    } catch (e) {
      _logger.e('更新四诊会话失败', error: e);
      throw Exception('更新四诊会话失败: $e');
    }
  }

  @override
  Future<DiagnosisSession> updateSessionStatus(
    String sessionId, 
    DiagnosisSessionStatus status
  ) async {
    try {
      // 确保会话ID存在
      if (!_localSessions.containsKey(sessionId)) {
        throw Exception('四诊会话不存在');
      }
      
      // 更新状态
      final updatedSession = _localSessions[sessionId]!.copyWith(
        status: status,
        updatedAt: DateTime.now(),
      );
      
      // 保存更新后的会话
      _localSessions[sessionId] = updatedSession;
      
      // TODO: 同步到远程数据库
      
      return updatedSession;
    } catch (e) {
      _logger.e('更新四诊会话状态失败', error: e);
      throw Exception('更新四诊会话状态失败: $e');
    }
  }

  @override
  Future<DiagnosisSession> updateSessionStep(
    String sessionId, 
    DiagnosisStep step
  ) async {
    try {
      // 确保会话ID存在
      if (!_localSessions.containsKey(sessionId)) {
        throw Exception('四诊会话不存在');
      }
      
      // 更新当前步骤
      final updatedSession = _localSessions[sessionId]!.copyWith(
        currentStep: step,
        updatedAt: DateTime.now(),
      );
      
      // 保存更新后的会话
      _localSessions[sessionId] = updatedSession;
      
      // TODO: 同步到远程数据库
      
      return updatedSession;
    } catch (e) {
      _logger.e('更新四诊会话步骤失败', error: e);
      throw Exception('更新四诊会话步骤失败: $e');
    }
  }

  @override
  Future<DiagnosisSession> completeSessionStep(
    String sessionId,
    DiagnosisStep step,
    Map<String, dynamic> stepData,
    {DiagnosisStep? nextStep}
  ) async {
    try {
      // 确保会话ID存在
      if (!_localSessions.containsKey(sessionId)) {
        throw Exception('四诊会话不存在');
      }
      
      // 获取当前会话
      final session = _localSessions[sessionId]!;
      
      // 标记步骤为已完成并更新数据
      final updatedSession = session.completeStep(
        step,
        stepData,
        nextStep: nextStep,
      );
      
      // 保存更新后的会话
      _localSessions[sessionId] = updatedSession;
      
      // TODO: 同步到远程数据库
      
      return updatedSession;
    } catch (e) {
      _logger.e('完成四诊会话步骤失败', error: e);
      throw Exception('完成四诊会话步骤失败: $e');
    }
  }

  @override
  Future<bool> deleteSession(String sessionId) async {
    try {
      // 确保会话ID存在
      if (!_localSessions.containsKey(sessionId)) {
        return false;
      }
      
      // 从本地删除
      _localSessions.remove(sessionId);
      
      // TODO: 从远程数据库删除
      
      return true;
    } catch (e) {
      _logger.e('删除四诊会话失败', error: e);
      return false;
    }
  }

  @override
  Future<TongueAnalysis> saveTongueAnalysis(TongueAnalysis analysis) async {
    try {
      // 存储到本地
      _localTongueAnalyses[analysis.id] = analysis;
      
      // TODO: 同步到远程数据库
      
      return analysis;
    } catch (e) {
      _logger.e('保存舌象分析失败', error: e);
      throw Exception('保存舌象分析失败: $e');
    }
  }

  @override
  Future<TongueAnalysis?> getTongueAnalysisById(String analysisId) async {
    try {
      // 先从本地查找
      if (_localTongueAnalyses.containsKey(analysisId)) {
        return _localTongueAnalyses[analysisId];
      }
      
      // TODO: 从远程数据库获取
      
      return null;
    } catch (e) {
      _logger.e('获取舌象分析失败', error: e);
      return null;
    }
  }

  @override
  Future<TongueAnalysis?> getLatestTongueAnalysisByUserId(String userId) async {
    try {
      // 从本地查找用户的所有舌象分析
      final userAnalyses = _localTongueAnalyses.values
          .where((analysis) => analysis.userId == userId)
          .toList();
      
      // 按采集时间排序
      userAnalyses.sort((a, b) => b.captureTime.compareTo(a.captureTime));
      
      // 返回最新的舌象分析
      return userAnalyses.isNotEmpty ? userAnalyses.first : null;
    } catch (e) {
      _logger.e('获取用户最新舌象分析失败', error: e);
      return null;
    }
  }

  @override
  Future<List<TongueAnalysis>> getTongueAnalysesByUserId(String userId) async {
    try {
      // 从本地查找用户的所有舌象分析
      final userAnalyses = _localTongueAnalyses.values
          .where((analysis) => analysis.userId == userId)
          .toList();
      
      // 按采集时间排序
      userAnalyses.sort((a, b) => b.captureTime.compareTo(a.captureTime));
      
      return userAnalyses;
    } catch (e) {
      _logger.e('获取用户所有舌象分析失败', error: e);
      return [];
    }
  }

  @override
  Future<List<TongueAnalysis>> getTongueAnalysesByTimeRange(
    String userId,
    DateTime startDate,
    DateTime endDate,
  ) async {
    try {
      // 从本地查找用户特定时间范围内的舌象分析
      final userAnalyses = _localTongueAnalyses.values
          .where((analysis) => 
              analysis.userId == userId &&
              analysis.captureTime.isAfter(startDate) &&
              analysis.captureTime.isBefore(endDate))
          .toList();
      
      // 按采集时间排序
      userAnalyses.sort((a, b) => b.captureTime.compareTo(a.captureTime));
      
      return userAnalyses;
    } catch (e) {
      _logger.e('获取用户时间范围内舌象分析失败', error: e);
      return [];
    }
  }

  @override
  Future<TongueAnalysis> updateTongueAnalysis(TongueAnalysis analysis) async {
    try {
      // 确保舌象分析ID存在
      if (!_localTongueAnalyses.containsKey(analysis.id)) {
        throw Exception('舌象分析不存在');
      }
      
      // 更新本地数据
      _localTongueAnalyses[analysis.id] = analysis;
      
      // TODO: 同步到远程数据库
      
      return analysis;
    } catch (e) {
      _logger.e('更新舌象分析失败', error: e);
      throw Exception('更新舌象分析失败: $e');
    }
  }

  @override
  Future<bool> deleteTongueAnalysis(String analysisId) async {
    try {
      // 确保舌象分析ID存在
      if (!_localTongueAnalyses.containsKey(analysisId)) {
        return false;
      }
      
      // 从本地删除
      _localTongueAnalyses.remove(analysisId);
      
      // TODO: 从远程数据库删除
      
      return true;
    } catch (e) {
      _logger.e('删除舌象分析失败', error: e);
      return false;
    }
  }

  @override
  Future<String> generateTongueAnalysisDescription(TongueAnalysis analysis) async {
    try {
      // 获取舌象特征综合描述
      final featureDescription = analysis.getFeatureDescription();
      
      // 构建分析描述
      final description = '''
根据您的舌象检查，舌体呈现为$featureDescription。

${_generateHealthImplication(analysis)}

${_generateConstitutionSuggestion(analysis)}
''';
      
      return description;
    } catch (e) {
      _logger.e('生成舌象分析描述失败', error: e);
      throw Exception('生成舌象分析描述失败: $e');
    }
  }

  @override
  Future<List<String>> inferConstitutionFromTongueAnalysis(TongueAnalysis analysis) async {
    // 基于舌象特征推断可能的体质倾向
    List<String> constitutions = [];
    
    // 根据舌质颜色推断
    switch (analysis.tongueColor) {
      case TongueColor.pale:
        constitutions.add('气虚质');
        constitutions.add('阳虚质');
        break;
      case TongueColor.red:
      case TongueColor.crimson:
        constitutions.add('阴虚质');
        constitutions.add('湿热质');
        break;
      case TongueColor.purple:
        constitutions.add('血瘀质');
        constitutions.add('气郁质');
        break;
      case TongueColor.blue:
        constitutions.add('寒凝质');
        constitutions.add('阳虚质');
        break;
      default:
        break;
    }
    
    // 根据舌苔推断
    if (analysis.coatingThickness == CoatingThickness.greasy) {
      if (analysis.coatingColor == CoatingColor.yellow) {
        constitutions.add('湿热质');
        constitutions.add('痰湿质');
      } else if (analysis.coatingColor == CoatingColor.white) {
        constitutions.add('痰湿质');
        constitutions.add('阳虚质');
      }
    }
    
    // 根据舌形推断
    if (analysis.tongueShape == TongueShape.swollen) {
      constitutions.add('痰湿质');
      constitutions.add('气虚质');
    } else if (analysis.tongueShape == TongueShape.thin) {
      constitutions.add('气阴两虚质');
      constitutions.add('阴虚质');
    } else if (analysis.tongueShape == TongueShape.cracked) {
      constitutions.add('阴虚质');
    }
    
    // 去重
    const constitutionSet = <String>{};
    constitutionSet.addAll(constitutions);
    
    return constitutionSet.toList();
  }
  
  /// 根据舌象分析生成健康状况提示
  String _generateHealthImplication(TongueAnalysis analysis) {
    String implication = '从中医角度分析，';
    
    // 根据舌质颜色分析
    switch (analysis.tongueColor) {
      case TongueColor.pale:
        implication += '您可能存在气血不足的情况，体内阳气偏弱；';
        break;
      case TongueColor.lightRed:
        implication += '您的舌色基本正常，显示气血状态平和；';
        break;
      case TongueColor.red:
        implication += '您体内有热象表现，可能存在阴虚内热的情况；';
        break;
      case TongueColor.crimson:
        implication += '您体内热象较重，可能有热入营血的表现；';
        break;
      case TongueColor.purple:
        implication += '您可能存在血行不畅、气滞血瘀的情况；';
        break;
      case TongueColor.blue:
        implication += '您体内寒气较重，阳气虚弱，气血运行不畅；';
        break;
    }
    
    // 根据舌苔分析
    if (analysis.coatingThickness == CoatingThickness.none) {
      implication += '舌无苔显示胃阴不足；';
    } else {
      implication += '${analysis.coatingColorName}色${analysis.coatingThicknessName}表明';
      if (analysis.coatingColor == CoatingColor.white && analysis.coatingThickness == CoatingThickness.thin) {
        implication += '体内寒湿较轻；';
      } else if (analysis.coatingColor == CoatingColor.white && analysis.coatingThickness == CoatingThickness.thick) {
        implication += '体内寒湿较重；';
      } else if (analysis.coatingColor == CoatingColor.yellow && analysis.coatingThickness == CoatingThickness.thin) {
        implication += '体内有湿热但程度较轻；';
      } else if (analysis.coatingColor == CoatingColor.yellow && analysis.coatingThickness == CoatingThickness.thick) {
        implication += '体内湿热较重；';
      } else if (analysis.coatingThickness == CoatingThickness.greasy) {
        implication += '体内痰湿较重；';
      } else if (analysis.coatingColor == CoatingColor.gray || analysis.coatingColor == CoatingColor.black) {
        implication += '体内有寒湿或热重伤阴的情况；';
      }
    }
    
    // 根据舌体形态
    switch (analysis.tongueShape) {
      case TongueShape.swollen:
        implication += '舌体胖大表明脾虚湿盛；';
        break;
      case TongueShape.thin:
        implication += '舌体瘦薄表明气血亏虚；';
        break;
      case TongueShape.cracked:
        implication += '裂纹表明体内津液不足；';
        break;
      case TongueShape.thorny:
        implication += '点刺表明有热毒；';
        break;
      case TongueShape.deviated:
        implication += '舌歪斜表明可能有中经络问题；';
        break;
      default:
        break;
    }
    
    // 根据湿度
    switch (analysis.moisture) {
      case TongueMoisture.dry:
        implication += '舌体干燥表明体内津液不足；';
        break;
      case TongueMoisture.wet:
        implication += '舌体过度湿润表明体内有湿；';
        break;
      default:
        break;
    }
    
    return implication;
  }
  
  /// 根据舌象分析生成体质建议
  String _generateConstitutionSuggestion(TongueAnalysis analysis) {
    String suggestion = '建议：';
    
    // 根据舌质颜色给出建议
    switch (analysis.tongueColor) {
      case TongueColor.pale:
        suggestion += '注意保暖，适当进行温和运动增强体质，饮食宜温补，可食用黑米、黑豆、羊肉等温补食材；';
        break;
      case TongueColor.lightRed:
        suggestion += '保持当前健康生活习惯，规律作息，均衡饮食；';
        break;
      case TongueColor.red:
      case TongueColor.crimson:
        suggestion += '注意清热养阴，避免辛辣刺激性食物，多食用梨、银耳、莲子等清润食材，保持情绪平和；';
        break;
      case TongueColor.purple:
        suggestion += '注意活血化瘀，适当进行有氧运动，可食用红枣、黑木耳等活血食材，避免久坐久立；';
        break;
      case TongueColor.blue:
        suggestion += '注意保暖，避免寒凉食物，可食用生姜、桂圆等温阳食材，保持室内温暖干燥；';
        break;
    }
    
    // 根据舌苔给出建议
    if (analysis.coatingThickness == CoatingThickness.greasy) {
      suggestion += '注意健脾化湿，避免油腻、甜腻食物，可食用薏米、赤小豆等健脾利湿的食材，保持规律运动；';
    }
    
    suggestion += '建议通过完整的四诊合参进一步确认您的体质类型，获得更全面的健康指导。';
    
    return suggestion;
  }
} 