import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

class AgreementDialog extends StatefulWidget {
  final VoidCallback onAgree;
  final VoidCallback onDisagree;

  const AgreementDialog({
    super.key,
    required this.onAgree,
    required this.onDisagree,
  });

  @override
  State<AgreementDialog> createState() => _AgreementDialogState();
}

class _AgreementDialogState extends State<AgreementDialog> {
  bool _isChecked = false;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return AlertDialog(
      title: const Text('用户协议和隐私政策'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '欢迎使用索客生活！我们非常重视您的个人信息和隐私保护。为了更好地保障您的权益，在使用我们的服务之前，请您认真阅读完整版',
              style: textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
            RichText(
              text: TextSpan(
                style: textTheme.bodyMedium,
                children: [
                  TextSpan(
                    text: '《用户协议》',
                    style: TextStyle(
                      color: colorScheme.primary,
                      decoration: TextDecoration.underline,
                    ),
                    recognizer: TapGestureRecognizer()
                      ..onTap = () {
                        Navigator.pushNamed(context, '/terms');
                      },
                  ),
                  const TextSpan(text: '和'),
                  TextSpan(
                    text: '《隐私政策》',
                    style: TextStyle(
                      color: colorScheme.primary,
                      decoration: TextDecoration.underline,
                    ),
                    recognizer: TapGestureRecognizer()
                      ..onTap = () {
                        Navigator.pushNamed(context, '/privacy');
                      },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            CheckboxListTile(
              value: _isChecked,
              onChanged: (value) {
                setState(() {
                  _isChecked = value ?? false;
                });
              },
              title: const Text('我已阅读并同意上述协议'),
              controlAffinity: ListTileControlAffinity.leading,
              contentPadding: EdgeInsets.zero,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: widget.onDisagree,
          child: const Text('不同意'),
        ),
        ElevatedButton(
          onPressed: _isChecked ? widget.onAgree : null,
          child: const Text('同意'),
        ),
      ],
    );
  }
} 