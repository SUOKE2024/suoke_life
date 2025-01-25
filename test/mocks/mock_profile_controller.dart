import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/profile/profile_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockProfileController extends ProfileController {
  MockProfileController({required SuokeService suokeService}) : super(suokeService);

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadUserProfile() async {
    // 不执行实际的加载操作
  }
} 