import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/constants/app_colors.dart';
import 'package:suoke_life/core/constants/app_strings.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/presentation/tcm/tcm_diagnosis_providers.dart';
import 'package:suoke_life/presentation/tcm/widgets/tcm_result_card.dart';
import 'package:suoke_life/presentation/tcm/widgets/record_audio_button.dart';
import 'package:suoke_life/domain/entities/tcm/tcm_diagnosis_result.dart';

@RoutePage()
class TcmDiagnosisPage extends ConsumerStatefulWidget {
  const TcmDiagnosisPage({Key? key}) : super(key: key);

  @override
  ConsumerState<TcmDiagnosisPage> createState() => _TcmDiagnosisPageState();
}

class _TcmDiagnosisPageState extends ConsumerState<TcmDiagnosisPage> {
  final _record = Record();
  String? _tongueImagePath;
  String? _faceImagePath;
  String? _audioPath;
  bool _isRecording = false;
  final TextEditingController _descriptionController = TextEditingController();
  
  @override
  void dispose() {
    _record.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source, bool isTongue) async {
    try {
      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(
        source: source, 
        imageQuality: 80,
        maxWidth: 1000,
      );
      
      if (pickedFile != null) {
        setState(() {
          if (isTongue) {
            _tongueImagePath = pickedFile.path;
          } else {
            _faceImagePath = pickedFile.path;
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('图片选取失败: $e')),
      );
    }
  }

  Future<void> _startRecording() async {
    try {
      if (await _record.hasPermission()) {
        final tempDir = await getTemporaryDirectory();
        final path = '${tempDir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.m4a';
        
        await _record.start(
          path: path,
          encoder: AudioEncoder.aacLc,
          bitRate: 128000,
          samplingRate: 44100,
        );
        
        setState(() {
          _audioPath = path;
          _isRecording = true;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('录音失败: $e')),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      final path = await _record.stop();
      setState(() {
        _isRecording = false;
        if (path != null) {
          _audioPath = path;
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('停止录音失败: $e')),
      );
    }
  }

  Future<void> _submitDiagnosis() async {
    if (_tongueImagePath == null && _faceImagePath == null && _audioPath == null && _descriptionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请至少提供一种诊断数据（舌诊图像、面诊图像、语音或文字描述）')),
      );
      return;
    }
    
    try {
      String? tongueBase64;
      String? faceBase64;
      String? audioBase64;
      
      if (_tongueImagePath != null) {
        final bytes = await File(_tongueImagePath!).readAsBytes();
        tongueBase64 = base64Encode(bytes);
      }
      
      if (_faceImagePath != null) {
        final bytes = await File(_faceImagePath!).readAsBytes();
        faceBase64 = base64Encode(bytes);
      }
      
      if (_audioPath != null) {
        final bytes = await File(_audioPath!).readAsBytes();
        audioBase64 = base64Encode(bytes);
      }
      
      final description = _descriptionController.text;
      
      await ref.read(tcmDiagnosisControllerProvider.notifier).submitDiagnosis(
        tongueImage: tongueBase64,
        faceImage: faceBase64,
        audioData: audioBase64,
        description: description,
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('诊断提交失败: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final diagnosisState = ref.watch(tcmDiagnosisControllerProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('中医多模态诊断'),
        backgroundColor: AppColors.SUOKE_GREEN,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AnimatedGradientCard(
                colors: const [
                  Color(0xFF35BB78), // 索克绿
                  Color(0xFF2DA160),
                  Color(0xFF35BB78),
                ],
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '中医多模态智能诊断',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        '通过舌诊、面诊和声音分析，结合中医理论进行辨证分析。',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildImageUploadButton(
                            icon: Icons.camera_alt,
                            label: '舌诊拍照',
                            onTap: () => _pickImage(ImageSource.camera, true),
                          ),
                          _buildImageUploadButton(
                            icon: Icons.face,
                            label: '面诊拍照',
                            onTap: () => _pickImage(ImageSource.camera, false),
                          ),
                          RecordAudioButton(
                            isRecording: _isRecording,
                            onStartRecording: _startRecording,
                            onStopRecording: _stopRecording,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              _buildInputSection(),
              const SizedBox(height: 16),
              _buildPreviewSection(),
              const SizedBox(height: 16),
              AnimatedPressButton(
                onPressed: _submitDiagnosis,
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                  child: Text(
                    diagnosisState.isLoading ? '诊断中...' : '提交诊断',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                color: AppColors.SUOKE_GREEN,
                disabledColor: AppColors.SUOKE_GREEN.withAlpha(150),
                isDisabled: diagnosisState.isLoading,
              ),
              const SizedBox(height: 24),
              if (diagnosisState.isLoading)
                const Center(child: CircularProgressIndicator())
              else if (diagnosisState.hasError)
                _buildErrorWidget(diagnosisState.error.toString())
              else if (diagnosisState.diagnosis != null)
                TcmResultCard(diagnosis: diagnosisState.diagnosis!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageUploadButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Column(
      children: [
        Container(
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(50),
            borderRadius: BorderRadius.circular(12),
          ),
          child: IconButton(
            icon: Icon(icon, color: Colors.white),
            onPressed: onTap,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildInputSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '症状描述',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _descriptionController,
          decoration: const InputDecoration(
            hintText: '请描述您的症状、感受或健康状况...',
            border: OutlineInputBorder(),
            filled: true,
            fillColor: Colors.white,
          ),
          maxLines: 3,
        ),
      ],
    );
  }

  Widget _buildPreviewSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '上传内容预览',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.withAlpha(20),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPreviewItem(
                title: '舌诊图像',
                value: _tongueImagePath != null ? '已上传' : '未上传',
                imagePath: _tongueImagePath,
              ),
              const Divider(),
              _buildPreviewItem(
                title: '面诊图像',
                value: _faceImagePath != null ? '已上传' : '未上传',
                imagePath: _faceImagePath,
              ),
              const Divider(),
              _buildPreviewItem(
                title: '语音描述',
                value: _audioPath != null ? '已录制' : '未录制',
              ),
              const Divider(),
              _buildPreviewItem(
                title: '文字描述',
                value: _descriptionController.text.isNotEmpty ? '已填写' : '未填写',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPreviewItem({
    required String title,
    required String value,
    String? imagePath,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(value),
              ],
            ),
          ),
          if (imagePath != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.file(
                File(imagePath),
                width: 60,
                height: 60,
                fit: BoxFit.cover,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildErrorWidget(String error) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.error_outline, color: Colors.red),
              SizedBox(width: 8),
              Text(
                '诊断失败',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(error),
        ],
      ),
    );
  }
}