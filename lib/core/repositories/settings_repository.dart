import 'package:suoke_life/lib/core/models/settings.dart';

abstract class SettingsRepository {
  Future<Settings?> getSettings();
  Future<void> saveSettings(Settings settings);
} 