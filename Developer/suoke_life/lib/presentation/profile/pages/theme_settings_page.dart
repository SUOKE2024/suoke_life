import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/cards/app_card.dart';

/// 主题设置页面
@RoutePage()
class ThemeSettingsPage extends ConsumerWidget {
  /// 创建主题设置页面
  const ThemeSettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appConfig = ref.watch(appConfigProvider);
    final appConfigNotifier = ref.read(appConfigProvider.notifier);

    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('主题设置'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 主题模式选择
          AppCard(
            title: '主题模式',
            content: Column(
              children: [
                _buildThemeModeOption(
                  context: context,
                  title: '系统',
                  subtitle: '跟随系统主题',
                  icon: Icons.auto_awesome,
                  isSelected: appConfig.themeMode == ThemeMode.system,
                  onTap: () =>
                      appConfigNotifier.updateThemeMode(ThemeMode.system),
                ),
                const Divider(),
                _buildThemeModeOption(
                  context: context,
                  title: '亮色模式',
                  subtitle: '始终使用亮色主题',
                  icon: Icons.light_mode,
                  isSelected: appConfig.themeMode == ThemeMode.light,
                  onTap: () =>
                      appConfigNotifier.updateThemeMode(ThemeMode.light),
                ),
                const Divider(),
                _buildThemeModeOption(
                  context: context,
                  title: '暗色模式',
                  subtitle: '始终使用暗色主题',
                  icon: Icons.dark_mode,
                  isSelected: appConfig.themeMode == ThemeMode.dark,
                  onTap: () =>
                      appConfigNotifier.updateThemeMode(ThemeMode.dark),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // 字体大小调整
          AppCard(
            title: '字体大小',
            content: Column(
              children: [
                Slider(
                  value: appConfig.fontSize,
                  min: 12.0,
                  max: 20.0,
                  divisions: 8,
                  label: '${appConfig.fontSize.toStringAsFixed(1)}',
                  onChanged: (value) {
                    appConfigNotifier.updateFontSize(value);
                  },
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('较小',
                          style: TextStyle(
                            fontSize: 12,
                            color: isDarkMode
                                ? AppColors.darkTextSecondary
                                : AppColors.lightTextSecondary,
                          )),
                      Text('${appConfig.fontSize.toStringAsFixed(1)}',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: AppColors.primaryColor,
                          )),
                      Text('较大',
                          style: TextStyle(
                            fontSize: 12,
                            color: isDarkMode
                                ? AppColors.darkTextSecondary
                                : AppColors.lightTextSecondary,
                          )),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    '预览文本：索克生活APP致力于为用户提供全方位的健康管理服务。',
                    style: TextStyle(fontSize: appConfig.fontSize),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // 自动检测舌诊图片开关
          AppCard(
            title: '功能设置',
            content: SwitchListTile(
              title: const Text('自动识别舌诊图片'),
              subtitle: const Text('上传舌头图片时自动启动舌诊分析'),
              value: appConfig.autoDetectTongueImages,
              onChanged: (value) {
                appConfigNotifier.updateAutoDetectTongueImages(value);
              },
              activeColor: AppColors.primaryColor,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建主题模式选项
  Widget _buildThemeModeOption({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return ListTile(
      leading: Icon(
        icon,
        color: isSelected
            ? AppColors.primaryColor
            : (isDarkMode ? Colors.white70 : Colors.black54),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: isSelected
          ? const Icon(Icons.check_circle, color: AppColors.primaryColor)
          : null,
      onTap: onTap,
    );
  }
}
