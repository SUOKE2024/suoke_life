/// 表单字段组件
class AppFormField extends StatelessWidget {
  final String label;
  final String? hint;
  final String? errorText;
  final TextEditingController? controller;
  final TextInputType? keyboardType;
  final bool obscureText;
  final int? maxLines;
  final int? maxLength;
  final ValueChanged<String>? onChanged;
  final FormFieldValidator<String>? validator;
  final Widget? prefix;
  final Widget? suffix;

  const AppFormField({
    super.key,
    required this.label,
    this.hint,
    this.errorText,
    this.controller,
    this.keyboardType,
    this.obscureText = false,
    this.maxLines = 1,
    this.maxLength,
    this.onChanged,
    this.validator,
    this.prefix,
    this.suffix,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          obscureText: obscureText,
          maxLines: maxLines,
          maxLength: maxLength,
          onChanged: onChanged,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            errorText: errorText,
            prefixIcon: prefix,
            suffixIcon: suffix,
            border: OutlineInputBorder(
              borderRadius: AppStyles.borderRadius,
            ),
          ),
        ),
      ],
    );
  }
} 