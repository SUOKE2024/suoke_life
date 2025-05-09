import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/presentation/explore/explore_screen.dart';
import 'package:suoke_life/presentation/home/home_screen.dart';
import 'package:suoke_life/presentation/life/life_screen.dart';
import 'package:suoke_life/presentation/profile/profile_screen.dart';
import 'package:suoke_life/presentation/suoke/agent_chat_screen.dart';
import 'package:suoke_life/presentation/suoke/suoke_screen.dart';
import 'package:suoke_life/presentation/widgets/floating_agent_bubble.dart';
import 'package:suoke_life/presentation/home/contact_chat_screen.dart';

/// 索克生活APP的主应用类
///
/// 包含应用的全局配置，包括主题、路由和本地化
class SuokeLifeApp extends ConsumerStatefulWidget {
  const SuokeLifeApp({super.key});

  @override
  ConsumerState<SuokeLifeApp> createState() => _SuokeLifeAppState();
}

class _SuokeLifeAppState extends ConsumerState<SuokeLifeApp> {
  int _currentIndex = 0;
  
  // 主页面列表
  final List<Widget> _pages = [
    const HomeScreen(),
    const SuokeScreen(),
    const ExploreScreen(),
    const LifeScreen(),
    const ProfileScreen(),
  ];
  
  // 底部导航项配置
  final List<BottomNavigationBarItem> _navItems = [
    const BottomNavigationBarItem(
      icon: Icon(Icons.home_outlined),
      activeIcon: Icon(Icons.home),
      label: '首页',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.smart_toy_outlined),
      activeIcon: Icon(Icons.smart_toy),
      label: 'SUOKE',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.explore_outlined),
      activeIcon: Icon(Icons.explore),
      label: '探索',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.favorite_outline),
      activeIcon: Icon(Icons.favorite),
      label: 'LIFE',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.person_outline),
      activeIcon: Icon(Icons.person),
      label: '我的',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '索克生活',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF35BB78), // 索克绿
          secondary: const Color(0xFFFF6800), // 索克橙
        ),
        useMaterial3: true,
        // fontFamily: 'PingFang SC', // 注释掉或删除字体设置
      ),
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('zh', 'CN'),
      ],
      locale: const Locale('zh', 'CN'),
      home: Scaffold(
        body: Stack(
          children: [
            // 当前选中的页面
            _pages[_currentIndex],
            
            // 浮动智能体气泡
            const Positioned(
              right: 16,
              bottom: 80,
              child: FloatingAgentBubble(
                agentType: AgentType.xiaoAi, // 小艾智能体
                scene: 'home',               // 首页场景
                promptMessage: '您好，我是小艾，有什么我能帮您的吗？',
              ),
            ),
          ],
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          selectedItemColor: const Color(0xFF35BB78), // 索克绿
          unselectedItemColor: Colors.grey,
          items: _navItems,
        ),
      ),
    );
  }
}
