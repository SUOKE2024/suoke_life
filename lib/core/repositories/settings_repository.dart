import 'package:suoke_life/core/models/settings.dart';

abstract class SettingsRepository {
  Future<Settings?> getSettings();
  Future<void> saveSettings(Settings settings);
} 