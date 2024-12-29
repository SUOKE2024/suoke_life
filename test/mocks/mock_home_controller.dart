import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockHomeController extends HomeController {
  @override
  final SuokeService suokeService;

  MockHomeController({required this.suokeService}) : super(suokeService) {
    // 初始化测试数据
    currentIndex.value = 0;
  }

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadInitialData() async {
    // 不执行实际的加载操作
  }

  @override
  void showAddMenu() {
    // 不执行实际的操作
  }
} 