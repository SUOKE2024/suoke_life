import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/settings/assistant_settings_controller.dart';

class AssistantSettingsPage extends GetView<AssistantSettingsController> {
  const AssistantSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('助手设置'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.resetSettings,
          ),
        ],
      ),
      body: ListView(
        children: [
          // 默认助手选择
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('默认助手', style: TextStyle(fontSize: 16)),
                const SizedBox(height: 8),
                Obx(() => Wrap(
                  spacing: 8,
                  children: controller.supportedAssistants.map((assistant) => 
                    ChoiceChip(
                      avatar: CircleAvatar(
                        backgroundImage: AssetImage(assistant['avatar']!),
                      ),
                      label: Text(assistant['name']!),
                      selected: controller.defaultAssistant.value == assistant['code'],
                      onSelected: (selected) {
                        if (selected) {
                          controller.updateDefaultAssistant(assistant['code']!);
                        }
                      },
                    ),
                  ).toList(),
                )),
              ],
            ),
          ),

          const Divider(),

          // 温度参数设置
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('温度', style: TextStyle(fontSize: 16)),
                    Obx(() => Text('${controller.temperature.value.toStringAsFixed(2)}'))
                  ],
                ),
                const SizedBox(height: 8),
                Obx(() => Slider(
                  value: controller.temperature.value,
                  min: 0.0,
                  max: 2.0,
                  divisions: 20,
                  label: controller.temperature.value.toStringAsFixed(2),
                  onChanged: controller.updateTemperature,
                )),
                const Text(
                  '较低的值会使回答更加确定，较高的值会使回答更加随机和创造性',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),

          const Divider(),

          // 最大Token设置
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('最大Token数', style: TextStyle(fontSize: 16)),
                    Obx(() => Text('${controller.maxTokens.value}')),
                  ],
                ),
                const SizedBox(height: 8),
                Obx(() => Slider(
                  value: controller.maxTokens.value.toDouble(),
                  min: 256,
                  max: 4096,
                  divisions: 15,
                  label: '${controller.maxTokens.value}',
                  onChanged: (value) => controller.updateMaxTokens(value.toInt()),
                )),
                const Text(
                  '控制单次回答的最大长度，较大的值会消耗更多的额度',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 