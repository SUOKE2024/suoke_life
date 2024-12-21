import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../data/models/life_record.dart';

class CalendarView extends StatelessWidget {
  final Rx<DateTime> selectedDate;
  final RxMap<DateTime, List<LifeRecord>> events;
  final Function(DateTime) onDateSelected;

  const CalendarView({
    Key? key,
    required this.selectedDate,
    required this.events,
    required this.onDateSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Obx(() => TableCalendar<LifeRecord>(
        firstDay: DateTime.utc(2020, 1, 1),
        lastDay: DateTime.now().add(const Duration(days: 365)),
        focusedDay: selectedDate.value,
        selectedDayPredicate: (day) => isSameDay(selectedDate.value, day),
        eventLoader: (day) => events[day] ?? [],
        calendarFormat: CalendarFormat.month,
        startingDayOfWeek: StartingDayOfWeek.monday,
        headerStyle: HeaderStyle(
          titleCentered: true,
          formatButtonVisible: false,
          titleTextStyle: Get.textTheme.titleMedium!,
        ),
        calendarStyle: CalendarStyle(
          outsideDaysVisible: false,
          selectedDecoration: BoxDecoration(
            color: Theme.of(context).primaryColor,
            shape: BoxShape.circle,
          ),
          todayDecoration: BoxDecoration(
            color: Theme.of(context).primaryColor.withOpacity(0.3),
            shape: BoxShape.circle,
          ),
          markerDecoration: BoxDecoration(
            color: Theme.of(context).primaryColor,
            shape: BoxShape.circle,
          ),
        ),
        onDaySelected: (selectedDay, focusedDay) {
          onDateSelected(selectedDay);
        },
      )),
    );
  }
} 