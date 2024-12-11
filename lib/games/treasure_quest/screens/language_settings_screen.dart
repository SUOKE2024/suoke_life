import 'package:flutter/material.dart';
import '../services/localization_service.dart';

class LanguageSettingsScreen extends StatefulWidget {
  const LanguageSettingsScreen({Key? key}) : super(key: key);

  @override
  State<LanguageSettingsScreen> createState() => _LanguageSettingsScreenState();
}

class _LanguageSettingsScreenState extends State<LanguageSettingsScreen> {
  final _localizationService = LocalizationService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('语言设置'),
        actions: [
          TextButton(
            onPressed: () async {
              await _localizationService.resetLocale();
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('已重置为默认语言')),
              );
            },
            child: const Text('重置'),
          ),
        ],
      ),
      body: ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '选择您的首��语言',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          const Divider(),
          ..._localizationService.supportedLocales.map((localeInfo) {
            final isSelected = _localizationService.currentLocale == localeInfo.locale;
            return ListTile(
              leading: Text(
                localeInfo.flag,
                style: const TextStyle(fontSize: 24),
              ),
              title: Text(localeInfo.name),
              subtitle: Text(_getLanguageDescription(localeInfo.locale)),
              trailing: isSelected
                  ? const Icon(
                      Icons.check_circle,
                      color: Colors.green,
                    )
                  : null,
              selected: isSelected,
              onTap: () async {
                await _localizationService.setLocale(localeInfo.locale);
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('已切换到${localeInfo.name}'),
                    duration: const Duration(seconds: 1),
                  ),
                );
              },
            );
          }).toList(),
          const Divider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '注意：切换语言后，部分内容可能需要重启应用才能完全生效。',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ),
          // 语言使用提示
          _buildLanguageUsageSection(),
        ],
      ),
    );
  }

  Widget _buildLanguageUsageSection() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.blue.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.lightbulb_outline,
                color: Colors.blue,
                size: 20,
              ),
              SizedBox(width: 8),
              Text(
                '语言使用说明',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildUsagePoint('系统语言优先：应用将优先使用您的系统语言设置'),
          _buildUsagePoint('离线支持：主要界面支持离线切换语言'),
          _buildUsagePoint('动态内容：部分动态内容可能仅支持特定语言'),
          _buildUsagePoint('社区内容：用户生成的内容将保持原始语言'),
        ],
      ),
    );
  }

  Widget _buildUsagePoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '• ',
            style: TextStyle(
              color: Colors.blue,
              fontWeight: FontWeight.bold,
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 14,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getLanguageDescription(Locale locale) {
    switch ('${locale.languageCode}_${locale.countryCode}') {
      case 'zh_CN':
        return '简体中文 - 中国大陆地区';
      case 'zh_TW':
        return '繁體中文 - 港澳台地区';
      case 'en_US':
        return 'English - United States';
      case 'ja_JP':
        return '日本語 - 日本';
      default:
        return locale.toString();
    }
  }
} 