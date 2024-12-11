import 'package:flutter/material.dart';
import 'dart:async';

class PhoneInput extends StatefulWidget {
  final TextEditingController controller;
  final VoidCallback onSendCode;

  const PhoneInput({
    super.key,
    required this.controller,
    required this.onSendCode,
  });

  @override
  State<PhoneInput> createState() => _PhoneInputState();
}

class _PhoneInputState extends State<PhoneInput> {
  Timer? _timer;
  int _countdown = 0;

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startCountdown() {
    setState(() => _countdown = 60);
    _timer = Timer.periodic(
      const Duration(seconds: 1),
      (timer) {
        if (_countdown == 0) {
          timer.cancel();
        } else {
          setState(() => _countdown--);
        }
      },
    );
  }

  void _handleSendCode() {
    if (_countdown > 0) return;

    final phone = widget.controller.text;
    if (phone.length != 11) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入正确的手机号')),
      );
      return;
    }

    widget.onSendCode();
    _startCountdown();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: widget.controller,
      decoration: InputDecoration(
        labelText: '手机号',
        border: const OutlineInputBorder(),
        suffixIcon: TextButton(
          onPressed: _countdown > 0 ? null : _handleSendCode,
          child: Text(
            _countdown > 0 ? '${_countdown}s' : '发送验证码',
            style: TextStyle(
              color: _countdown > 0
                  ? Colors.grey
                  : Theme.of(context).colorScheme.primary,
            ),
          ),
        ),
      ),
      keyboardType: TextInputType.phone,
      maxLength: 11,
    );
  }
} 