import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/core/database/database_helper.dart';
import 'package:suoke_app/app/core/services/storage/storage_service.dart';
import 'package:suoke_app/app/core/services/network/network_service.dart';
import 'package:suoke_app/app/services/features/ai/assistants/xiaoi_service.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service_impl.dart';
import 'package:suoke_app/app/presentation/pages/home/home_page.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';
import 'app/routes/app_pages.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化服务
  final db = DatabaseHelper();
  final storage = StorageService();
  final network = NetworkService();
  final xiaoi = XiaoiService(network);
  final suoke = SuokeServiceImpl(db);

  await Future.wait([
    db.init(),
    storage.init(),
    network.init(),
    xiaoi.init(),
    suoke.init(),
  ]);

  // 注册服务
  Get.put<DatabaseHelper>(db);
  Get.put<StorageService>(storage);
  Get.put<NetworkService>(network);
  Get.put<XiaoiService>(xiaoi);
  Get.put<SuokeService>(suoke);

  // 注册控制器
  Get.put<HomeController>(HomeController(suoke));

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'SUOKE',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/',
      getPages: AppPages.routes,
    );
  }
}
