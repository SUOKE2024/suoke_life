import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';

class LifeController extends GetxController {
  final SuokeService suokeService;
  final isLoading = false.obs;
  final userProfile = ''.obs;
  final healthAdvice = <String>[].obs;

  LifeController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    try {
      isLoading.value = true;
      final profile = await suokeService.getUserProfile();
      userProfile.value = profile['description'] as String;

      final advice = await suokeService.getHealthAdvice();
      healthAdvice.value = advice.map((e) => e['content'] as String).toList();
    } catch (e) {
      Get.snackbar('错误', '加载数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  void showAdviceDetail(String advice) {
    Get.toNamed('/life/advice', arguments: advice);
  }
} 