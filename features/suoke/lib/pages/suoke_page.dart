import 'package:flutter/material.dart';
import 'package:suoke_life/libs/ui_components/lib/navigation/bottom_navigation_bar.dart';

class SuokePage extends StatefulWidget {
  const SuokePage({Key? key}) : super(key: key);

  @override
  _SuokePageState createState() => _SuokePageState();
}

class _SuokePageState extends State<SuokePage> {
  int _currentIndex = 1;

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Suoke'),
      ),
      body: const Center(
        child: Text('Suoke Page Content'),
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
} 