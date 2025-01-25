import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class QuestionnaireListPage extends StatelessWidget {
  const QuestionnaireListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('问卷列表')),
      body: const Center(child: Text('问卷列表页面')),
    );
  }
} 