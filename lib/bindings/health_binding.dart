import 'package:get/get.dart';
import '../services/health/health_service.dart';
import '../services/health/health_analysis_service.dart';
import '../services/health/health_report_service.dart';

class HealthBinding extends Bindings {
  @override
  void dependencies() async {
    // 健康数据服务
    final healthService = HealthService();
    await healthService.init();
    Get.lazyPut(() => healthService);

    // 健康分析服务
    Get.lazyPut(() => HealthAnalysisService(Get.find()));

    // 健康报告服务
    Get.lazyPut(() => HealthReportService(Get.find()));
  }
} 