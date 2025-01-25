import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class CalendarPage extends StatelessWidget {
  const CalendarPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('日历'),
      ),
      body: const Center(
        child: Text('日历页面'),
      ),
    );
  }
} 