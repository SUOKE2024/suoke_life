import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/health_regimen.dart';
import 'package:suoke_life/domain/repositories/constitution_repository.dart';
import 'package:suoke_life/domain/repositories/diagnostic_repository.dart';
import 'package:suoke_life/domain/repositories/health_regimen_repository.dart';

/// 生成健康调理方案用例
///
/// 负责基于体质类型和四诊数据生成个性化的中医健康调理方案
class GenerateHealthRegimenUseCase {
  final HealthRegimenRepository _regimenRepository;
  final ConstitutionRepository _constitutionRepository;
  final DiagnosticRepository _diagnosticRepository;
  
  /// 创建生成健康调理方案用例
  GenerateHealthRegimenUseCase(
    this._regimenRepository,
    this._constitutionRepository,
    this._diagnosticRepository,
  );
  
  /// 根据用户体质类型生成健康调理方案
  /// 
  /// [userId] 用户ID
  /// [constitutionType] 体质类型
  /// [diagnosis] 诊断结论，可选
  Future<HealthRegimen> generateByConstitution(
    String userId, 
    ConstitutionType constitutionType, 
    {String? diagnosis}
  ) async {
    final actualDiagnosis = diagnosis ?? await _generateDiagnosisForConstitution(constitutionType);
    
    return _regimenRepository.generateHealthRegimenByConstitution(
      userId, 
      constitutionType, 
      actualDiagnosis,
    );
  }
  
  /// 根据四诊数据生成健康调理方案
  /// 
  /// [userId] 用户ID
  /// [diagnosticDataId] 四诊数据ID
  Future<HealthRegimen> generateFromDiagnosticData(
    String userId, 
    String diagnosticDataId
  ) async {
    // 首先获取四诊数据的诊断结论
    final diagnosticData = await _diagnosticRepository.getDiagnosticDataById(diagnosticDataId);
    
    // 分析四诊数据获取体质类型
    final constitutionResult = await _constitutionRepository.generateConstitutionResultFromDiagnosticData(
      userId, 
      diagnosticDataId
    );
    
    // 使用体质类型和诊断结论生成健康调理方案
    final regimen = await _regimenRepository.generateHealthRegimenFromDiagnosticData(
      userId, 
      diagnosticDataId
    );
    
    return regimen;
  }
  
  /// 为特定体质类型生成默认诊断结论
  Future<String> _generateDiagnosisForConstitution(ConstitutionType type) async {
    final traits = await _constitutionRepository.getConstitutionTraits(type);
    
    // 基于体质特征生成诊断结论
    switch (type) {
      case ConstitutionType.balanced:
        return '平和体质，阴阳气血调和，脏腑功能正常，抗病能力强。';
      case ConstitutionType.qiDeficiency:
        return '气虚体质，表现为气不足，易疲乏，抵抗力低下。';
      case ConstitutionType.yangDeficiency:
        return '阳虚体质，表现为阳气不足，怕冷，手脚发凉。';
      case ConstitutionType.yinDeficiency:
        return '阴虚体质，表现为阴液不足，内热明显，口燥咽干。';
      case ConstitutionType.phlegmDampness:
        return '痰湿体质，表现为体内痰湿较盛，形体肥胖，多痰。';
      case ConstitutionType.dampnessHeat:
        return '湿热体质，表现为体内湿热偏盛，易生疮疡，口苦。';
      case ConstitutionType.bloodStasis:
        return '血瘀体质，表现为血行不畅，皮肤晦暗，易有瘀斑。';
      case ConstitutionType.qiStagnation:
        return '气郁体质，表现为气机郁滞，情志不畅，易焦虑。';
      case ConstitutionType.specialConstitution:
        return '特禀体质，表现为体质特异，过敏性强，易发生变态反应。';
    }
  }
  
  /// 获取指定体质类型的食疗推荐
  Future<List<MedicinalDietItem>> getMedicinalDiet(ConstitutionType type) async {
    return _regimenRepository.getMedicinalDietForConstitution(type);
  }
  
  /// 获取指定体质类型的传统功法推荐
  Future<List<TraditionalExercise>> getTraditionalExercises(ConstitutionType type) async {
    return _regimenRepository.getTraditionalExercisesForConstitution(type);
  }
  
  /// 获取指定体质类型的穴位按摩推荐
  Future<List<AcupointRecommendation>> getAcupointRecommendations(ConstitutionType type) async {
    return _regimenRepository.getAcupointRecommendationsForConstitution(type);
  }
  
  /// 获取指定体质类型的季节性调理建议
  Future<Map<String, dynamic>> getSeasonalAdvice(ConstitutionType type, String season) async {
    return _regimenRepository.getSeasonalRegimenSuggestions(type, season);
  }
}

/// 生成健康调理方案用例Provider
final generateHealthRegimenUseCaseProvider = Provider<GenerateHealthRegimenUseCase>((ref) {
  final regimenRepository = ref.watch(healthRegimenRepositoryProvider);
  final constitutionRepository = ref.watch(constitutionRepositoryProvider);
  final diagnosticRepository = ref.watch(diagnosticRepositoryProvider);
  
  return GenerateHealthRegimenUseCase(
    regimenRepository,
    constitutionRepository,
    diagnosticRepository,
  );
}); 