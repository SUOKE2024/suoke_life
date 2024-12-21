import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 输入框组件
class AppInput extends StatelessWidget {
  final TextEditingController? controller;
  final String? initialValue;
  final String? label;
  final String? hint;
  final String? helper;
  final String? error;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final bool obscureText;
  final bool readOnly;
  final bool enabled;
  final int? maxLength;
  final int? maxLines;
  final List<TextInputFormatter>? inputFormatters;
  final ValueChanged<String>? onChanged;
  final VoidCallback? onEditingComplete;
  final ValueChanged<String>? onSubmitted;
  final GestureTapCallback? onTap;
  final Widget? prefix;
  final Widget? suffix;
  final EdgeInsets? contentPadding;
  final InputBorder? border;
  final double? borderRadius;
  final Color? fillColor;
  final bool? filled;
  final FocusNode? focusNode;
  final TextStyle? style;
  final TextAlign textAlign;
  final TextAlignVertical? textAlignVertical;
  final bool autofocus;
  final bool showCursor;
  final String? counterText;
  final bool expands;
  
  const AppInput({
    super.key,
    this.controller,
    this.initialValue,
    this.label,
    this.hint,
    this.helper,
    this.error,
    this.keyboardType,
    this.textInputAction,
    this.obscureText = false,
    this.readOnly = false,
    this.enabled = true,
    this.maxLength,
    this.maxLines = 1,
    this.inputFormatters,
    this.onChanged,
    this.onEditingComplete,
    this.onSubmitted,
    this.onTap,
    this.prefix,
    this.suffix,
    this.contentPadding,
    this.border,
    this.borderRadius,
    this.fillColor,
    this.filled,
    this.focusNode,
    this.style,
    this.textAlign = TextAlign.start,
    this.textAlignVertical,
    this.autofocus = false,
    this.showCursor = true,
    this.counterText,
    this.expands = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      obscureText: obscureText,
      readOnly: readOnly,
      enabled: enabled,
      maxLength: maxLength,
      maxLines: maxLines,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      onEditingComplete: onEditingComplete,
      onSubmitted: onSubmitted,
      onTap: onTap,
      focusNode: focusNode,
      style: style,
      textAlign: textAlign,
      textAlignVertical: textAlignVertical,
      autofocus: autofocus,
      showCursor: showCursor,
      expands: expands,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        helperText: helper,
        errorText: error,
        prefixIcon: prefix,
        suffixIcon: suffix,
        contentPadding: contentPadding,
        counterText: counterText,
        border: border ?? OutlineInputBorder(
          borderRadius: BorderRadius.circular(borderRadius ?? 4),
        ),
        fillColor: fillColor,
        filled: filled,
      ),
    );
  }
} 