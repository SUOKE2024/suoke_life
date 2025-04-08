import 'package:suoke_life/domain/entities/constitution_type_result.dart';
import 'package:suoke_life/domain/repositories/user_constitution_repository.dart';

/// 获取最新体质结果用例
class GetLatestConstitutionResultUseCase {
  /// 用户体质存储库
  final UserConstitutionRepository _repository;
  
  /// 创建获取最新体质结果用例
  GetLatestConstitutionResultUseCase(this._repository);
  
  /// 调用用例，获取用户最新的体质评估结果
  Future<ConstitutionTypeResult?> call(String userId) async {
    return await _repository.getLatestResult(userId);
  }
} 