import 'package:flutter/material.dart';
import 'dart:async';

class WelcomePage extends StatefulWidget {
  const WelcomePage({super.key});

  @override
  _WelcomePageState createState() => _WelcomePageState();
}

class _WelcomePageState extends State<WelcomePage> {
  double _opacity = 0.0;
  double _progress = 0.0;

  @override
  void initState() {
    super.initState();
    _startAnimation();
  }

  void _startAnimation() {
    Timer(const Duration(milliseconds: 500), () {
      setState(() {
        _opacity = 1.0;
      });
      Timer.periodic(const Duration(milliseconds: 100), (timer) {
        setState(() {
          _progress += 0.1;
          if (_progress >= 1.0) {
            timer.cancel();
            Navigator.pushReplacementNamed(context, '/login');
          }
        });
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedOpacity(
              opacity: _opacity,
              duration: const Duration(seconds: 1),
              child: const Text(
                '索克生活',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),
            LinearProgressIndicator(
              value: _progress,
              minHeight: 4,
              color: Colors.blue,
              backgroundColor: Colors.blue.withOpacity(0.3),
            ),
          ],
        ),
      ),
    );
  }
} 