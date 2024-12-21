import 'package:get/get.dart';

class ChatController extends GetxController {
  final _title = 'Chat'.obs;
  get title => _title.value;
  
  @override
  void onInit() {
    super.onInit();
    // 初始化聊天逻辑
  }
  
  @override
  void onReady() {
    super.onReady();
    // 加载聊天列表等
  }
  
  @override
  void onClose() {
    super.onClose();
    // 清理资源
  }
} 