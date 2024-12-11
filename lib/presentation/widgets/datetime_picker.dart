import 'package:flutter/material.dart';

class CustomDateTimePicker extends StatelessWidget {
  final DateTime initialDateTime;
  final ValueChanged<DateTime> onChanged;
  final DateTime? minDateTime;
  final DateTime? maxDateTime;

  const CustomDateTimePicker({
    Key? key,
    required this.initialDateTime,
    required this.onChanged,
    this.minDateTime,
    this.maxDateTime,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '预约时间',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () => _showDateTimePicker(context),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(
                color: Theme.of(context).dividerColor,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.calendar_today),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _formatDate(initialDateTime),
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatTime(initialDateTime),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
                const Spacer(),
                const Icon(Icons.arrow_forward_ios, size: 16),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '提示：请选择合适的会诊时间，AI助手会为您智能匹配专家的空闲时段。',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
      ],
    );
  }

  Future<void> _showDateTimePicker(BuildContext context) async {
    final now = DateTime.now();
    final min = minDateTime ?? now.add(const Duration(hours: 1));
    final max = maxDateTime ?? now.add(const Duration(days: 30));

    final date = await showDatePicker(
      context: context,
      initialDate: initialDateTime,
      firstDate: min,
      lastDate: max,
      helpText: '选择会诊日期',
      cancelText: '取消',
      confirmText: '确定',
      currentDate: now,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme.copyWith(
              primary: Theme.of(context).primaryColor,
            ),
          ),
          child: child!,
        );
      },
    );

    if (date != null && context.mounted) {
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.fromDateTime(initialDateTime),
        helpText: '选择会诊时间',
        cancelText: '取消',
        confirmText: '确定',
        builder: (context, child) {
          return Theme(
            data: Theme.of(context).copyWith(
              colorScheme: Theme.of(context).colorScheme.copyWith(
                primary: Theme.of(context).primaryColor,
              ),
            ),
            child: child!,
          );
        },
      );

      if (time != null) {
        final dateTime = DateTime(
          date.year,
          date.month,
          date.day,
          time.hour,
          time.minute,
        );
        onChanged(dateTime);
      }
    }
  }

  String _formatDate(DateTime dateTime) {
    return '${dateTime.year}年${dateTime.month}月${dateTime.day}日';
  }

  String _formatTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:'
           '${dateTime.minute.toString().padLeft(2, '0')}';
  }
} 