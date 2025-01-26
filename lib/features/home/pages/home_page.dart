import 'package:flutter/material.dart';
import 'package:suoke_life_app_app/core/config/app_config.dart';
import 'package:suoke_life_app_app/features/home/widgets/health_status_card.dart';
import 'package:suoke_life_app_app/features/home/widgets/quick_action_grid.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppConfig.appName),
        actions: const [
          NotificationIndicator(key: Key('notification_indicator'))
        ],
      ),
      body: const Column(
        children: [
          HealthStatusCard(key: Key('health_status_card')),
          SizedBox(height: 16),
          QuickActionGrid(key: Key('quick_action_grid')),
          RecentActivitiesSection(),
        ],
      ),
    );
  }
}
