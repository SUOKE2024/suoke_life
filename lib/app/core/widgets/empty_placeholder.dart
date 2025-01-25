import 'package:flutter/material.dart';

class EmptyPlaceholder extends StatelessWidget {
  final String message;
  final String? secondaryMessage;
  final Widget? action;

  const EmptyPlaceholder({
    Key? key,
    required this.message,
    this.secondaryMessage,
    this.action,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.inbox_outlined,
              size: 64,
              color: theme.disabledColor,
            ),
            if (message != null) ...[
              SizedBox(height: 16),
              Text(
                message!,
                style: TextStyle(
                  fontSize: 16,
                  color: theme.textTheme.bodyMedium?.color?.withOpacity(0.6),
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (action != null) ...[
              SizedBox(height: 24),
              action!,
            ],
          ],
        ),
      ),
    );
  }
} 