import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/repositories/constitution_repository.dart';

/// 获取体质特征用例
class GetConstitutionTraitsUseCase {
  /// 体质存储库
  final ConstitutionRepository _repository;
  
  /// 创建获取体质特征用例
  GetConstitutionTraitsUseCase(this._repository);
  
  /// 调用用例，获取特定体质类型的特征
  Future<ConstitutionTraits> call(ConstitutionType type) async {
    return await _repository.getConstitutionTraits(type);
  }
  
  /// 获取所有体质类型特征
  Future<List<ConstitutionTraits>> getAllTypes() async {
    return await _repository.getAllConstitutionTypes();
  }
  
  /// 获取特定体质类型的适宜食物
  Future<List<String>> getSuitableFoods(ConstitutionType type) async {
    return await _repository.getSuitableFoods(type);
  }
  
  /// 获取特定体质类型的不适宜食物
  Future<List<String>> getUnsuitableFoods(ConstitutionType type) async {
    return await _repository.getUnsuitableFoods(type);
  }
} 