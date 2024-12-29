import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/user.dart';

class ProfileController extends GetxController {
  final SuokeService suokeService;
  final isLoading = false.obs;
  final user = User(id: '', name: '').obs;

  ProfileController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadUserData();
  }

  Future<void> loadUserData() async {
    try {
      isLoading.value = true;
      final currentUser = await suokeService.getCurrentUser();
      if (currentUser != null) {
        user.value = currentUser;
      }
    } catch (e) {
      Get.snackbar('错误', '加载用户数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  void editProfile() {
    Get.toNamed('/profile/edit', arguments: user.value);
  }

  void showHistory() {
    Get.toNamed('/profile/history');
  }

  void showFavorites() {
    Get.toNamed('/profile/favorites');
  }

  void showHelp() {
    Get.toNamed('/profile/help');
  }

  void showAbout() {
    Get.toNamed('/profile/about');
  }
} 