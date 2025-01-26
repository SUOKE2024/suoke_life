import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SyncProgressIndicator extends StatelessWidget {
  final double progress;
  final String? currentItem;
  final Color? color;
  final double strokeWidth;
  final double? width;
  final double? height;

  const SyncProgressIndicator({
    Key? key,
    required this.progress,
    this.currentItem,
    this.color,
    this.strokeWidth = 2.0,
    this.width,
    this.height,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: width,
      height: height,
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 48,
                height: 48,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: strokeWidth,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    color ?? theme.primaryColor,
                  ),
                  backgroundColor:
                      (color ?? theme.primaryColor).withOpacity(0.2),
                ),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: color ?? theme.primaryColor,
                ),
              ),
            ],
          ),
          if (currentItem != null) ...[
            const SizedBox(height: 8),
            Text(
              currentItem!,
              style: TextStyle(
                fontSize: 14,
                color: theme.textTheme.bodyMedium?.color?.withOpacity(0.6),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
