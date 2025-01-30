// Remove all imports and code related to 'injectable'

@module
abstract class StorageModule {
  @factoryMethod
  Future<SharedPreferences> createPrefs() => SharedPreferences.getInstance();
} 