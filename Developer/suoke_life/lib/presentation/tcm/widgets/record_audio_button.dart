import 'package:flutter/material.dart';
import 'package:suoke_life/core/constants/app_colors.dart';

class RecordAudioButton extends StatelessWidget {
  final bool isRecording;
  final VoidCallback onStartRecording;
  final VoidCallback onStopRecording;

  const RecordAudioButton({
    Key? key,
    required this.isRecording,
    required this.onStartRecording,
    required this.onStopRecording,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(50),
            borderRadius: BorderRadius.circular(12),
          ),
          child: IconButton(
            icon: Icon(
              isRecording ? Icons.stop : Icons.mic,
              color: isRecording ? Colors.red : Colors.white,
            ),
            onPressed: isRecording ? onStopRecording : onStartRecording,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          isRecording ? '停止录音' : '声音录制',
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white,
          ),
        ),
        if (isRecording)
          _buildRecordingIndicator(),
      ],
    );
  }

  Widget _buildRecordingIndicator() {
    return Container(
      margin: const EdgeInsets.only(top: 4),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.red,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 4),
          const Text(
            'REC',
            style: TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}