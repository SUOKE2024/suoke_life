import 'package:get/get.dart';
import 'base_chat_controller.dart';
import '../../services/ai/xiaoi_service.dart';
import '../../services/storage/chat_storage_service.dart';
import '../../models/health_analysis.dart';

class XiaoiChatController extends BaseChatController {
  final healthReports = <HealthReport>[].obs;
  final isAnalyzing = false.obs;

  XiaoiChatController() : super(
    aiService: Get.find<XiaoiService>(),
    storageService: Get.find<ChatStorageService>(),
  );

  Future<void> startHealthAnalysis() async {
    try {
      isAnalyzing.value = true;
      
      // 发送开始分析消息
      final startMessage = Message(
        id: DateTime.now().toString(),
        type: MessageType.text,
        content: '好的,让我们开始健康分析。请告诉我您最近的身体状况。',
        isFromUser: false,
        timestamp: DateTime.now(),
      );
      
      messages.add(startMessage);
      await storageService.saveMessage(startMessage);
      
    } finally {
      isAnalyzing.value = false;
    }
  }

  Future<void> generateHealthReport() async {
    try {
      isAnalyzing.value = true;
      
      final xiaoiService = aiService as XiaoiService;
      final report = await xiaoiService.generateHealthReport();
      
      healthReports.add(report);
      
      // 发送报告生成消息
      final reportMessage = Message(
        id: DateTime.now().toString(),
        type: MessageType.text,
        content: '您的健康报告已生成,请查看。',
        isFromUser: false,
        timestamp: DateTime.now(),
        metadata: {'reportId': report.id},
      );
      
      messages.add(reportMessage);
      await storageService.saveMessage(reportMessage);
      
    } finally {
      isAnalyzing.value = false;
    }
  }

  Future<void> scheduleReminder(DateTime time, String content) async {
    try {
      final xiaoiService = aiService as XiaoiService;
      await xiaoiService.setReminder(time, content);
      
      final reminderMessage = Message(
        id: DateTime.now().toString(),
        type: MessageType.text,
        content: '好的,我已经帮您设置了提醒。',
        isFromUser: false,
        timestamp: DateTime.now(),
        metadata: {
          'reminderTime': time.toIso8601String(),
          'reminderContent': content,
        },
      );
      
      messages.add(reminderMessage);
      await storageService.saveMessage(reminderMessage);
      
    } catch (e) {
      print('Error in scheduleReminder: $e');
      Get.snackbar('提示', '设置提醒失败');
    }
  }
} 