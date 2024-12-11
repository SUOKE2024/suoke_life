import 'package:flutter/material.dart';
import '../../services/biometric_analysis_service.dart';

class BiometricFeedbackWidget extends StatelessWidget {
  final Stream<BiometricAnalysisResult> biometricStream;

  const BiometricFeedbackWidget({
    Key? key,
    required this.biometricStream,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
          ),
        ),
      ),
      child: StreamBuilder<BiometricAnalysisResult>(
        stream: biometricStream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(
              child: Text('等待生物特征数据...'),
            );
          }

          final result = snapshot.data!;
          return Row(
            children: [
              _buildIndicator(
                context,
                icon: _getTypeIcon(result.type),
                label: _getTypeLabel(result.type),
                value: result.confidence,
                color: _getConfidenceColor(result.confidence),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildAnalysisDetails(context, result),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildIndicator(
    BuildContext context, {
    required IconData icon,
    required String label,
    required double value,
    required Color color,
  }) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, color: color),
        const SizedBox(height: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildAnalysisDetails(BuildContext context, BiometricAnalysisResult result) {
    final details = _getAnalysisDetails(result);
    return ListView(
      scrollDirection: Axis.horizontal,
      children: details.entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.only(right: 16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                entry.key,
                style: Theme.of(context).textTheme.bodySmall,
              ),
              Text(
                entry.value,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  IconData _getTypeIcon(BiometricType type) {
    switch (type) {
      case BiometricType.face:
        return Icons.face;
      case BiometricType.voice:
        return Icons.mic;
      case BiometricType.emotion:
        return Icons.emoji_emotions;
      default:
        return Icons.data_usage;
    }
  }

  String _getTypeLabel(BiometricType type) {
    switch (type) {
      case BiometricType.face:
        return '面部';
      case BiometricType.voice:
        return '语音';
      case BiometricType.emotion:
        return '情绪';
      default:
        return '未知';
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

  Map<String, String> _getAnalysisDetails(BiometricAnalysisResult result) {
    final details = <String, String>{};
    
    switch (result.type) {
      case BiometricType.face:
        final features = result.metadata?['features'] as Map<String, dynamic>?;
        if (features != null) {
          details['注意力'] = '${(features['attention'] * 100).toStringAsFixed(1)}%';
          details['情绪'] = features['emotion'] ?? '未知';
        }
        break;
        
      case BiometricType.voice:
        final features = result.metadata?['features'] as Map<String, dynamic>?;
        if (features != null) {
          details['音调'] = features['pitch'] ?? '未知';
          details['语速'] = features['speed'] ?? '未知';
          details['音量'] = features['volume'] ?? '未知';
        }
        break;
        
      case BiometricType.emotion:
        final emotions = result.metadata?['emotions'] as Map<String, dynamic>?;
        if (emotions != null) {
          details['主要情绪'] = emotions['primary'] ?? '未知';
          details['强度'] = '${(emotions['intensity'] * 100).toStringAsFixed(1)}%';
        }
        break;
    }
    
    return details;
  }
} 