import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/explore/coffee_bloc.dart';

@RoutePage()
class CoffeePage extends StatelessWidget {
  const CoffeePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<CoffeeBloc>()
        ..add(const CoffeeEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('咖啡时光'),
          actions: [
            IconButton(
              icon: const Icon(Icons.search),
              onPressed: () => context.router.push(const CoffeeSearchRoute()),
            ),
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  builder: (context) => const CoffeeFilterSheet(),
                );
              },
            ),
          ],
        ),
        body: BlocBuilder<CoffeeBloc, CoffeeState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (coffeeShops) => ListView.builder(
                itemCount: coffeeShops.length,
                itemBuilder: (context, index) {
                  final shop = coffeeShops[index];
                  return CoffeeShopCard(
                    shop: shop,
                    onTap: () => context.router.push(
                      CoffeeShopDetailRoute(id: shop.id),
                    ),
                  );
                },
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => context.router.push(const CoffeeRecommendRoute()),
          child: const Icon(Icons.recommend),
        ),
      ),
    );
  }
} 