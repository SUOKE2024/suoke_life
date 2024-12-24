import 'package:get/get.dart';

class HomeController extends GetxController {
  final title = 'Home'.obs;
  final isLoading = false.obs;
  final messages = <String>[].obs;
  final currentIndex = 0.obs;

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    isLoading.value = true;
    try {
      // TODO: 加载消息列表
      messages.value = ['Message 1', 'Message 2', 'Message 3'];
    } finally {
      isLoading.value = false;
    }
  }

  void sendMessage(String message) {
    if (message.trim().isEmpty) return;
    messages.add(message);
  }

  void changeTab(int index) {
    currentIndex.value = index;
  }
} 