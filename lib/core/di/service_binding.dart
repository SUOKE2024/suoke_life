import 'package:get/get.dart';
import '../../services/voice_service.dart';

class ServiceBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<VoiceService>(() => VoiceService()..initialize());
  }
} 