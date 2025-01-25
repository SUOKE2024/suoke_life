import 'package:flutter/material.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

class AdminDashboardPage extends StatelessWidget {
  const AdminDashboardPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.translate('admin_dashboard_title')),
      ),
      body: Center(
        child: Text(localizations.translate('admin_dashboard_message')),
      ),
    );
  }
} 