import 'package:flutter/material.dart';

class AppTitle extends StatelessWidget {
  final String text;

  const AppTitle({super.key, required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(text);
  }
} 