/// 表单组件
class AppForm extends StatefulWidget {
  final List<FormField> fields;
  final VoidCallback? onSubmit;
  final String? submitText;
  final bool showDivider;
  final EdgeInsets? padding;
  final bool autovalidate;
  final GlobalKey<FormState>? formKey;

  const AppForm({
    super.key,
    required this.fields,
    this.onSubmit,
    this.submitText,
    this.showDivider = true,
    this.padding,
    this.autovalidate = false,
    this.formKey,
  });

  @override
  State<AppForm> createState() => _AppFormState();
}

class _AppFormState extends State<AppForm> {
  late final GlobalKey<FormState> _formKey;

  @override
  void initState() {
    super.initState();
    _formKey = widget.formKey ?? GlobalKey<FormState>();
  }

  void _handleSubmit() {
    if (_formKey.currentState?.validate() ?? false) {
      _formKey.currentState?.save();
      widget.onSubmit?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      autovalidateMode: widget.autovalidate
          ? AutovalidateMode.onUserInteraction
          : AutovalidateMode.disabled,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            padding: widget.padding,
            itemCount: widget.fields.length,
            separatorBuilder: (_, __) => widget.showDivider
                ? const Divider(height: 1)
                : const SizedBox(height: 16),
            itemBuilder: (context, index) {
              final field = widget.fields[index];
              return _buildFormField(field);
            },
          ),
          if (widget.onSubmit != null) ...[
            const SizedBox(height: 24),
            AppButton(
              text: widget.submitText ?? '提交',
              onPressed: _handleSubmit,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFormField(FormField field) {
    switch (field.type) {
      case FormFieldType.text:
        return TextFormField(
          controller: field.controller,
          decoration: InputDecoration(
            labelText: field.label,
            hintText: field.hint,
            prefixIcon: field.prefix,
            suffixIcon: field.suffix,
          ),
          validator: field.validator,
          onSaved: field.onSaved,
          enabled: field.enabled,
          obscureText: field.obscureText ?? false,
          maxLines: field.maxLines,
          keyboardType: field.keyboardType,
        );
      case FormFieldType.select:
        return DropdownButtonFormField<dynamic>(
          value: field.value,
          items: field.items?.map((item) {
            return DropdownMenuItem(
              value: item.value,
              child: Text(item.label),
            );
          }).toList(),
          decoration: InputDecoration(
            labelText: field.label,
            prefixIcon: field.prefix,
            suffixIcon: field.suffix,
          ),
          onChanged: field.onChanged,
          validator: field.validator,
          onSaved: field.onSaved,
        );
      case FormFieldType.checkbox:
        return CheckboxListTile(
          value: field.value ?? false,
          title: Text(field.label ?? ''),
          subtitle: field.hint != null ? Text(field.hint!) : null,
          onChanged: (value) => field.onChanged?.call(value),
        );
      case FormFieldType.switch_:
        return SwitchListTile(
          value: field.value ?? false,
          title: Text(field.label ?? ''),
          subtitle: field.hint != null ? Text(field.hint!) : null,
          onChanged: (value) => field.onChanged?.call(value),
        );
      case FormFieldType.custom:
        return field.builder?.call(context) ?? const SizedBox();
    }
  }
}

/// 表单字段类型
enum FormFieldType {
  text,
  select,
  checkbox,
  switch_,
  custom,
}

/// 表单字段
class FormField {
  final FormFieldType type;
  final String? label;
  final String? hint;
  final Widget? prefix;
  final Widget? suffix;
  final TextEditingController? controller;
  final dynamic value;
  final List<FormItem>? items;
  final ValueChanged? onChanged;
  final FormFieldValidator? validator;
  final FormFieldSetter? onSaved;
  final bool? enabled;
  final bool? obscureText;
  final int? maxLines;
  final TextInputType? keyboardType;
  final Widget Function(BuildContext)? builder;

  const FormField({
    required this.type,
    this.label,
    this.hint,
    this.prefix,
    this.suffix,
    this.controller,
    this.value,
    this.items,
    this.onChanged,
    this.validator,
    this.onSaved,
    this.enabled,
    this.obscureText,
    this.maxLines,
    this.keyboardType,
    this.builder,
  });
}

/// 表单选项
class FormItem {
  final String label;
  final dynamic value;

  const FormItem({
    required this.label,
    required this.value,
  });
} 