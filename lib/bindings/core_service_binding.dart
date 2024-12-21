import 'package:get/get.dart';
import '../services/voice/speech_recognition_service.dart';
import '../services/voice/text_to_speech_service.dart';
import '../services/biometric/biometric_service.dart';
import '../services/deeplink/deep_link_service.dart';
import '../services/analytics/analytics_service.dart';

class CoreServiceBinding extends Bindings {
  @override
  void dependencies() async {
    // 语音识别服务
    final speechRecognition = SpeechRecognitionService();
    await speechRecognition.init();
    Get.lazyPut(() => speechRecognition);

    // 语音合成服务
    final textToSpeech = TextToSpeechService();
    await textToSpeech.init();
    Get.lazyPut(() => textToSpeech);

    // 生物识别服务
    Get.lazyPut(() => BiometricService());

    // 深度链接服务
    final deepLinkService = DeepLinkService();
    await deepLinkService.init();
    Get.lazyPut(() => deepLinkService);

    // 分析服务
    Get.lazyPut(() => AnalyticsService());
  }
} 