// 中医服务提供者文件
// 定义中医相关的Provider

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers/core_providers.dart';

/// 中医服务提供者
/// 暂时仅提供空实现，将在后续开发中完善
final tcmServiceProvider = Provider<TCMService>((ref) {
  final dio = ref.watch(dioProvider);
  return TCMService(dio: dio);
});

/// 临时中医服务类
/// 后续将实现完整的中医服务功能
class TCMService {
  final dynamic dio;
  
  TCMService({required this.dio});
  
  // 未来将实现的方法
  Future<void> fetchConstitutionTypes() async {
    // 获取体质类型
  }
  
  Future<void> analyzeFourDiagnostics(Map<String, dynamic> data) async {
    // 分析四诊数据
  }
  
  Future<void> getHealthRegimen() async {
    // 获取调理方案
  }
} 