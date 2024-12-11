import 'package:flutter/material.dart';
import '../services/theme_service.dart';
import '../models/theme_config.dart';

class ThemeSettingsScreen extends StatefulWidget {
  const ThemeSettingsScreen({Key? key}) : super(key: key);

  @override
  State<ThemeSettingsScreen> createState() => _ThemeSettingsScreenState();
}

class _ThemeSettingsScreenState extends State<ThemeSettingsScreen> {
  final _themeService = ThemeService();
  late ThemeConfig _currentConfig;

  @override
  void initState() {
    super.initState();
    _currentConfig = _themeService.themeConfig;
  }

  void _saveChanges() async {
    await _themeService.setThemeConfig(_currentConfig);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('主题设置已保存')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('主题设置'),
        actions: [
          TextButton(
            onPressed: () async {
              await _themeService.resetThemeSettings();
              setState(() {
                _currentConfig = _themeService.themeConfig;
              });
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('已重置主题设置')),
              );
            },
            child: const Text('重置'),
          ),
        ],
      ),
      body: ListView(
        children: [
          _buildSection(
            '主题模式',
            [
              RadioListTile<ThemeMode>(
                title: const Text('跟随系统'),
                value: ThemeMode.system,
                groupValue: _themeService.themeMode,
                onChanged: (value) {
                  if (value != null) {
                    _themeService.setThemeMode(value);
                  }
                },
              ),
              RadioListTile<ThemeMode>(
                title: const Text('浅色模式'),
                value: ThemeMode.light,
                groupValue: _themeService.themeMode,
                onChanged: (value) {
                  if (value != null) {
                    _themeService.setThemeMode(value);
                  }
                },
              ),
              RadioListTile<ThemeMode>(
                title: const Text('深色模式'),
                value: ThemeMode.dark,
                groupValue: _themeService.themeMode,
                onChanged: (value) {
                  if (value != null) {
                    _themeService.setThemeMode(value);
                  }
                },
              ),
            ],
          ),
          _buildSection(
            '主题颜色',
            [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: _themeService.presetColors.map((color) {
                    return _buildColorOption(color);
                  }).toList(),
                ),
              ),
            ],
          ),
          _buildSection(
            '预设主题',
            [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _themeService.presetConfigs.keys.map((name) {
                    return ChoiceChip(
                      label: Text(name),
                      selected: _currentConfig == _themeService.presetConfigs[name],
                      onSelected: (selected) {
                        if (selected) {
                          setState(() {
                            _currentConfig =
                                _themeService.presetConfigs[name] ?? _currentConfig;
                          });
                          _saveChanges();
                        }
                      },
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
          _buildSection(
            '界面风格',
            [
              SwitchListTile(
                title: const Text('使用Material 3'),
                subtitle: const Text('启用新一代Material Design风格'),
                value: _themeService.useMaterial3,
                onChanged: (value) {
                  _themeService.setUseMaterial3(value);
                },
              ),
              SwitchListTile(
                title: const Text('使用阴影'),
                subtitle: const Text('为界面元素添加立体感'),
                value: _currentConfig.useShadows,
                onChanged: (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(useShadows: value);
                  });
                  _saveChanges();
                },
              ),
              SwitchListTile(
                title: const Text('使用渐变'),
                subtitle: const Text('为界面添加渐变效果'),
                value: _currentConfig.useGradients,
                onChanged: (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(useGradients: value);
                  });
                  _saveChanges();
                },
              ),
              SwitchListTile(
                title: const Text('使用动画'),
                subtitle: const Text('启用界面过渡动画'),
                value: _currentConfig.useAnimations,
                onChanged: (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(useAnimations: value);
                  });
                  _saveChanges();
                },
              ),
              SwitchListTile(
                title: const Text('紧凑布局'),
                subtitle: const Text('减小界面元素间距'),
                value: _currentConfig.isDense,
                onChanged: (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(isDense: value);
                  });
                  _saveChanges();
                },
              ),
            ],
          ),
          _buildSection(
            '自定义选项',
            [
              _buildSliderOption(
                '圆角大小',
                _currentConfig.borderRadius,
                4,
                32,
                (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(borderRadius: value);
                  });
                  _saveChanges();
                },
              ),
              _buildSliderOption(
                '阴影深度',
                _currentConfig.elevation,
                0,
                8,
                (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(elevation: value);
                  });
                  _saveChanges();
                },
              ),
              _buildSliderOption(
                '间距大小',
                _currentConfig.spacing,
                8,
                24,
                (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(spacing: value);
                  });
                  _saveChanges();
                },
              ),
              _buildSliderOption(
                '图标大小',
                _currentConfig.iconSize,
                16,
                32,
                (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(iconSize: value);
                  });
                  _saveChanges();
                },
              ),
              _buildSliderOption(
                '字体大小',
                _currentConfig.fontSize,
                12,
                18,
                (value) {
                  setState(() {
                    _currentConfig = _currentConfig.copyWith(fontSize: value);
                  });
                  _saveChanges();
                },
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '提示：部分设置可能需要重启应用后生效。',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }

  Widget _buildColorOption(Color color) {
    final isSelected = _themeService.primaryColor == color;
    return GestureDetector(
      onTap: () => _themeService.setPrimaryColor(color),
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          border: Border.all(
            color: isSelected ? Colors.white : Colors.transparent,
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: isSelected
            ? const Icon(
                Icons.check,
                color: Colors.white,
              )
            : null,
      ),
    );
  }

  Widget _buildSliderOption(
    String label,
    double value,
    double min,
    double max,
    ValueChanged<double> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label),
              Text(value.toStringAsFixed(1)),
            ],
          ),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: ((max - min) * 2).toInt(),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
} 