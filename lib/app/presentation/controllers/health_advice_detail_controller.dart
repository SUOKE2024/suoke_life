import 'package:get/get.dart';
import '../../data/models/health_advice.dart';
import '../../services/health_advice_service.dart';

class HealthAdviceDetailController extends GetxController {
  final advice = Rx<HealthAdvice?>(null);
  final isLoading = false.obs;
  final error = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    advice.value = Get.arguments as HealthAdvice;
    if (advice.value != null) {
      Get.find<HealthAdviceService>().addToHistory(advice.value!.id);
    }
    _loadDetail();
  }

  @override
  void onClose() {
    super.onClose();
    advice.value = null;
    error.value = null;
  }

  Future<void> _loadDetail() async {
    if (advice.value == null) {
      error.value = '无效的健康建议';
      return;
    }
    
    try {
      isLoading.value = true;
      error.value = null;
      final detail = await Get.find<HealthAdviceService>()
          .getAdviceDetail(advice.value!.id);
      if (detail != null) {
        advice.value = detail;
      } else {
        error.value = '未找到健康建议详情';
        Get.back();
      }
    } catch (e) {
      error.value = '加载详情失败: ${e.toString()}';
      Get.back();
    } finally {
      isLoading.value = false;
    }
  }
} 