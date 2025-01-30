import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/features/life/lib/widgets/user_profile_card.dart';
import 'package:suoke_life/features/life/lib/widgets/health_advice_card.dart';
import 'package:suoke_life/features/life/lib/widgets/life_record_item.dart';
import 'package:suoke_life/lib/core/utils/app_localizations.dart';
import 'package:suoke_life/lib/core/widgets/common_bottom_navigation_bar.dart';
import 'package:suoke_life/lib/core/widgets/common_scaffold.dart';

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
    LifeRecord(
      title: 'Night Meditation',
      time: '9:00 PM',
      description: '15 minutes of meditation',
    ),
    LifeRecord(
      title: 'Breakfast',
      time: '7:00 AM',
      description: 'Healthy breakfast to start the day',
    ),
    LifeRecord(
      title: 'Work',
      time: '9:00 AM',
      description: 'Focus on work tasks',
    ),
    LifeRecord(
      title: 'Relaxation',
      time: '5:00 PM',
      description: 'Relax and unwind',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return CommonScaffold(
      title: AppLocalizations.of(context)!.translate('life') ?? 'Life',
      body: Column(
        children: [
          UserProfileCard(
            userName: 'John Doe',
            userPoints: 1200,
            onTap: () {
              // 实现用户信息逻辑
              Navigator.pushNamed(context, '/userProfile');
            },
          ),
          HealthAdviceCard(
            advice: 'Drink 8 glasses of water daily.',
            onTap: () {
              // 实现健康建议逻辑
              Navigator.pushNamed(context, '/healthAdvice');
            },
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _lifeRecords.length,
              itemBuilder: (context, index) {
                final record = _lifeRecords[index];
                return LifeRecordItem(
                  title: record.title,
                  time: record.time,
                  description: record.description,
                  onTap: () {
                    // 实现生活记录详情逻辑
                    Navigator.pushNamed(context, '/lifeRecordDetail', arguments: record);
                  },
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 实现添加记录逻辑
          _addRecord();
        },
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: CommonBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
            // TODO: 实现底部导航逻辑
          });
        },
      ),
    );
  }

  void _addRecord() {
    // TODO: 实现添加记录逻辑
    print('记录添加成功');
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