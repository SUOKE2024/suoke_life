import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'router/app_router.dart';

void main() => runApp(const SuokeLifeApp());

class SuokeLifeApp extends StatelessWidget {
  const SuokeLifeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '索克生活',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      routerConfig: goRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
