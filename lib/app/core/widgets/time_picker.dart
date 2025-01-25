/// 时间选择器组件
class AppTimePicker extends StatelessWidget {
  final TimeOfDay? value;
  final ValueChanged<TimeOfDay>? onChanged;
  final String? label;
  final String? hint;
  final bool enabled;
  final InputDecoration? decoration;
  final String? format;
  final String? cancelText;
  final String? confirmText;
  final String? helpText;
  final String? hourLabelText;
  final String? minuteLabelText;
  final Widget? prefix;
  final Widget? suffix;
  final TimePickerEntryMode initialEntryMode;
  final bool use24HourFormat;

  const AppTimePicker({
    super.key,
    this.value,
    this.onChanged,
    this.label,
    this.hint,
    this.enabled = true,
    this.decoration,
    this.format,
    this.cancelText,
    this.confirmText,
    this.helpText,
    this.hourLabelText,
    this.minuteLabelText,
    this.prefix,
    this.suffix,
    this.initialEntryMode = TimePickerEntryMode.dial,
    this.use24HourFormat = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final localizations = MaterialLocalizations.of(context);

    String formatTime(TimeOfDay? time) {
      if (time == null) return '';
      return localizations.formatTimeOfDay(
        time,
        alwaysUse24HourFormat: use24HourFormat,
      );
    }

    Future<void> showPicker() async {
      final time = await showTimePicker(
        context: context,
        initialTime: value ?? TimeOfDay.now(),
        cancelText: cancelText,
        confirmText: confirmText,
        helpText: helpText,
        hourLabelText: hourLabelText,
        minuteLabelText: minuteLabelText,
        initialEntryMode: initialEntryMode,
        builder: (context, child) {
          return MediaQuery(
            data: MediaQuery.of(context).copyWith(
              alwaysUse24HourFormat: use24HourFormat,
            ),
            child: child!,
          );
        },
      );

      if (time != null) {
        onChanged?.call(time);
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
                      const Icon(Icons.access_time),
                  border: const OutlineInputBorder(),
                ),
            child: Text(
              formatTime(value),
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