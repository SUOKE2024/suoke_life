import 'package:flutter/material.dart';
import 'package:suoke_life/presentation/visualization/providers/visualization_providers.dart';

class ControlPanel extends StatelessWidget {
  final VisualizationMode mode;
  final Function(VisualizationMode) onModeChanged;
  final Function(String) onLayoutChanged;
  final Function(Map<String, dynamic>) onFilterChanged;

  const ControlPanel({
    super.key,
    required this.mode,
    required this.onModeChanged,
    required this.onLayoutChanged,
    required this.onFilterChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Container(
        padding: const EdgeInsets.all(16),
        width: 300,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '可视化控制面板',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            
            // 可视化模式选择
            Text(
              '可视化模式',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            SegmentedButton<VisualizationMode>(
              segments: const [
                ButtonSegment<VisualizationMode>(
                  value: VisualizationMode.mode3D,
                  label: Text('3D'),
                  icon: Icon(Icons.view_in_ar),
                ),
                ButtonSegment<VisualizationMode>(
                  value: VisualizationMode.modeVR,
                  label: Text('VR'),
                  icon: Icon(Icons.vrpano),
                ),
                ButtonSegment<VisualizationMode>(
                  value: VisualizationMode.modeAR,
                  label: Text('AR'),
                  icon: Icon(Icons.camera),
                ),
              ],
              selected: {mode},
              onSelectionChanged: (Set<VisualizationMode> selected) {
                if (selected.isNotEmpty) {
                  onModeChanged(selected.first);
                }
              },
            ),
            const SizedBox(height: 16),

            // 布局算法选择
            Text(
              '布局算法',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: 'force-directed',
              items: const [
                DropdownMenuItem(
                  value: 'force-directed',
                  child: Text('力导向布局'),
                ),
                DropdownMenuItem(
                  value: 'circular',
                  child: Text('环形布局'),
                ),
                DropdownMenuItem(
                  value: 'hierarchical',
                  child: Text('层级布局'),
                ),
              ],
              onChanged: (value) {
                if (value != null) {
                  onLayoutChanged(value);
                }
              },
            ),
            const SizedBox(height: 16),

            // 过滤器
            Text(
              '节点过滤',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            FilterChipGroup(
              onFilterChanged: onFilterChanged,
            ),
          ],
        ),
      ),
    );
  }
}

class FilterChipGroup extends StatefulWidget {
  final Function(Map<String, dynamic>) onFilterChanged;

  const FilterChipGroup({
    super.key,
    required this.onFilterChanged,
  });

  @override
  State<FilterChipGroup> createState() => _FilterChipGroupState();
}

class _FilterChipGroupState extends State<FilterChipGroup> {
  final Map<String, bool> _filters = {
    '中医理论': false,
    '症状': false,
    '方剂': false,
    '穴位': false,
    '经络': false,
  };

  void _updateFilters() {
    widget.onFilterChanged({
      'types': _filters.entries
          .where((e) => e.value)
          .map((e) => e.key)
          .toList(),
    });
  }

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: _filters.entries.map((entry) {
        return FilterChip(
          label: Text(entry.key),
          selected: entry.value,
          onSelected: (bool selected) {
            setState(() {
              _filters[entry.key] = selected;
              _updateFilters();
            });
          },
        );
      }).toList(),
    );
  }
}