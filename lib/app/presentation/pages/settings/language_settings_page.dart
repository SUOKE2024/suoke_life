import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/settings/language_settings_controller.dart';

class LanguageSettingsPage extends GetView<LanguageSettingsController> {
  const LanguageSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('语言设置'),
      ),
      body: Obx(() => ListView(
        children: controller.supportedLanguages.map((language) => ListTile(
          title: Text(language['name']!),
          trailing: Radio<String>(
            value: language['code']!,
            groupValue: controller.selectedLanguage.value,
            onChanged: (value) => controller.changeLanguage(value!),
          ),
        )).toList(),
      )),
    );
  }
} 