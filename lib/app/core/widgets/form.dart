import 'package:flutter/material.dart';

/// 表单组件
class AppForm extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final List<Widget> children;
  final EdgeInsets? padding;
  final bool autovalidateMode;
  final VoidCallback? onSubmit;
  
  const AppForm({
    super.key,
    required this.formKey,
    required this.children,
    this.padding,
    this.autovalidateMode = false,
    this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      autovalidateMode: autovalidateMode 
          ? AutovalidateMode.onUserInteraction
          : AutovalidateMode.disabled,
      child: Padding(
        padding: padding ?? const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ...children,
            if (onSubmit != null) ...[
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  if (formKey.currentState?.validate() ?? false) {
                    formKey.currentState?.save();
                    onSubmit?.call();
                  }
                },
                child: const Text('提交'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// 表单字段组件
class AppFormField extends StatelessWidget {
  final String? label;
  final String? hint;
  final String? initialValue;
  final TextInputType? keyboardType;
  final bool obscureText;
  final int? maxLines;
  final String? Function(String?)? validator;
  final void Function(String?)? onSaved;
  final void Function(String)? onChanged;
  final Widget? prefix;
  final Widget? suffix;
  
  const AppFormField({
    super.key,
    this.label,
    this.hint,
    this.initialValue,
    this.keyboardType,
    this.obscureText = false,
    this.maxLines = 1,
    this.validator,
    this.onSaved,
    this.onChanged,
    this.prefix,
    this.suffix,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      initialValue: initialValue,
      keyboardType: keyboardType,
      obscureText: obscureText,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: prefix,
        suffixIcon: suffix,
      ),
      validator: validator,
      onSaved: onSaved,
      onChanged: onChanged,
    );
  }
} 