import 'package:injectable/injectable.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

@module
abstract class ThirdPartyModule {
  @lazySingleton
  Connectivity get connectivity => Connectivity();

  @lazySingleton
  FlutterLocalNotificationsPlugin get notifications => 
      FlutterLocalNotificationsPlugin();

  @lazySingleton
  FirebaseMessaging get messaging => FirebaseMessaging.instance;
} 