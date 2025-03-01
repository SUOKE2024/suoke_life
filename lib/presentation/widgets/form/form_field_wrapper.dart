import 'package:flutter/material.dart';

/// 表单字段包装器
/// 用于统一表单字段的样式和布局
class FormFieldWrapper extends StatelessWidget {
  final String label;
  final Widget child;
  final String? description;
  final Widget? suffix;

  const FormFieldWrapper({
    Key? key,
    required this.label,
    required this.child,
    this.description,
    this.suffix,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标签和可选后缀
        Row(
          children: [
            Text(
              label,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const Spacer(),
            if (suffix != null) suffix!,
          ],
        ),
        
        const SizedBox(height: 8),
        
        // 表单字段
        Theme(
          data: Theme.of(context).copyWith(
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: theme.brightness == Brightness.dark
                  ? Colors.grey.shade800
                  : Colors.grey.shade100,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.primaryColor,
                  width: 1.5,
                ),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.error,
                  width: 1.5,
                ),
              ),
              focusedErrorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.error,
                  width: 1.5,
                ),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 14,
              ),
              errorStyle: TextStyle(
                color: theme.colorScheme.error,
                fontSize: 12,
              ),
            ),
          ),
          child: child,
        ),
        
        // 描述信息
        if (description != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              description!,
              style: theme.textTheme.bodySmall,
            ),
          ),
      ],
    );
  }
} 