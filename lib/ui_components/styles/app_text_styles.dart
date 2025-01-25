import 'package:flutter/material.dart';

class AppTextStyles {
  static TextStyle get title => const TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
      );

  static TextStyle get subtitle => const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w500,
      );

  static TextStyle get body => const TextStyle(
        fontSize: 16,
      );

  static TextStyle get caption => const TextStyle(
        fontSize: 14,
        color: Colors.grey,
      );
} 