import 'package:flutter_test/flutter_test.dart';
import 'dart:io';
import 'package:suoke_life/core/di/injection.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

void main() async {
  await dotenv.load(fileName: ".env");
  configureDependencies();
  final featureTestDirs = [
    'test/features/home/pages',
    'test/features/suoke/pages',
    'test/features/suoke/widgets',
    'test/features/explore/pages',
    'test/features/explore/widgets',
    'test/features/life/widgets',
    'test/features/profile/pages',
    'test/features/auth/pages',
    'test/features/auth/widgets',
  ];

  for (final dir in featureTestDirs) {
    group('Testing $dir', () {
      final testFiles = Directory(dir)
          .listSync()
          .whereType<File>()
          .where((file) => file.path.endsWith('_test.dart'))
          .toList();

      for (final file in testFiles) {
        test(file.path, () async {
          final result = await Process.run('flutter', ['test', file.path]);
          expect(result.exitCode, 0, reason: 'Test failed: ${file.path}\n${result.stderr}');
          print('Test passed: ${file.path}');
        });
      }
    });
  }

  group('All Features Tests', () {
    // 这里可以添加其他测试
  });
} 