import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/home/home_controller.dart';
import '../chat/chat_page.dart';
import '../suoke/suoke_page.dart';
import '../explore/explore_page.dart';
import '../life/life_page.dart';
import '../profile/profile_page.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import 'package:get_it/get_it.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final getIt = GetIt.instance;

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => getIt<HomeBloc>()..add(InitializeHome()),
      child: BlocBuilder<HomeBloc, HomeState>(
        builder: (context, state) {
          return Scaffold(
            body: Consumer(
              builder: (context, ref, child) {
                final config = ref.watch(configProvider);
                final session = ref.watch(sessionProvider);
                
                if (state is HomeLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                
                if (state is HomeError) {
                  return ErrorView(
                    message: state.message,
                    onRetry: () => context.read<HomeBloc>().add(InitializeHome()),
                  );
                }
                
                return IndexedStack(
                  index: (state as HomeLoaded).currentPage,
                  children: const [
                    ChatPage(),
                    SuokePage(),
                    ExplorePage(),
                    LifePage(),
                    ProfilePage(),
                  ],
                );
              },
            ),
            bottomNavigationBar: const HomeNavigationBar(),
          );
        },
      ),
    );
  }
} 