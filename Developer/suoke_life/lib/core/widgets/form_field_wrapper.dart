import 'package:flutter/material.dart';

/// 表单字段包装器
/// 用于统一表单字段的样式和布局
class FormFieldWrapper extends StatelessWidget {
  const FormFieldWrapper({
    Key? key,
    required this.child,
    required this.label,
    this.hint,
    this.isRequired = false,
    this.errorText,
  }) : super(key: key);

  /// 子部件，通常是TextFormField或其派生类
  final Widget child;
  
  /// 字段标签
  final String label;
  
  /// 提示文字（可选）
  final String? hint;
  
  /// 是否必填
  final bool isRequired;
  
  /// 错误文本（可选）
  final String? errorText;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 标签行
        Row(
          children: [
            // 标签文本
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.black87,
              ),
            ),
            
            // 必填标记
            if (isRequired) ...[
              const SizedBox(width: 4),
              const Text(
                '*',
                style: TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ],
        ),
        
        // 间距
        const SizedBox(height: 8),
        
        // 表单字段
        child,
        
        // 提示或错误信息
        if (errorText != null || hint != null) ...[
          const SizedBox(height: 6),
          Text(
            errorText ?? hint ?? '',
            style: TextStyle(
              fontSize: 12,
              fontStyle: errorText != null ? FontStyle.normal : FontStyle.italic,
              color: errorText != null ? Colors.red : Colors.black54,
            ),
          ),
        ],
      ],
    );
  }
} 