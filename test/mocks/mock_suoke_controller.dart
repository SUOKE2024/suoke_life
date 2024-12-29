import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/suoke/suoke_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/data/models/service.dart';

class MockSuokeController extends SuokeController {
  @override
  final SuokeService suokeService;

  MockSuokeController({required this.suokeService}) : super(suokeService) {
    // 初始化测试数据
    healthServices = [
      Service(
        id: '1',
        title: 'Test Health Service',
        description: 'Test Description',
        type: 'health_survey',
        createdAt: DateTime.now(),
      ),
    ];
    agriServices = [
      Service(
        id: '2',
        title: 'Test Agri Service',
        description: 'Test Description',
        type: 'agri_product',
        createdAt: DateTime.now(),
      ),
    ];
    update();
  }

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadServices() async {
    // 不执行实际的加载操作
  }
} 