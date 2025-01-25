import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../blocs/life/calendar_bloc.dart';

@RoutePage()
class CalendarPage extends StatelessWidget {
  const CalendarPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<CalendarBloc>()
        ..add(const CalendarEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('日历'),
          actions: [
            IconButton(
              icon: const Icon(Icons.today),
              onPressed: () {
                // 跳转到今天
              },
            ),
          ],
        ),
        body: BlocBuilder<CalendarBloc, CalendarState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (events) => Column(
                children: [
                  TableCalendar(
                    firstDay: DateTime.utc(2021, 1, 1),
                    lastDay: DateTime.utc(2030, 12, 31),
                    focusedDay: DateTime.now(),
                    eventLoader: (day) {
                      // 返回当天的事件
                      return events[day] ?? [];
                    },
                    onDaySelected: (selectedDay, focusedDay) {
                      // 处理日期选择
                    },
                  ),
                  Expanded(
                    child: ListView.builder(
                      itemCount: state.selectedDayEvents.length,
                      itemBuilder: (context, index) {
                        final event = state.selectedDayEvents[index];
                        return ListTile(
                          title: Text(event.title),
                          subtitle: Text(event.description),
                          trailing: Text(event.time),
                          onTap: () {
                            // 处理事件点击
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            // 添加新事件
          },
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
} 