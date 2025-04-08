import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'optimization_manager.dart';

class OptimizationSettingsWidget extends ConsumerWidget {
  const OptimizationSettingsWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(optimizationManagerProvider);
    final settings = state.settings;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context, ref, state),
            const SizedBox(height: 16),
            _buildSettingsForm(context, ref, settings),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(
      BuildContext context, WidgetRef ref, OptimizationState state) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Text(
          '优化设置',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        Row(
          children: [
            const Text('自动优化'),
            const SizedBox(width: 8),
            Switch(
              value: state.isAutoOptimizing,
              onChanged: (value) {
                if (value) {
                  ref
                      .read(optimizationManagerProvider.notifier)
                      .enableAutoOptimization();
                } else {
                  ref
                      .read(optimizationManagerProvider.notifier)
                      .disableAutoOptimization();
                }
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSettingsForm(
      BuildContext context, WidgetRef ref, OptimizationSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildOptimizationLevelSelector(context, ref),
        const SizedBox(height: 16),
        _buildRenderingSettings(settings),
        const SizedBox(height: 16),
        _buildVisibilitySettings(settings),
        const SizedBox(height: 16),
        _buildPerformanceSettings(settings),
      ],
    );
  }

  Widget _buildOptimizationLevelSelector(BuildContext context, WidgetRef ref) {
    final state = ref.watch(optimizationManagerProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '优化级别',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<OptimizationLevel>(
          value: state.currentLevel,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          ),
          items: OptimizationLevel.values.map((level) {
            return DropdownMenuItem(
              value: level,
              child: Text(_getOptimizationLevelName(level)),
            );
          }).toList(),
          onChanged: (level) {
            if (level != null) {
              ref
                  .read(optimizationManagerProvider.notifier)
                  .setOptimizationLevel(level);
            }
          },
        ),
      ],
    );
  }

  Widget _buildRenderingSettings(OptimizationSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '渲染设置',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        _buildSettingTile(
          '渲染质量',
          '${(settings.renderQuality * 100).toInt()}%',
          subtitle: '降低渲染质量可以提高性能',
        ),
        _buildSettingSwitch(
          '启用阴影',
          settings.enableShadows,
          subtitle: '禁用阴影可以提高性能',
        ),
        _buildSettingSwitch(
          '启用后处理',
          settings.enablePostProcessing,
          subtitle: '禁用后处理效果可以提高性能',
        ),
        _buildSettingSwitch(
          '启用抗锯齿',
          settings.enableAntiAliasing,
          subtitle: '禁用抗锯齿可以提高性能',
        ),
      ],
    );
  }

  Widget _buildVisibilitySettings(OptimizationSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '可见性设置',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        _buildSettingTile(
          '最大可见节点数',
          '${settings.maxVisibleNodes}',
          subtitle: '限制可见节点数量可以提高性能',
        ),
        _buildSettingTile(
          '最大可见边数',
          '${settings.maxVisibleEdges}',
          subtitle: '限制可见边数量可以提高性能',
        ),
        _buildSettingSwitch(
          '启用视锥体剔除',
          settings.enableCulling,
          subtitle: '启用剔除可以提高性能',
        ),
        _buildSettingSwitch(
          '启用LOD',
          settings.enableLOD,
          subtitle: '启用LOD可以提高性能',
        ),
      ],
    );
  }

  Widget _buildPerformanceSettings(OptimizationSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '性能设置',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        _buildSettingSwitch(
          '启用实例化',
          settings.enableInstancing,
          subtitle: '启用实例化可以提高性能',
        ),
        _buildSettingSwitch(
          '启用压缩',
          settings.enableCompression,
          subtitle: '启用压缩可以减少内存使用',
        ),
      ],
    );
  }

  Widget _buildSettingTile(String title, String value, {String? subtitle}) {
    return ListTile(
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: Text(
        value,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildSettingSwitch(String title, bool value, {String? subtitle}) {
    return ListTile(
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: Switch(
        value: value,
        onChanged: null, // 由优化级别统一控制
      ),
    );
  }

  String _getOptimizationLevelName(OptimizationLevel level) {
    switch (level) {
      case OptimizationLevel.none:
        return '无优化';
      case OptimizationLevel.low:
        return '低级优化';
      case OptimizationLevel.medium:
        return '中级优化';
      case OptimizationLevel.high:
        return '高级优化';
      case OptimizationLevel.extreme:
        return '极限优化';
    }
  }
}