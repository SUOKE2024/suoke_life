import 'package:get/get.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/services/features/ai/assistants/xiaoi_service.dart';

class MockXiaoiService extends GetxService with Mock implements XiaoiService {
  @override
  void onInit() {
    super.onInit();
  }

  @override
  Future<void> init() async {}

  @override
  Future<String> chat(String message) async {
    return 'Mock response from XiaoiService';
  }

  @override
  void onClose() {
    super.onClose();
  }
} 