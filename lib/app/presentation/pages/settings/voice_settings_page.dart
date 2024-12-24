import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/settings/voice_settings_controller.dart';

class VoiceSettingsPage extends GetView<VoiceSettingsController> {
  const VoiceSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('语音设置'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.resetSettings,
          ),
        ],
      ),
      body: ListView(
        children: [
          // 语音识别开关
          Obx(() => SwitchListTile(
            title: const Text('语音识别'),
            subtitle: const Text('开启后可以使用语音输入'),
            value: controller.isRecognitionEnabled.value,
            onChanged: controller.toggleRecognition,
          )),
          
          // 语音合成开关
          Obx(() => SwitchListTile(
            title: const Text('语音合成'),
            subtitle: const Text('开启后可以听到AI的语音回复'),
            value: controller.isSynthesisEnabled.value,
            onChanged: controller.toggleSynthesis,
          )),
          
          const Divider(),
          
          // 音量控制
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('音量'),
                Obx(() => Slider(
                  value: controller.volume.value,
                  min: 0.0,
                  max: 1.0,
                  divisions: 10,
                  label: '${(controller.volume.value * 100).toInt()}%',
                  onChanged: controller.updateVolume,
                )),
              ],
            ),
          ),
          
          // 语速控制
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('语速'),
                Obx(() => Slider(
                  value: controller.speed.value,
                  min: 0.5,
                  max: 2.0,
                  divisions: 15,
                  label: '${controller.speed.value}x',
                  onChanged: controller.updateSpeed,
                )),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 