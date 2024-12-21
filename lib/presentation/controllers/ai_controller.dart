import 'package:get/get.dart';

class AIController extends GetxController {
  final _title = 'AI Assistant'.obs;
  get title => _title.value;
  
  @override
  void onInit() {
    super.onInit();
    // 初始化AI助手
  }
  
  @override
  void onReady() {
    super.onReady();
    // 加载AI设置等
  }
  
  @override
  void onClose() {
    super.onClose();
    // 清理资源
  }
} 