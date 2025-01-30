import 'package:suoke_life_app_app_app/app/core/env/env_config_dart.dart';
import 'package:suoke_life_app_app_app/app/core/ai/ai_config.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_service.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_service_client.dart';

void main() async {
  // 初始化环境配置
  await EnvConfigDart.init();
  
  // 初始化AI服务
  final aiConfig = AIConfig(apiKey: EnvConfigDart.instance.aiApiKey);
  final client = AIServiceClient(AIServiceClient.createDio());
  final aiService = AIServiceImpl(client, aiConfig);

  // 测试小艾对话
  print('\n=== 测试小艾对话 ===');
  try {
    final response = await aiService.chat(
      message: '你好,请介绍一下你自己,你是谁开发的?',
      modelType: 'xiao_ai',
    );
    if (response.choices?.isNotEmpty == true) {
      print('小艾: ${response.choices?.first.message.content}');
    } else {
      print('小艾没有回应');
    }
  } catch (e) {
    print('小艾对话出错: $e');
  }

  // 测试小克专业问答
  print('\n=== 测试小克专业问答 ===');
  try {
    final response = await aiService.chat(
      message: '请详细介绍一下常见的十字花科蔬菜及其种植方法',
      modelType: 'xiao_ke',
    );
    if (response.choices?.isNotEmpty == true) {
      print('小克: ${response.choices?.first.message.content}');
    } else {
      print('小克没有回应');
    }
  } catch (e) {
    print('小克对话出错: $e');
  }

  // 测试老克向量生成
  print('\n=== 测试老克向量生成 ===');
  try {
    final embeddings = await aiService.generateEmbeddings(
      '花椰菜又称菜花、花菜，是一种常见的蔬菜，富含维生素C和膳食纤维。',
    );
    print('向量维度: ${embeddings.length}');
  } catch (e) {
    print('老克向量生成出错: $e');
  }

  // 测试对话上下文
  print('\n=== 测试对话上下文 ===');
  try {
    final response1 = await aiService.chat(
      message: '我想种植一些蔬菜',
      modelType: 'xiao_ke',
    );
    if (response1.choices?.isNotEmpty != true) {
      throw Exception('No response from AI');
    }
    print('用户: 我想种植一些蔬菜');
    print('小克: ${response1.choices!.first.message.content}');

    final response2 = await aiService.chat(
      message: '我家在北方,现在是春季',
      modelType: 'xiao_ke',
      context: [
        {
          'role': 'user',
          'content': '我想种植一些蔬菜',
        },
        {
          'role': 'assistant',
          'content': response1.choices!.first.message.content,
        },
      ],
    );
    if (response2.choices?.isNotEmpty == true) {
      print('用户: 我家在北方,现在是春季');
      print('小克: ${response2.choices?.first.message.content}');
    } else {
      print('小克没有回应');
    }
  } catch (e) {
    print('对话上下文测试出错: $e');
  }
} 