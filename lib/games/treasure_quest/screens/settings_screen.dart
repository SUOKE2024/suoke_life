import 'package:flutter/material.dart';
import '../models/player.dart';
import '../services/game_service.dart';
import '../services/settings_service.dart';

class SettingsScreen extends StatefulWidget {
  final Player player;
  final GameService gameService;

  const SettingsScreen({
    Key? key,
    required this.player,
    required this.gameService,
  }) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _settingsService = SettingsService();

  // 游戏设置
  late bool _backgroundMusic;
  late bool _soundEffects;
  late bool _vibration;
  late bool _autoRotate;
  late bool _showDistance;
  late bool _showCompass;
  late double _musicVolume;
  late double _effectsVolume;
  late String _mapStyle;
  late String _language;
  late bool _highQualityGraphics;
  late bool _powerSavingMode;
  late bool _showFPS;
  late bool _showPing;

  // 地图样式选项
  final List<String> _mapStyles = ['标准', '卫星', '地形', '复古'];
  
  // 语言选项
  final List<String> _languages = ['简体中文', '繁体中文', 'English', '日本語'];

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() {
      _backgroundMusic = _settingsService.getBackgroundMusic();
      _soundEffects = _settingsService.getSoundEffects();
      _vibration = _settingsService.getVibration();
      _autoRotate = _settingsService.getAutoRotate();
      _showDistance = _settingsService.getShowDistance();
      _showCompass = _settingsService.getShowCompass();
      _musicVolume = _settingsService.getMusicVolume();
      _effectsVolume = _settingsService.getEffectsVolume();
      _mapStyle = _settingsService.getMapStyle();
      _language = _settingsService.getLanguage();
      _highQualityGraphics = _settingsService.getHighQualityGraphics();
      _powerSavingMode = _settingsService.getPowerSavingMode();
      _showFPS = _settingsService.getShowFPS();
      _showPing = _settingsService.getShowPing();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          _buildSection(
            '声音设置',
            [
              SwitchListTile(
                title: const Text('背景音乐'),
                value: _backgroundMusic,
                onChanged: (value) {
                  _updateBackgroundMusic(value);
                },
              ),
              if (_backgroundMusic)
                _buildVolumeSlider(
                  '音乐音量',
                  _musicVolume,
                  (value) {
                    _updateMusicVolume(value);
                  },
                ),
              SwitchListTile(
                title: const Text('音效'),
                value: _soundEffects,
                onChanged: (value) {
                  _updateSoundEffects(value);
                },
              ),
              if (_soundEffects)
                _buildVolumeSlider(
                  '音效音量',
                  _effectsVolume,
                  (value) {
                    _updateEffectsVolume(value);
                  },
                ),
              SwitchListTile(
                title: const Text('震动'),
                value: _vibration,
                onChanged: (value) {
                  _updateVibration(value);
                },
              ),
            ],
          ),
          _buildSection(
            '显示设置',
            [
              SwitchListTile(
                title: const Text('高品质图像'),
                subtitle: const Text('更好的视觉效果，但会消耗更多电量'),
                value: _highQualityGraphics,
                onChanged: (value) {
                  _updateHighQualityGraphics(value);
                },
              ),
              SwitchListTile(
                title: const Text('省电模式'),
                subtitle: const Text('降低画面质量以节省电量'),
                value: _powerSavingMode,
                onChanged: (value) {
                  _updatePowerSavingMode(value);
                },
              ),
              SwitchListTile(
                title: const Text('自动旋转'),
                value: _autoRotate,
                onChanged: (value) {
                  _updateAutoRotate(value);
                },
              ),
            ],
          ),
          _buildSection(
            '地图设置',
            [
              _buildDropdownTile(
                '地图样式',
                _mapStyle,
                _mapStyles,
                (value) {
                  if (value != null) {
                    _updateMapStyle(value);
                  }
                },
              ),
              SwitchListTile(
                title: const Text('显示距离'),
                value: _showDistance,
                onChanged: (value) {
                  _updateShowDistance(value);
                },
              ),
              SwitchListTile(
                title: const Text('显示指南针'),
                value: _showCompass,
                onChanged: (value) {
                  _updateShowCompass(value);
                },
              ),
            ],
          ),
          _buildSection(
            '调试设置',
            [
              SwitchListTile(
                title: const Text('显示FPS'),
                value: _showFPS,
                onChanged: (value) {
                  _updateShowFPS(value);
                },
              ),
              SwitchListTile(
                title: const Text('显示网络延迟'),
                value: _showPing,
                onChanged: (value) {
                  _updateShowPing(value);
                },
              ),
            ],
          ),
          _buildSection(
            '语言设置',
            [
              _buildDropdownTile(
                '界面语言',
                _language,
                _languages,
                (value) {
                  if (value != null) {
                    _updateLanguage(value);
                  }
                },
              ),
            ],
          ),
          _buildSection(
            '账号设置',
            [
              ListTile(
                title: const Text('修改密码'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 实现修改密码功能
                },
              ),
              ListTile(
                title: const Text('隐私设置'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 实现隐私设置功能
                },
              ),
              ListTile(
                title: const Text('注销账号'),
                textColor: Colors.red,
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  _showDeleteAccountDialog();
                },
              ),
            ],
          ),
          _buildSection(
            '关于',
            [
              ListTile(
                title: const Text('版本信息'),
                subtitle: const Text('v1.0.0'),
              ),
              ListTile(
                title: const Text('用户协议'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 显示用户协议
                },
              ),
              ListTile(
                title: const Text('隐私政策'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: 显示隐私政策
                },
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: () {
                // TODO: 实现退出登录功能
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: const Text('退出登录'),
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

  Widget _buildVolumeSlider(
    String label,
    double value,
    ValueChanged<double> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          const Icon(Icons.volume_up),
          const SizedBox(width: 16),
          Expanded(
            child: Slider(
              value: value,
              onChanged: onChanged,
              divisions: 100,
              label: '${(value * 100).round()}%',
            ),
          ),
          SizedBox(
            width: 40,
            child: Text(
              '${(value * 100).round()}%',
              style: TextStyle(
                color: Colors.grey[600],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownTile(
    String title,
    String value,
    List<String> items,
    ValueChanged<String?> onChanged,
  ) {
    return ListTile(
      title: Text(title),
      trailing: DropdownButton<String>(
        value: value,
        items: items.map((item) {
          return DropdownMenuItem(
            value: item,
            child: Text(item),
          );
        }).toList(),
        onChanged: onChanged,
        underline: const SizedBox(),
      ),
    );
  }

  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('注销账号'),
        content: const Text(
          '注销账号后，您的所有游戏数据将被永久删除，且无法恢复。\n'
          '您确定要继续吗？',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              // TODO: 实现注销账号功能
              Navigator.of(context).pop();
            },
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: const Text('确认注销'),
          ),
        ],
      ),
    );
  }

  // 更新设置值的方法
  Future<void> _updateBackgroundMusic(bool value) async {
    await _settingsService.setBackgroundMusic(value);
    setState(() => _backgroundMusic = value);
  }

  Future<void> _updateSoundEffects(bool value) async {
    await _settingsService.setSoundEffects(value);
    setState(() => _soundEffects = value);
  }

  Future<void> _updateVibration(bool value) async {
    await _settingsService.setVibration(value);
    setState(() => _vibration = value);
  }

  Future<void> _updateAutoRotate(bool value) async {
    await _settingsService.setAutoRotate(value);
    setState(() => _autoRotate = value);
  }

  Future<void> _updateShowDistance(bool value) async {
    await _settingsService.setShowDistance(value);
    setState(() => _showDistance = value);
  }

  Future<void> _updateShowCompass(bool value) async {
    await _settingsService.setShowCompass(value);
    setState(() => _showCompass = value);
  }

  Future<void> _updateMusicVolume(double value) async {
    await _settingsService.setMusicVolume(value);
    setState(() => _musicVolume = value);
  }

  Future<void> _updateEffectsVolume(double value) async {
    await _settingsService.setEffectsVolume(value);
    setState(() => _effectsVolume = value);
  }

  Future<void> _updateMapStyle(String value) async {
    await _settingsService.setMapStyle(value);
    setState(() => _mapStyle = value);
  }

  Future<void> _updateLanguage(String value) async {
    await _settingsService.setLanguage(value);
    setState(() => _language = value);
  }

  Future<void> _updateHighQualityGraphics(bool value) async {
    await _settingsService.setHighQualityGraphics(value);
    setState(() => _highQualityGraphics = value);
  }

  Future<void> _updatePowerSavingMode(bool value) async {
    await _settingsService.setPowerSavingMode(value);
    setState(() => _powerSavingMode = value);
  }

  Future<void> _updateShowFPS(bool value) async {
    await _settingsService.setShowFPS(value);
    setState(() => _showFPS = value);
  }

  Future<void> _updateShowPing(bool value) async {
    await _settingsService.setShowPing(value);
    setState(() => _showPing = value);
  }

  Future<void> _resetAllSettings() async {
    await _settingsService.resetAllSettings();
    await _loadSettings();
  }
} 