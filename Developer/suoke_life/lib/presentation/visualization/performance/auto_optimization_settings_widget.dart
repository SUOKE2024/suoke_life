import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'auto_optimization_trigger.dart';
import 'optimization_manager.dart';

class AutoOptimizationSettingsWidget extends ConsumerWidget {
  const AutoOptimizationSettingsWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(autoOptimizationTriggerProvider);
    final config = state.config;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context, ref, state),
            const SizedBox(height: 16),
            _buildThresholds(context, ref, config),
            const SizedBox(height: 16),
            _buildLevelSettings(context, ref, config),
            const SizedBox(height: 16),
            if (state.lastTriggeredReason != null) _buildOptimizationHistory(context, state),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(
    BuildContext context,
    WidgetRef ref,
    AutoOptimizationTriggerState state,
  ) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '自动优化设置',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Row(
          children: [
            const Text('启用自动优化'),
            const SizedBox(width: 8),
            Switch(
              value: state.isEnabled && state.config.enableAutoTrigger,
              onChanged: (value) {
                if (value) {
                  ref.read(autoOptimizationTriggerProvider.notifier).enable();
                  
                  // 更新配置启用状态
                  final newConfig = state.config.copyWith(enableAutoTrigger: true);
                  ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
                } else {
                  // 禁用自动优化
                  ref.read(autoOptimizationTriggerProvider.notifier).disable();
                }
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildThresholds(
    BuildContext context,
    WidgetRef ref,
    OptimizationTriggerConfig config,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '触发阈值',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        _buildSliderSetting(
          context,
          ref,
          '帧率阈值',
          config.lowFpsThreshold,
          10.0,
          60.0,
          (value) {
            final newConfig = config.copyWith(lowFpsThreshold: value);
            ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
          },
          suffix: ' FPS',
          helperText: '帧率低于此值将触发优化',
        ),
        _buildSliderSetting(
          context,
          ref,
          '内存阈值',
          config.highMemoryThreshold,
          100.0,
          1000.0,
          (value) {
            final newConfig = config.copyWith(highMemoryThreshold: value);
            ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
          },
          suffix: ' MB',
          helperText: '内存使用超过此值将触发优化',
        ),
        _buildSliderSetting(
          context,
          ref,
          '节点数量阈值',
          config.highNodeCountThreshold.toDouble(),
          100.0,
          5000.0,
          (value) {
            final newConfig = config.copyWith(highNodeCountThreshold: value.toInt());
            ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
          },
          suffix: ' 个',
          helperText: '节点数量超过此值将触发优化',
        ),
        _buildSliderSetting(
          context,
          ref,
          '渲染时间阈值',
          config.highRenderTimeThreshold,
          8.0,
          33.0,
          (value) {
            final newConfig = config.copyWith(highRenderTimeThreshold: value);
            ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
          },
          suffix: ' ms',
          helperText: '渲染时间超过此值将触发优化',
        ),
        _buildSliderSetting(
          context,
          ref,
          '连续警告触发阈值',
          config.consecutiveWarningsThreshold.toDouble(),
          1.0,
          10.0,
          (value) {
            final newConfig = config.copyWith(consecutiveWarningsThreshold: value.toInt());
            ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
          },
          suffix: ' 次',
          helperText: '连续警告达到此值将触发优化',
        ),
      ],
    );
  }

  Widget _buildLevelSettings(
    BuildContext context,
    WidgetRef ref,
    OptimizationTriggerConfig config,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '优化级别设置',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildLevelDropdown(
                context,
                '初始级别',
                config.initialLevel,
                (level) {
                  if (level != null) {
                    final newConfig = config.copyWith(initialLevel: level);
                    ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
                    
                    // 重置到初始级别
                    ref.read(autoOptimizationTriggerProvider.notifier).resetToLevel(level);
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildLevelDropdown(
                context,
                '最大级别',
                config.maxLevel,
                (level) {
                  if (level != null) {
                    final newConfig = config.copyWith(maxLevel: level);
                    ref.read(autoOptimizationTriggerProvider.notifier).updateConfig(newConfig);
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.refresh),
            label: const Text('重置优化状态'),
            onPressed: () {
              ref.read(autoOptimizationTriggerProvider.notifier).resetToLevel(config.initialLevel);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildOptimizationHistory(
    BuildContext context,
    AutoOptimizationTriggerState state,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '优化历史',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('当前级别: ${_getLevelName(state.currentLevel)}'),
                  if (state.lastOptimizationTime != null)
                    Text(
                      '最近优化: ${_formatTime(state.lastOptimizationTime!)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                ],
              ),
              if (state.lastTriggeredReason != null) ...[
                const SizedBox(height: 8),
                Text(
                  '触发原因: ${state.lastTriggeredReason}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
              if (state.recentWarnings.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  '最近警告 (${state.recentWarnings.length}/${state.config.consecutiveWarningsThreshold}):',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                ...state.recentWarnings.map(
                  (warning) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Text(
                      '• $warning',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSliderSetting(
    BuildContext context,
    WidgetRef ref,
    String label,
    double value,
    double min,
    double max,
    Function(double) onChanged, {
    String? suffix,
    String? helperText,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label),
              Text(
                '${value.toStringAsFixed(1)}${suffix ?? ""}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: ((max - min) / (min * 0.1)).round(),
            onChanged: onChanged,
          ),
          if (helperText != null)
            Padding(
              padding: const EdgeInsets.only(top: 4.0),
              child: Text(
                helperText,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLevelDropdown(
    BuildContext context,
    String label,
    OptimizationLevel currentLevel,
    Function(OptimizationLevel?) onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label),
        const SizedBox(height: 4),
        DropdownButtonFormField<OptimizationLevel>(
          value: currentLevel,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
          items: OptimizationLevel.values.map((level) {
            return DropdownMenuItem(
              value: level,
              child: Text(_getLevelName(level)),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }

  String _getLevelName(OptimizationLevel level) {
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

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}:${time.second.toString().padLeft(2, '0')}';
  }
}