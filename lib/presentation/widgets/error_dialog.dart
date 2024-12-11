import 'package:flutter/material.dart';
import '../../services/error_handler_service.dart';

class ErrorDialog extends StatelessWidget {
  final VideoConferenceError error;

  const ErrorDialog({
    Key? key,
    required this.error,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(
            _getIcon(),
            color: _getColor(),
          ),
          const SizedBox(width: 8),
          Text(_getTitle()),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(error.message),
          if (error.originalError != null) ...[
            const SizedBox(height: 8),
            Text(
              '错误详情: ${error.originalError}',
              style: Theme.of(context).textTheme.caption,
            ),
          ],
        ],
      ),
      actions: [
        if (_shouldShowRetryButton())
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: 实现重试逻辑
            },
            child: const Text('重试'),
          ),
        if (_shouldShowSettingsButton())
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: 打开相关设置页面
            },
            child: const Text('设置'),
          ),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('确定'),
        ),
      ],
    );
  }

  IconData _getIcon() {
    switch (error.severity) {
      case ErrorSeverity.critical:
      case ErrorSeverity.high:
        return Icons.error;
      case ErrorSeverity.medium:
        return Icons.warning;
      case ErrorSeverity.low:
        return Icons.info;
      default:
        return Icons.help;
    }
  }

  Color _getColor() {
    switch (error.severity) {
      case ErrorSeverity.critical:
      case ErrorSeverity.high:
        return Colors.red;
      case ErrorSeverity.medium:
        return Colors.orange;
      case ErrorSeverity.low:
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  String _getTitle() {
    switch (error.severity) {
      case ErrorSeverity.critical:
        return '严重错误';
      case ErrorSeverity.high:
        return '错误';
      case ErrorSeverity.medium:
        return '警告';
      case ErrorSeverity.low:
        return '提示';
      default:
        return '未知错误';
    }
  }

  bool _shouldShowRetryButton() {
    return error.code == ErrorHandlerService.networkError ||
           error.code == ErrorHandlerService.cameraInitError;
  }

  bool _shouldShowSettingsButton() {
    return error.code == ErrorHandlerService.permissionError;
  }
} 