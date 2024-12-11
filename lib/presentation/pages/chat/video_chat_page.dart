import 'package:flutter/material.dart';
import '../../widgets/video_preview.dart';
import '../../widgets/chat_bubble.dart';
import '../../widgets/voice_wave_animation.dart';
import '../../../services/video_service.dart';
import '../../../services/voice_service.dart';
import '../../../services/api/health_check_service.dart';
import '../../../models/chat_message.dart';

class VideoChatPage extends StatefulWidget {
  const VideoChatPage({Key? key}) : super(key: key);

  @override
  _VideoChatPageState createState() => _VideoChatPageState();
}

class _VideoChatPageState extends State<VideoChatPage> {
  final VideoService _videoService = VideoService();
  final VoiceService _voiceService = VoiceService();
  final HealthCheckService _healthCheckService = HealthCheckService();
  final List<ChatMessage> _messages = [];
  bool _isVideoOn = false;
  bool _isRecording = false;
  Map<String, dynamic> _healthData = {};

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      await _videoService.initialize();
      await _voiceService.initialize();
      
      // 订阅健康数据流
      _videoService.healthDataStream.listen((healthData) {
        setState(() {
          _healthData = healthData;
          _addHealthMessage(healthData);
        });
      });
    } catch (e) {
      _showErrorDialog('服务初始化失败: $e');
    }
  }

  void _addHealthMessage(Map<String, dynamic> healthData) {
    // 只在检测到异常或重要变化时添加消息
    if (_shouldAddHealthMessage(healthData)) {
      final message = ChatMessage(
        id: DateTime.now().toString(),
        content: _generateHealthMessage(healthData),
        type: MessageType.healthReport,
        sender: MessageSender.assistant,
        healthData: healthData,
      );

      setState(() {
        _messages.add(message);
      });
    }
  }

  bool _shouldAddHealthMessage(Map<String, dynamic> healthData) {
    // TODO: 实现健康数据变化检测逻辑
    return true;
  }

  String _generateHealthMessage(Map<String, dynamic> healthData) {
    final vitalSigns = healthData['vital_signs'];
    if (vitalSigns == null) return '正在进行健康检测...';

    return '我注意到您的生命体征有一些变化：\n'
        '心率: ${vitalSigns['heart_rate']} bpm\n'
        '血压: ${vitalSigns['blood_pressure']}\n'
        '呼吸率: ${vitalSigns['respiratory_rate']}\n'
        '血氧: ${vitalSigns['blood_oxygen']}%';
  }

  void _toggleVideo() {
    setState(() {
      _isVideoOn = !_isVideoOn;
    });
    if (_isVideoOn) {
      _videoService.startVideo();
    } else {
      _videoService.stopVideo();
    }
  }

  void _toggleVoiceRecording() {
    setState(() {
      _isRecording = !_isRecording;
    });
    if (_isRecording) {
      _voiceService.startRecording();
    } else {
      _voiceService.stopRecording();
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('错误'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('小艾智能助理'),
        actions: [
          IconButton(
            icon: Icon(_isVideoOn ? Icons.videocam : Icons.videocam_off),
            onPressed: _toggleVideo,
          ),
        ],
      ),
      body: Column(
        children: [
          // 健康数据面板
          if (_healthData.isNotEmpty) _buildHealthPanel(),
          
          // 视频预览区域
          if (_isVideoOn)
            Container(
              height: 200,
              child: const VideoPreview(),
            ),
          
          // 聊天消息列表
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return ChatBubble(message: message);
              },
            ),
          ),
          
          // 底部输入区域
          Container(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                // 语音输入按钮
                GestureDetector(
                  onTapDown: (_) => _toggleVoiceRecording(),
                  onTapUp: (_) => _toggleVoiceRecording(),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _isRecording ? Colors.red : Colors.blue,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      _isRecording ? Icons.mic : Icons.mic_none,
                      color: Colors.white,
                    ),
                  ),
                ),
                
                // 语音波形动画
                if (_isRecording)
                  const Expanded(
                    child: VoiceWaveAnimation(),
                  ),
                
                // 发送按钮
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: () {
                    // TODO: 实现发送消息逻辑
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthPanel() {
    final vitalSigns = _healthData['vital_signs'];
    if (vitalSigns == null) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '实时健康指标',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildHealthIndicator(
                  icon: Icons.favorite,
                  label: '心率',
                  value: '${vitalSigns['heart_rate']} bpm',
                ),
                _buildHealthIndicator(
                  icon: Icons.speed,
                  label: '血压',
                  value: vitalSigns['blood_pressure'],
                ),
                _buildHealthIndicator(
                  icon: Icons.air,
                  label: '呼吸率',
                  value: '${vitalSigns['respiratory_rate']}',
                ),
                _buildHealthIndicator(
                  icon: Icons.opacity,
                  label: '血氧',
                  value: '${vitalSigns['blood_oxygen']}%',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthIndicator({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: Theme.of(context).primaryColor),
        Text(label, style: const TextStyle(fontSize: 12)),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _videoService.dispose();
    _voiceService.dispose();
    super.dispose();
  }
} 