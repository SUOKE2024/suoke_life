import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/navigation/navigation_bloc.dart';

@RoutePage()
class MainNavigationPage extends StatelessWidget {
  const MainNavigationPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<NavigationBloc>(),
      child: AutoTabsScaffold(
        routes: const [
          HomeTab(),
          SuokeTab(),
          ExploreTab(),
          LifeTab(),
          ProfileTab(),
        ],
        bottomNavigationBuilder: (_, tabsRouter) {
          return BottomNavigationBar(
            currentIndex: tabsRouter.activeIndex,
            onTap: tabsRouter.setActiveIndex,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.chat),
                label: '聊天',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.business),
                label: 'SUOKE',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.explore),
                label: '探索',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.favorite),
                label: 'LIFE',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.person),
                label: '我的',
              ),
            ],
          );
        },
      ),
    );
  }
} 