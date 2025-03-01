import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app.dart';
import 'core/config/app_config.dart';
import 'core/config/environment.dart';
import 'core/utils/logger.dart';
import 'core/utils/provider_observer.dart';
import 'di/providers.dart';
import 'core/storage/hydrated_provider.dart';

/// 应用入口点
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    // 设置应用方向
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
    
    // 加载环境配置
    await Environment.initialize(env: Environment.prod);
    
    // 初始化应用配置
    await AppConfig.initialize();
    
    // 配置日志
    configureLogger();
    
    logger.i('应用启动: 环境 ${Environment.current.name}');
    
    // 创建Provider容器观察器
    final providerObserver = ProviderContainerObserver();
    
    // 初始化持久化状态系统
    await HydratedStateNotifier.initialize();
    
    // 初始化数据库
    await _initDatabase();
    
    // 启动应用，使用ProviderScope包装
    runApp(
      ProviderScope(
        observers: [providerObserver],
        child: Consumer(
          builder: (context, ref, _) {
            // 异步初始化AI代理，但不使用其结果
            ref.watch(aiAgentInitializerProvider);
            return const SuokeLifeApp();
          },
        ),
      ),
    );
    
  } catch (e, stackTrace) {
    logger.e('应用启动失败', error: e, stackTrace: stackTrace);
    
    // 显示错误启动页面
    runApp(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  color: Colors.red,
                  size: 60,
                ),
                const SizedBox(height: 16),
                const Text(
                  '应用启动时发生错误',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  e.toString(),
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// 初始化数据库
Future<void> _initDatabase() async {
  final documentsDirectory = await getApplicationDocumentsDirectory();
  final path = '${documentsDirectory.path}/suoke_life.db';
  
  // 打开数据库（如果不存在则创建）
  await openDatabase(
    path,
    version: 1,
    onCreate: (Database db, int version) async {
      // 创建用户表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          avatar_url TEXT,
          email TEXT,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL
        )
      ''');
      
      // 创建聊天记录表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY,
          sender_id TEXT NOT NULL,
          sender_type TEXT NOT NULL,
          content TEXT NOT NULL,
          timestamp INTEGER NOT NULL,
          read INTEGER NOT NULL DEFAULT 0,
          type TEXT NOT NULL,
          FOREIGN KEY (sender_id) REFERENCES users (id)
        )
      ''');
      
      // 创建知识库表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          category TEXT NOT NULL,
          tags TEXT,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL
        )
      ''');
      
      // 创建健康数据表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          type TEXT NOT NULL,
          value REAL NOT NULL,
          unit TEXT NOT NULL,
          timestamp INTEGER NOT NULL,
          note TEXT,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      ''');
    },
    onUpgrade: (Database db, int oldVersion, int newVersion) async {
      // 处理数据库升级
      if (oldVersion < 2) {
        // 未来的版本2升级代码
      }
    },
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // TRY THIS: Try running your application with "flutter run". You'll see
        // the application has a purple toolbar. Then, without quitting the app,
        // try changing the seedColor in the colorScheme below to Colors.green
        // and then invoke "hot reload" (save your changes or press the "hot
        // reload" button in a Flutter-supported IDE, or press "r" if you used
        // the command line to start the app).
        //
        // Notice that the counter didn't reset back to zero; the application
        // state is not lost during the reload. To reset the state, use hot
        // restart instead.
        //
        // This works for code too, not just values: Most code changes can be
        // tested with just a hot reload.
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      // This call to setState tells the Flutter framework that something has
      // changed in this State, which causes it to rerun the build method below
      // so that the display can reflect the updated values. If we changed
      // _counter without calling setState(), then the build method would not be
      // called again, and so nothing would appear to happen.
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Center(
        // Center is a layout widget. It takes a single child and positions it
        // in the middle of the parent.
        child: Column(
          // Column is also a layout widget. It takes a list of children and
          // arranges them vertically. By default, it sizes itself to fit its
          // children horizontally, and tries to be as tall as its parent.
          //
          // Column has various properties to control how it sizes itself and
          // how it positions its children. Here we use mainAxisAlignment to
          // center the children vertically; the main axis here is the vertical
          // axis because Columns are vertical (the cross axis would be
          // horizontal).
          //
          // TRY THIS: Invoke "debug painting" (choose the "Toggle Debug Paint"
          // action in the IDE, or press "p" in the console), to see the
          // wireframe for each widget.
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
