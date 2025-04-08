import 'package:flutter/material.dart';
import 'package:suoke_life/presentation/visualization/providers/visualization_providers.dart';

class VisualizationSettings extends StatefulWidget {
  final VisualizationMode mode;
  final Function(Map<String, dynamic>) onSettingsChanged;

  const VisualizationSettings({
    super.key,
    required this.mode,
    required this.onSettingsChanged,
  });

  @override
  State<VisualizationSettings> createState() => _VisualizationSettingsState();
}

class _VisualizationSettingsState extends State<VisualizationSettings> {
  late Map<String, dynamic> _settings;

  @override
  void initState() {
    super.initState();
    _settings = {
      'style': {
        'nodeSize': 1.0,
        'edgeWidth': 0.1,
        'defaultNodeColor': '#35BB78',
        'defaultEdgeColor': '#FF6800',
      },
      'interaction': {
        'rotationSpeed': 1.0,
        'zoomSpeed': 1.0,
        'enableSelection': true,
      },
    };
  }

  void _updateSettings() {
    widget.onSettingsChanged(_settings);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 样式设置
          Text(
            '样式设置',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          
          // 节点大小
          Row(
            children: [
              const Text('节点大小'),
              Expanded(
                child: Slider(
                  value: _settings['style']['nodeSize'],
                  min: 0.5,
                  max: 2.0,
                  divisions: 15,
                  label: _settings['style']['nodeSize'].toStringAsFixed(1),
                  onChanged: (value) {
                    setState(() {
                      _settings['style']['nodeSize'] = value;
                      _updateSettings();
                    });
                  },
                ),
              ),
            ],
          ),

          // 边宽度
          Row(
            children: [
              const Text('边宽度'),
              Expanded(
                child: Slider(
                  value: _settings['style']['edgeWidth'],
                  min: 0.1,
                  max: 1.0,
                  divisions: 9,
                  label: _settings['style']['edgeWidth'].toStringAsFixed(1),
                  onChanged: (value) {
                    setState(() {
                      _settings['style']['edgeWidth'] = value;
                      _updateSettings();
                    });
                  },
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 交互设置
          Text(
            '交互设置',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),

          // 旋转速度
          Row(
            children: [
              const Text('旋转速度'),
              Expanded(
                child: Slider(
                  value: _settings['interaction']['rotationSpeed'],
                  min: 0.5,
                  max: 2.0,
                  divisions: 15,
                  label: _settings['interaction']['rotationSpeed'].toStringAsFixed(1),
                  onChanged: (value) {
                    setState(() {
                      _settings['interaction']['rotationSpeed'] = value;
                      _updateSettings();
                    });
                  },
                ),
              ),
            ],
          ),

          // 缩放速度
          Row(
            children: [
              const Text('缩放速度'),
              Expanded(
                child: Slider(
                  value: _settings['interaction']['zoomSpeed'],
                  min: 0.5,
                  max: 2.0,
                  divisions: 15,
                  label: _settings['interaction']['zoomSpeed'].toStringAsFixed(1),
                  onChanged: (value) {
                    setState(() {
                      _settings['interaction']['zoomSpeed'] = value;
                      _updateSettings();
                    });
                  },
                ),
              ),
            ],
          ),

          // 启用选择
          SwitchListTile(
            title: const Text('启用节点选择'),
            value: _settings['interaction']['enableSelection'],
            onChanged: (value) {
              setState(() {
                _settings['interaction']['enableSelection'] = value;
                _updateSettings();
              });
            },
          ),

          if (widget.mode == VisualizationMode.modeVR) ...[
            const SizedBox(height: 16),
            Text(
              'VR设置',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            // 添加VR特定设置
          ],

          if (widget.mode == VisualizationMode.modeAR) ...[
            const SizedBox(height: 16),
            Text(
              'AR设置',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            // 添加AR特定设置
          ],
        ],
      ),
    );
  }
}