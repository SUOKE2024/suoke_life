import 'package:flutter/material.dart';

class SymptomInput extends StatelessWidget {
  final String initialValue;
  final ValueChanged<String> onChanged;

  const SymptomInput({
    Key? key,
    required this.initialValue,
    required this.onChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '症状描述',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: initialValue,
          onChanged: onChanged,
          maxLines: 5,
          maxLength: 1000,
          decoration: InputDecoration(
            hintText: '请详细描述您的症状、病史和需求...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            filled: true,
            fillColor: Theme.of(context).cardColor,
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '请输入症状描述';
            }
            if (value.trim().length < 10) {
              return '请至少输入10个字的描述';
            }
            return null;
          },
          textInputAction: TextInputAction.newline,
          keyboardType: TextInputType.multiline,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 8),
        Text(
          '提示：描述越详细，AI助手越能准确分析并安排合适的专家。',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
      ],
    );
  }
} 