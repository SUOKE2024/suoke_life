import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/health_regimen.dart';
import 'package:suoke_life/domain/repositories/health_regimen_repository.dart';

/// 健康调理方案管理用例
///
/// 负责健康调理方案的查询、保存、删除等管理功能
class ManageHealthRegimenUseCase {
  final HealthRegimenRepository _repository;
  
  /// 创建健康调理方案管理用例
  ManageHealthRegimenUseCase(this._repository);
  
  /// 保存健康调理方案
  Future<void> saveRegimen(HealthRegimen regimen) async {
    await _repository.saveHealthRegimen(regimen);
  }
  
  /// 获取指定ID的健康调理方案
  Future<HealthRegimen> getRegimenById(String id) async {
    return _repository.getHealthRegimenById(id);
  }
  
  /// 获取用户所有的健康调理方案
  Future<List<HealthRegimen>> getUserRegimens(String userId) async {
    final regimens = await _repository.getUserHealthRegimens(userId);
    
    // 按创建时间降序排序
    regimens.sort((a, b) => b.createdTime.compareTo(a.createdTime));
    return regimens;
  }
  
  /// 获取用户最新的健康调理方案
  Future<HealthRegimen?> getLatestRegimen(String userId) async {
    return _repository.getLatestHealthRegimen(userId);
  }
  
  /// 删除指定ID的健康调理方案
  Future<void> deleteRegimen(String id) async {
    await _repository.deleteHealthRegimen(id);
  }
  
  /// 按体质类型筛选用户的调理方案
  Future<List<HealthRegimen>> filterByConstitutionType(
      String userId, ConstitutionType type) async {
    final allRegimens = await _repository.getUserHealthRegimens(userId);
    return allRegimens.where((regimen) => regimen.constitutionType == type).toList();
  }
  
  /// 按创建日期范围筛选用户的调理方案
  Future<List<HealthRegimen>> filterByDateRange(
      String userId, DateTime startDate, DateTime endDate) async {
    final allRegimens = await _repository.getUserHealthRegimens(userId);
    
    return allRegimens.where((regimen) {
      return regimen.createdTime.isAfter(startDate) && 
             regimen.createdTime.isBefore(endDate.add(const Duration(days: 1)));
    }).toList();
  }
  
  /// 保存用户对方案的反馈
  Future<void> saveRegimenFeedback(String regimenId, String feedback, int rating) async {
    await _repository.saveRegimenFeedback(regimenId, feedback, rating);
  }
  
  /// 获取用户方案执行的依从性数据
  Future<Map<String, dynamic>> getRegimenAdherenceData(String userId, String regimenId) async {
    return _repository.getRegimenAdherenceData(userId, regimenId);
  }
}

/// 健康调理方案管理用例Provider
final manageHealthRegimenUseCaseProvider = Provider<ManageHealthRegimenUseCase>((ref) {
  final repository = ref.watch(healthRegimenRepositoryProvider);
  return ManageHealthRegimenUseCase(repository);
}); 