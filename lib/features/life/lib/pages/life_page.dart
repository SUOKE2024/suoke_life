import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/features/life/lib/widgets/user_profile_card.dart';
import 'package:suoke_life/features/life/lib/widgets/health_advice_card.dart';
import 'package:suoke_life/features/life/lib/widgets/life_record_item.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

class LifePage extends StatefulWidget {
  const LifePage({Key? key}) : super(key: key);

  @override
  State<LifePage> createState() => _LifePageState();
}

class _LifePageState extends State<LifePage> {
  int _currentIndex = 1;
  final List<LifeRecord> _lifeRecords = [
    LifeRecord(
      title: 'Morning Walk',
      time: '8:00 AM',
      description: '30 minutes walk in the park',
    ),
    LifeRecord(
      title: 'Lunch',
      time: '12:00 PM',
      description: 'Healthy lunch at home',
    ),
    LifeRecord(
      title: 'Afternoon Reading',
      time: '3:00 PM',
      description: 'Reading a book for 1 hour',
    ),
    LifeRecord(
      title: 'Evening Exercise',
      time: '6:00 PM',
      description: '30 minutes of light exercise',
    ),
    LifeRecord(
      title: 'Dinner',
      time: '7:00 PM',
      description: 'Healthy dinner with family',
    ),
  ];

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
        title: Text(localizations.translate('life_title')),
      ),
      body: ListView(
        children: [
          const UserProfileCard(),
          const SizedBox(height: 16),
          const HealthAdviceCard(),
          const SizedBox(height: 16),
          ..._lifeRecords.map((record) => LifeRecordItem(
                title: record.title,
                time: record.time,
                description: record.description,
              )),
        ],
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}

class LifeRecord {
  final String title;
  final String time;
  final String description;

  LifeRecord({
    required this.title,
    required this.time,
    required this.description,
  });
} 