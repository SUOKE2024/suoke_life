import 'package:flutter/material.dart';

/// 日历组件
class AppCalendar extends StatelessWidget {
  final DateTime? selectedDate;
  final ValueChanged<DateTime>? onDateSelected;
  final DateTime? firstDate;
  final DateTime? lastDate;
  final DateTime? currentDate;
  final Color? selectedDateColor;
  final Color? todayColor;
  final TextStyle? dayTextStyle;
  final TextStyle? weekdayTextStyle;
  final TextStyle? headerTextStyle;
  final bool showHeader;
  final bool showWeekdays;
  final EdgeInsets? padding;
  
  const AppCalendar({
    super.key,
    this.selectedDate,
    this.onDateSelected,
    this.firstDate,
    this.lastDate,
    this.currentDate,
    this.selectedDateColor,
    this.todayColor,
    this.dayTextStyle,
    this.weekdayTextStyle,
    this.headerTextStyle,
    this.showHeader = true,
    this.showWeekdays = true,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSelectedColor = selectedDateColor ?? theme.primaryColor;
    final defaultTodayColor = todayColor ?? theme.primaryColor.withOpacity(0.5);
    
    return CalendarDatePicker(
      initialDate: selectedDate ?? DateTime.now(),
      firstDate: firstDate ?? DateTime(1900),
      lastDate: lastDate ?? DateTime(2100),
      currentDate: currentDate,
      onDateChanged: onDateSelected ?? (_) {},
      selectableDayPredicate: (date) {
        if (firstDate != null && date.isBefore(firstDate!)) {
          return false;
        }
        if (lastDate != null && date.isAfter(lastDate!)) {
          return false;
        }
        return true;
      },
      selectedDayDecoration: BoxDecoration(
        color: defaultSelectedColor,
        shape: BoxShape.circle,
      ),
      todayDecoration: BoxDecoration(
        color: defaultTodayColor,
        shape: BoxShape.circle,
      ),
    );
  }
}

/// 日期范围选择组件
class AppDateRangePicker extends StatelessWidget {
  final DateTimeRange? selectedRange;
  final ValueChanged<DateTimeRange>? onRangeSelected;
  final DateTime? firstDate;
  final DateTime? lastDate;
  final DateTime? currentDate;
  final Color? selectedDateColor;
  final Color? todayColor;
  final TextStyle? dayTextStyle;
  final TextStyle? weekdayTextStyle;
  final TextStyle? headerTextStyle;
  final bool showHeader;
  final bool showWeekdays;
  final EdgeInsets? padding;
  
  const AppDateRangePicker({
    super.key,
    this.selectedRange,
    this.onRangeSelected,
    this.firstDate,
    this.lastDate,
    this.currentDate,
    this.selectedDateColor,
    this.todayColor,
    this.dayTextStyle,
    this.weekdayTextStyle,
    this.headerTextStyle,
    this.showHeader = true,
    this.showWeekdays = true,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSelectedColor = selectedDateColor ?? theme.primaryColor;
    final defaultTodayColor = todayColor ?? theme.primaryColor.withOpacity(0.5);
    
    return CalendarDatePicker2(
      config: CalendarDatePicker2Config(
        calendarType: CalendarDatePicker2Type.range,
        selectedDayHighlightColor: defaultSelectedColor,
        dayTextStyle: dayTextStyle,
        weekdayLabelTextStyle: weekdayTextStyle,
        controlsTextStyle: headerTextStyle,
        firstDate: firstDate,
        lastDate: lastDate,
        currentDate: currentDate,
        selectedDayDecoration: BoxDecoration(
          color: defaultSelectedColor,
          shape: BoxShape.circle,
        ),
        todayDecoration: BoxDecoration(
          color: defaultTodayColor,
          shape: BoxShape.circle,
        ),
      ),
      value: selectedRange != null ? [selectedRange!.start, selectedRange!.end] : null,
      onValueChanged: (dates) {
        if (dates.length == 2 && onRangeSelected != null) {
          onRangeSelected!(DateTimeRange(
            start: dates[0]!,
            end: dates[1]!,
          ));
        }
      },
    );
  }
} 