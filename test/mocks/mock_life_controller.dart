import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/life/life_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockLifeController extends LifeController {
  @override
  final SuokeService suokeService;

  MockLifeController({required this.suokeService}) : super(suokeService) {
    // 初始化测试数据
    userProfile.value = {
      'name': 'Test User',
      'avatar': 'assets/images/default_avatar.png',
      'description': 'Test Description',
    };
    healthAdvices.value = [
      {'id': '1', 'title': 'Test Advice'},
    ];
    lifeRecords.value = [
      {'id': '1', 'title': 'Test Record'},
    ];
  }

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadData() async {
    // 不执行实际的加载操作
  }

  @override
  void showProfileDetail() {}

  @override
  void showAdviceDetail(Map<String, dynamic> advice) {}

  @override
  void showRecordDetail(Map<String, dynamic> record) {}

  @override
  void showCalendar() {}

  @override
  void showXiaoKe() {}
} 