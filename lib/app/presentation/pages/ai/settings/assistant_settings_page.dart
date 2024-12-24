import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/assistant_settings_controller.dart';

class AssistantSettingsPage extends GetView<AssistantSettingsController> {
  const AssistantSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('助手设置'),
      ),
      body: ListView(
        children: [
          // 模型设置
          ListTile(
            leading: const Icon(Icons.model_training),
            title: const Text('模型设置'),
            subtitle: const Text('选择和配置AI模型'),
            onTap: controller.showModelSettings,
          ),
          
          // 语音设置
          ListTile(
            leading: const Icon(Icons.record_voice_over),
            title: const Text('语音设置'),
            subtitle: const Text('配置语音识别和合成'),
            onTap: controller.showVoiceSettings,
          ),
          
          // 知识库设置
          ListTile(
            leading: const Icon(Icons.library_books),
            title: const Text('知识库设置'),
            subtitle: const Text('管理专业知识库'),
            onTap: controller.showKnowledgeBaseSettings,
          ),
          
          // API设置
          ListTile(
            leading: const Icon(Icons.api),
            title: const Text('API设置'),
            subtitle: const Text('配置API密钥和参数'),
            onTap: controller.showApiSettings,
          ),
          
          // 隐私设置
          ListTile(
            leading: const Icon(Icons.privacy_tip),
            title: const Text('隐私设置'),
            subtitle: const Text('配置数据隐私和安全'),
            onTap: controller.showPrivacySettings,
          ),
        ],
      ),
    );
  }
} 