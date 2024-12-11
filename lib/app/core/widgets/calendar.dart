/// 日历组件
class AppCalendar extends StatefulWidget {
  final DateTime? initialDate;
  final DateTime? firstDate;
  final DateTime? lastDate;
  final ValueChanged<DateTime>? onDateSelected;
  final bool showWeekDays;
  final bool showHeader;
  final bool showNavigation;
  final Color? selectedColor;
  final Color? todayColor;
  final TextStyle? dayTextStyle;
  final TextStyle? weekDayTextStyle;
  final TextStyle? headerTextStyle;
  final String? locale;
  final List<DateTime>? specialDates;
  final Widget Function(DateTime)? dayBuilder;

  const AppCalendar({
    super.key,
    this.initialDate,
    this.firstDate,
    this.lastDate,
    this.onDateSelected,
    this.showWeekDays = true,
    this.showHeader = true,
    this.showNavigation = true,
    this.selectedColor,
    this.todayColor,
    this.dayTextStyle,
    this.weekDayTextStyle,
    this.headerTextStyle,
    this.locale,
    this.specialDates,
    this.dayBuilder,
  });

  @override
  State<AppCalendar> createState() => _AppCalendarState();
}

class _AppCalendarState extends State<AppCalendar> {
  late DateTime _currentMonth;
  late DateTime _selectedDate;
  late List<DateTime> _days;

  @override
  void initState() {
    super.initState();
    _currentMonth = widget.initialDate ?? DateTime.now();
    _selectedDate = widget.initialDate ?? DateTime.now();
    _generateDays();
  }

  void _generateDays() {
    final firstDayOfMonth = DateTime(_currentMonth.year, _currentMonth.month, 1);
    final lastDayOfMonth = DateTime(_currentMonth.year, _currentMonth.month + 1, 0);
    
    final firstWeekday = firstDayOfMonth.weekday;
    final daysInMonth = lastDayOfMonth.day;
    
    _days = [];
    
    // Add days from previous month
    final previousMonth = DateTime(_currentMonth.year, _currentMonth.month - 1);
    final daysInPreviousMonth = DateTime(_currentMonth.year, _currentMonth.month, 0).day;
    for (var i = firstWeekday - 1; i >= 0; i--) {
      _days.add(DateTime(previousMonth.year, previousMonth.month, daysInPreviousMonth - i));
    }
    
    // Add days from current month
    for (var i = 1; i <= daysInMonth; i++) {
      _days.add(DateTime(_currentMonth.year, _currentMonth.month, i));
    }
    
    // Add days from next month
    final remainingDays = 42 - _days.length; // 6 weeks * 7 days
    for (var i = 1; i <= remainingDays; i++) {
      _days.add(DateTime(_currentMonth.year, _currentMonth.month + 1, i));
    }
  }

  void _onDaySelected(DateTime date) {
    if (widget.firstDate != null && date.isBefore(widget.firstDate!)) return;
    if (widget.lastDate != null && date.isAfter(widget.lastDate!)) return;
    
    setState(() {
      _selectedDate = date;
    });
    widget.onDateSelected?.call(date);
  }

  void _previousMonth() {
    setState(() {
      _currentMonth = DateTime(_currentMonth.year, _currentMonth.month - 1);
      _generateDays();
    });
  }

  void _nextMonth() {
    setState(() {
      _currentMonth = DateTime(_currentMonth.year, _currentMonth.month + 1);
      _generateDays();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultSelectedColor = widget.selectedColor ?? theme.primaryColor;
    final defaultTodayColor = widget.todayColor ?? theme.primaryColor.withOpacity(0.3);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.showHeader)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (widget.showNavigation)
                  IconButton(
                    icon: const Icon(Icons.chevron_left),
                    onPressed: _previousMonth,
                  )
                else
                  const SizedBox(width: 48),
                Text(
                  DateFormat.yMMMM(widget.locale).format(_currentMonth),
                  style: widget.headerTextStyle ?? theme.textTheme.titleMedium,
                ),
                if (widget.showNavigation)
                  IconButton(
                    icon: const Icon(Icons.chevron_right),
                    onPressed: _nextMonth,
                  )
                else
                  const SizedBox(width: 48),
              ],
            ),
          ),
        if (widget.showWeekDays)
          Row(
            children: List.generate(7, (index) {
              final weekDay = DateFormat.E(widget.locale).format(
                DateTime.now().subtract(Duration(days: DateTime.now().weekday - index - 1)),
              );
              return Expanded(
                child: Center(
                  child: Text(
                    weekDay,
                    style: widget.weekDayTextStyle ?? theme.textTheme.bodySmall,
                  ),
                ),
              );
            }),
          ),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            childAspectRatio: 1,
          ),
          itemCount: _days.length,
          itemBuilder: (context, index) {
            final date = _days[index];
            final isSelected = date.isAtSameMomentAs(_selectedDate);
            final isToday = date.isAtSameMomentAs(DateTime.now());
            final isCurrentMonth = date.month == _currentMonth.month;
            final isSpecial = widget.specialDates?.contains(date) ?? false;

            if (widget.dayBuilder != null) {
              return widget.dayBuilder!(date);
            }

            return InkWell(
              onTap: () => _onDaySelected(date),
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isSelected
                      ? defaultSelectedColor
                      : isToday
                          ? defaultTodayColor
                          : null,
                ),
                child: Center(
                  child: Text(
                    '${date.day}',
                    style: widget.dayTextStyle?.copyWith(
                      color: isSelected
                          ? Colors.white
                          : !isCurrentMonth
                              ? theme.disabledColor
                              : isSpecial
                                  ? defaultSelectedColor
                                  : null,
                    ) ??
                        TextStyle(
                          color: isSelected
                              ? Colors.white
                              : !isCurrentMonth
                                  ? theme.disabledColor
                                  : isSpecial
                                      ? defaultSelectedColor
                                      : null,
                        ),
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }
} 