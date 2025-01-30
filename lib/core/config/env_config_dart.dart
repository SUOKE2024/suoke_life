import 'dart:io';

class EnvConfigDart {
  static late EnvConfigDart _instance;
  late String aiApiKey;

  EnvConfigDart._();

  static Future<void> init() async {
    _instance = EnvConfigDart._();
    await _instance._load();
  }

  static EnvConfigDart get instance => _instance;

  Future<void> _load() async {
    final file = File('.env');
    if (!await file.exists()) {
      throw Exception('Environment file .env not found');
    }

    final lines = await file.readAsLines();
    final env = Map.fromEntries(
      lines
          .where((line) => line.isNotEmpty && !line.startsWith('#'))
          .map((line) => line.split('='))
          .where((parts) => parts.length == 2)
          .map((parts) => MapEntry(parts[0].trim(), parts[1].trim())),
    );

    aiApiKey = env['AI_API_KEY'] ?? '';
    if (aiApiKey.isEmpty) {
      throw Exception('AI_API_KEY not found in environment file');
    }
  }
} 