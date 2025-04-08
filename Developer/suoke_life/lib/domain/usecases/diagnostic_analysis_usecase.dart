import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/four_diagnostic_data.dart';
import 'package:suoke_life/domain/repositories/diagnostic_repository.dart';

/// 四诊数据分析用例
///
/// 负责采集和分析四诊数据（望闻问切），并生成诊断结论
class DiagnosticAnalysisUseCase {
  final DiagnosticRepository _repository;
  
  /// 创建四诊数据分析用例
  DiagnosticAnalysisUseCase(this._repository);
  
  /// 保存四诊数据
  Future<void> saveDiagnosticData(FourDiagnosticData data) async {
    await _repository.saveDiagnosticData(data);
  }
  
  /// 获取指定ID的四诊数据
  Future<FourDiagnosticData> getDiagnosticDataById(String id) async {
    return _repository.getDiagnosticDataById(id);
  }
  
  /// 获取用户所有的四诊数据
  Future<List<FourDiagnosticData>> getUserDiagnosticData(String userId) async {
    return _repository.getUserDiagnosticData(userId);
  }
  
  /// 获取用户最新的四诊数据
  Future<FourDiagnosticData?> getLatestDiagnosticData(String userId) async {
    return _repository.getLatestDiagnosticData(userId);
  }
  
  /// 删除指定ID的四诊数据
  Future<void> deleteDiagnosticData(String id) async {
    await _repository.deleteDiagnosticData(id);
  }
  
  /// 根据日期范围获取用户的四诊数据
  Future<List<FourDiagnosticData>> getUserDiagnosticDataByDateRange(
      String userId, DateTime startDate, DateTime endDate) async {
    return _repository.getUserDiagnosticDataByDateRange(userId, startDate, endDate);
  }
  
  /// 上传四诊照片（如舌诊、面诊照片）
  Future<List<String>> uploadDiagnosticImages(String diagnosisId, List<String> localImagePaths) async {
    return _repository.uploadDiagnosticImages(diagnosisId, localImagePaths);
  }
  
  /// 分析四诊数据，生成诊断结论
  Future<String> analyzeDiagnosticData(FourDiagnosticData data) async {
    return _repository.analyzeDiagnosticData(data);
  }
  
  /// 分析舌象照片
  Future<Map<String, dynamic>> analyzeTongueImage(String imagePath) async {
    return _repository.analyzeTongueImage(imagePath);
  }
  
  /// 分析面部照片
  Future<Map<String, dynamic>> analyzeFacialImage(String imagePath) async {
    return _repository.analyzeFacialImage(imagePath);
  }
  
  /// 语音转文字（用于问诊记录）
  Future<String> speechToText(String audioPath) async {
    return _repository.speechToText(audioPath);
  }
  
  /// 创建空的四诊数据模板，用于初始化新的诊断
  FourDiagnosticData createEmptyDiagnosticTemplate(String userId, String doctorId, String doctorName) {
    final now = DateTime.now();
    const id = ''; // 临时ID，保存时会生成新ID
    
    // 创建空的望诊数据
    final inspectionData = InspectionData(
      facial: FacialData(
        complexion: '',
        complexionFeatures: [],
        spirit: '',
        eyes: '',
        lips: '',
      ),
      tongue: TongueData(
        tongueColor: '',
        tongueForm: [],
        tongueBody: '',
        tongueMoisture: '',
        coatingColor: '',
        coatingThickness: '',
        coatingDistribution: '',
      ),
      bodyForm: BodyFormData(
        bodyType: '',
        bodyShape: '',
        posture: '',
        movementFeatures: [],
      ),
      skin: SkinData(
        skinColor: '',
        skinTexture: '',
        skinMoisture: '',
        skinFeatures: [],
      ),
    );
    
    // 创建空的闻诊数据
    final auscultationData = AuscultationData(
      voice: VoiceData(
        voiceQuality: '',
        speechRate: '',
        voiceFeatures: [],
      ),
      breathing: '',
      odor: OdorData(
        breath: '',
        body: '',
      ),
    );
    
    // 创建空的问诊数据
    final inquiryData = InquiryData(
      chiefComplaint: '',
      medicalHistory: MedicalHistoryData(
        presentIllness: '',
        pastHistory: '',
        familyHistory: '',
        allergicHistory: '',
        medicationHistory: '',
      ),
      lifestyle: LifestyleData(
        diet: '',
        sleep: '',
        emotion: '',
        exercise: '',
        habits: '',
      ),
      systemInquiry: SystemInquiryData(),
    );
    
    // 创建空的切诊数据
    final palpationData = PalpationData(
      pulse: PulseData(
        leftCun: '',
        leftGuan: '',
        leftChi: '',
        rightCun: '',
        rightGuan: '',
        rightChi: '',
        pulseCharacteristics: [],
      ),
    );
    
    return FourDiagnosticData(
      id: id,
      userId: userId,
      diagnosisTime: now,
      inspection: inspectionData,
      auscultation: auscultationData,
      inquiry: inquiryData,
      palpation: palpationData,
      conclusion: '',
      doctorId: doctorId,
      doctorName: doctorName,
    );
  }
}

/// 四诊数据分析用例Provider
final diagnosticAnalysisUseCaseProvider = Provider<DiagnosticAnalysisUseCase>((ref) {
  final repository = ref.watch(diagnosticRepositoryProvider);
  return DiagnosticAnalysisUseCase(repository);
}); 