import 'package:get/get.dart';
import '../../../services/ai/ai_service.dart';
import '../../../models/chat_message.dart';

class XiaoiController extends GetxController {
  final AIService _aiService;
  final messages = <ChatMessage>[].obs;
  
  XiaoiController(this._aiService);

  @override
  void onInit() {
    super.onInit();
    // 添加欢迎消息
    messages.add(ChatMessage.assistant(
      content: '您好，我是小艾，您的AI健康助手。我可以帮您：\n'
          '1. 收集和分析健康数据\n'
          '2. 提供个性化健康建议\n'
          '3. 解答健康相关问题\n'
          '4. 推荐专业医生咨询\n\n'
          '请问有什么可以帮您？',
    ));
  }

  // 发送文本消息
  Future<void> sendTextMessage(String text) async {
    if (text.trim().isEmpty) return;

    try {
      // 添加用户消息
      messages.insert(0, ChatMessage.user(
        content: text,
      ));

      // 显示AI正在输入状态
      messages.insert(0, ChatMessage.assistant(
        content: '正在思考...',
      ));

      // 调用AI接口获取回复
      final response = await _aiService.chat(
        model: AIModel.xiaoAi,
        message: text,
      );
      
      // 移除"正在思考"消息
      messages.removeAt(0);
      
      // 添加AI回复
      messages.insert(0, ChatMessage.assistant(
        content: response,
      ));
    } catch (e) {
      // 移除"正在思考"消息
      if (messages.isNotEmpty && messages[0].role == MessageRole.assistant) {
        messages.removeAt(0);
      }
      
      // 添加错误消息
      messages.insert(0, ChatMessage.error(
        content: '消息发送失败：$e',
      ));
    }
  }

  // 播放语音消息
  Future<void> playVoiceMessage(ChatMessage message) async {
    // TODO: 实现语音播放功能
  }
} 