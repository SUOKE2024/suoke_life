import 'package:get/get.dart';

class StatisticsController extends GetxController {
  final todayRecords = 0.obs;
  final weekRecords = 0.obs;
  final monthRecords = 0.obs;

  @override
  void onInit() {
    super.onInit();
    loadStatistics();
  }

  Future<void> loadStatistics() async {
    // TODO: 从数据库加载统计数据
  }
} 