/// 日期选择器组件
class AppDatePicker extends StatelessWidget {
  final DateTime? value;
  final DateTime? firstDate;
  final DateTime? lastDate;
  final ValueChanged<DateTime>? onChanged;
  final String? label;
  final String? hint;
  final bool enabled;
  final InputDecoration? decoration;
  final String? format;
  final String? cancelText;
  final String? confirmText;
  final String? errorFormatText;
  final String? errorInvalidText;
  final String? fieldHintText;
  final String? fieldLabelText;
  final String? helpText;
  final DatePickerMode initialDatePickerMode;
  final DatePickerEntryMode initialEntryMode;
  final SelectableDayPredicate? selectableDayPredicate;
  final Widget? prefix;
  final Widget? suffix;

  const AppDatePicker({
    super.key,
    this.value,
    this.firstDate,
    this.lastDate,
    this.onChanged,
    this.label,
    this.hint,
    this.enabled = true,
    this.decoration,
    this.format,
    this.cancelText,
    this.confirmText,
    this.errorFormatText,
    this.errorInvalidText,
    this.fieldHintText,
    this.fieldLabelText,
    this.helpText,
    this.initialDatePickerMode = DatePickerMode.day,
    this.initialEntryMode = DatePickerEntryMode.calendar,
    this.selectableDayPredicate,
    this.prefix,
    this.suffix,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultFirstDate = DateTime(1900);
    final defaultLastDate = DateTime(2100);

    String formatDate(DateTime? date) {
      if (date == null) return '';
      if (format != null) {
        return DateFormat(format).format(date);
      }
      return DateFormat.yMd().format(date);
    }

    Future<void> showPicker() async {
      final date = await showDatePicker(
        context: context,
        initialDate: value ?? DateTime.now(),
        firstDate: firstDate ?? defaultFirstDate,
        lastDate: lastDate ?? defaultLastDate,
        cancelText: cancelText,
        confirmText: confirmText,
        errorFormatText: errorFormatText,
        errorInvalidText: errorInvalidText,
        fieldHintText: fieldHintText,
        fieldLabelText: fieldLabelText,
        helpText: helpText,
        initialDatePickerMode: initialDatePickerMode,
        initialEntryMode: initialEntryMode,
        selectableDayPredicate: selectableDayPredicate,
      );

      if (date != null) {
        onChanged?.call(date);
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              label!,
              style: theme.textTheme.bodyMedium,
            ),
          ),
        InkWell(
          onTap: enabled ? showPicker : null,
          child: InputDecorator(
            decoration: decoration ??
                InputDecoration(
                  hintText: hint,
                  prefixIcon: prefix,
                  suffixIcon: suffix ??
                      const Icon(Icons.calendar_today_outlined),
                  border: const OutlineInputBorder(),
                ),
            child: Text(
              formatDate(value),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: value == null ? theme.hintColor : null,
              ),
            ),
          ),
        ),
      ],
    );
  }
} 