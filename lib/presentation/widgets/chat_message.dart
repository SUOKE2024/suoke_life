import 'package:flutter/material.dart';
import '../../models/message.dart';
import 'chat_bubble.dart';

class ChatMessage extends StatelessWidget {
  final Message message;
  final bool showBiometricData;
  final VoidCallback? onRetry;

  const ChatMessage({
    Key? key,
    required this.message,
    this.showBiometricData = false,
    this.onRetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment:
            message.role == 'user' ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (message.role != 'user') _buildAvatar(context),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment: message.role == 'user'
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                ChatBubble(
                  message: message,
                  onRetry: onRetry,
                ),
                if (showBiometricData && message.metadata != null)
                  _buildBiometricData(context),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (message.role == 'user') _buildAvatar(context),
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context) {
    return CircleAvatar(
      radius: 16,
      backgroundColor: message.role == 'user'
          ? Theme.of(context).colorScheme.primary
          : Theme.of(context).colorScheme.secondary,
      child: Icon(
        message.role == 'user' ? Icons.person : Icons.smart_toy,
        size: 20,
        color: Theme.of(context).colorScheme.onPrimary,
      ),
    );
  }

  Widget _buildBiometricData(BuildContext context) {
    final biometricData = <String, dynamic>{};
    
    // 收集所有生物特征数据
    message.metadata?.forEach((key, value) {
      if (key.startsWith('biometric_')) {
        biometricData[key.substring(10)] = value;
      }
    });
    
    if (biometricData.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Card(
        color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.5),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: biometricData.entries.map((entry) {
              return _buildBiometricEntry(context, entry.key, entry.value);
            }).toList(),
          ),
        ),
      ),
    );
  }

  Widget _buildBiometricEntry(
    BuildContext context,
    String type,
    Map<String, dynamic> data,
  ) {
    final icon = _getBiometricIcon(type);
    final label = _getBiometricLabel(type);
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(width: 8),
        if (data['confidence'] != null)
          _buildConfidenceIndicator(context, data['confidence']),
      ],
    );
  }

  Widget _buildConfidenceIndicator(BuildContext context, double confidence) {
    return Container(
      width: 40,
      height: 4,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(2),
        color: Theme.of(context).colorScheme.surfaceVariant,
      ),
      child: FractionallySizedBox(
        alignment: Alignment.centerLeft,
        widthFactor: confidence,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(2),
            color: _getConfidenceColor(confidence),
          ),
        ),
      ),
    );
  }

  IconData _getBiometricIcon(String type) {
    switch (type) {
      case 'face':
        return Icons.face;
      case 'voice':
        return Icons.mic;
      case 'emotion':
        return Icons.emoji_emotions;
      default:
        return Icons.data_usage;
    }
  }

  String _getBiometricLabel(String type) {
    switch (type) {
      case 'face':
        return '面部分析';
      case 'voice':
        return '语音分析';
      case 'emotion':
        return '情绪分析';
      default:
        return '数据分析';
    }
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) {
      return Colors.green;
    } else if (confidence >= 0.6) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
} 