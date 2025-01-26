--- a/core/lib/config/app_config.dart
+++ b/core/lib/config/app_config.dart
@@ -10,6 +10,8 @@
   final String baseUrl;
   final String googleApiKey;
   final String sentryDsn;
+  final String redisHost;
+  final int redisPort;
 
   AppConfig({
     required this.appName,
@@ -17,6 +19,8 @@
     required this.baseUrl,
     required this.googleApiKey,
     required this.sentryDsn,
+    required this.redisHost,
+    required this.redisPort,
   });
 
   AppConfig.fromJson(Map<String, dynamic> json) {
@@ -25,6 +29,8 @@
       baseUrl: json['baseUrl'] as String,
       googleApiKey: json['googleApiKey'] as String,
       sentryDsn: json['sentryDsn'] as String,
+      redisHost: json['redisHost'] as String,
+      redisPort: json['redisPort'] as int,
     )
   }
 
@@ -33,6 +39,8 @@
       'baseUrl': baseUrl,
       'googleApiKey': googleApiKey,
       'sentryDsn': sentryDsn,
+      'redisHost': redisHost,
+      'redisPort': redisPort,
     };
   }
 }

import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static String get redisHost => dotenv.env['REDIS_HOST'] ?? 'localhost';
  static int get redisPort => int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
  static String get mysqlHost => dotenv.env['MYSQL_HOST'] ?? 'localhost';
  static int get mysqlPort => int.parse(dotenv.env['MYSQL_PORT'] ?? '3306');
  static String get mysqlUser => dotenv.env['MYSQL_USER'] ?? 'root';
  static String get mysqlDatabase => dotenv.env['MYSQL_DATABASE'] ?? 'suoke_life';
} 