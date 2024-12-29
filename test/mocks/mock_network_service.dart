import 'package:mockito/mockito.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/core/services/network/network_service.dart';

class MockNetworkService extends GetxService with Mock implements NetworkService {
  @override
  void onInit() {
    super.onInit();
  }
  
  @override
  void onClose() {
    super.onClose();
  }
  
  @override
  Future<void> init() async {}
  
  @override
  Future<void> dispose() async {}
} 