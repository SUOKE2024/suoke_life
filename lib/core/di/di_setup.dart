import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/network/llm_service_client.dart';
import 'package:suoke_life/core/network/health_service_client.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:suoke_life/core/di/modules/network_module.dart';
import 'package:suoke_life/core/di/modules/storage_module.dart';
import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/services/infrastructure/notification_service.dart';
import 'package:suoke_life/core/di/di_setup.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
void configureDependencies() => $initGetIt(getIt); 