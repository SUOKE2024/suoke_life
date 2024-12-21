import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/feedback_controller.dart';
import 'package:suoke_life/services/feedback_service.dart';

class FeedbackBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => FeedbackService());
    Get.lazyPut(() => FeedbackController());
  }
} 