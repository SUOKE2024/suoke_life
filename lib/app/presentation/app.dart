import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../core/router/router_config.dart';
import '../core/di/injection.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = getIt<AppRouter>();
    
    return MaterialApp.router(
      title: 'Suoke Life',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      routerDelegate: router.delegate(),
      routeInformationParser: router.defaultRouteParser(),
    );
  }
} 