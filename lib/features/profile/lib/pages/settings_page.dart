import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';
import 'package:suoke_life/features/profile/lib/pages/health_data_input_page.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  int _currentIndex = 3;

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.translate('settings_title')),
      ),
      body: ListView(
        children: [
          ListTile(
            title: Text(localizations.translate('notifications')),
            onTap: () {
              // TODO: Implement notifications settings
            },
          ),
          ListTile(
            title: Text(localizations.translate('privacy')),
            onTap: () {
              // TODO: Implement privacy settings
            },
          ),
          ListTile(
            title: Text(localizations.translate('about')),
            onTap: () {
              // TODO: Implement about page
            },
          ),
          ListTile(
            title: const Text('Edit Profile'),
            onTap: () => context.go('/edit_profile'),
          ),
          ListTile(
            leading: const Icon(Icons.fitness_center),
            title: const Text('健康数据录入'),
            onTap: () {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const HealthDataInputPage()));
            },
          ),
          ListTile(
            title: const Text('Admin Dashboard'),
            onTap: () => context.go('/admin_dashboard'),
          ),
        ],
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}
