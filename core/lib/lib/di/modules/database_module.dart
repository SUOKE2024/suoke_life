import 'package:core/services/infrastructure/database_service.dart';
import 'package:core/services/infrastructure/database_service_impl.dart';
import 'package:injectable/injectable.dart';

@module
abstract class DatabaseModule {
  @singleton
  DatabaseService get databaseService => DatabaseServiceImpl();
} 