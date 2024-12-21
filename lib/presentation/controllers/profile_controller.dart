import 'package:get/get.dart';

class ProfileController extends GetxController {
  final _title = 'Profile'.obs;
  get title => _title.value;
  
  @override
  void onInit() {
    super.onInit();
    // 初始化用户信息
  }
  
  @override
  void onReady() {
    super.onReady();
    // 加载用户数据
  }
  
  @override
  void onClose() {
    super.onClose();
    // 清理资源
  }
} 