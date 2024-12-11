import 'package:flutter/material.dart';
import 'package:shared_preferences.dart';
import '../../services/voice_service.dart';

class VoiceSettingsPage extends StatefulWidget {
  const VoiceSettingsPage({super.key});

  @override
  State<VoiceSettingsPage> createState() => _VoiceSettingsPageState();
}

class _VoiceSettingsPageState extends State<VoiceSettingsPage> {
  late final VoiceService _voiceService;
  final _previewController = TextEditingController();
  bool _isLoading = true;
  double _speechRate = 0.5;
  double _volume = 1.0;
  double _pitch = 1.0;

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  @override
  void dispose() {
    _previewController.dispose();
    super.dispose();
  }

  Future<void> _initializeService() async {
    final prefs = await SharedPreferences.getInstance();
    _voiceService = VoiceService(
      nasBasePath: 'voice_records',
      prefs: prefs,
    );
    await _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);
    try {
      final settings = await _voiceService.getSettings();
      setState(() {
        _speechRate = settings['speechRate']!;
        _volume = settings['volume']!;
        _pitch = settings['pitch']!;
        _previewController.text = '你好，我是语音助手';
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _previewVoice() async {
    if (_previewController.text.isEmpty) return;
    await _voiceService.speak(_previewController.text);
  }

  Widget _buildSliderSection({
    required String title,
    required String subtitle,
    required double value,
    required ValueChanged<double> onChanged,
    required double min,
    required double max,
    int? divisions,
    String? valueLabel,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ListTile(
          title: Text(title),
          subtitle: Text(subtitle),
          trailing: Text(valueLabel ?? value.toStringAsFixed(1)),
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: divisions,
          onChanged: onChanged,
        ),
        const Divider(),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('语音设置'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadSettings,
            tooltip: '重置设置',
          ),
        ],
      ),
      body: ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              '语音参数',
              style: theme.textTheme.titleMedium,
            ),
          ),
          _buildSliderSection(
            title: '语速',
            subtitle: '调整语音播放的速度',
            value: _speechRate,
            min: 0.1,
            max: 1.0,
            divisions: 9,
            onChanged: (value) {
              setState(() => _speechRate = value);
              _voiceService.setSpeechRate(value);
            },
            valueLabel: '${(_speechRate * 100).toInt()}%',
          ),
          _buildSliderSection(
            title: '音量',
            subtitle: '调整语音播放的音量',
            value: _volume,
            min: 0.0,
            max: 1.0,
            divisions: 10,
            onChanged: (value) {
              setState(() => _volume = value);
              _voiceService.setVolume(value);
            },
            valueLabel: '${(_volume * 100).toInt()}%',
          ),
          _buildSliderSection(
            title: '音调',
            subtitle: '调整语音的音调高低',
            value: _pitch,
            min: 0.5,
            max: 2.0,
            divisions: 15,
            onChanged: (value) {
              setState(() => _pitch = value);
              _voiceService.setPitch(value);
            },
          ),
          const Divider(height: 32),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '试听',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _previewController,
                  decoration: const InputDecoration(
                    hintText: '输入要试听的文本',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 16),
                Center(
                  child: ElevatedButton.icon(
                    onPressed: _previewVoice,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('试听'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 