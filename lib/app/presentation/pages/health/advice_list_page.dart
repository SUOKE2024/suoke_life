import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/health_advice_controller.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/error_state.dart';
import '../../widgets/loading_state.dart';
import '../../widgets/health_advice_list.dart';
import '../../widgets/search_bar.dart';

class AdviceListPage extends GetView<HealthAdviceController> {
  const AdviceListPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康建议'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: SearchBar(
            hint: '搜索健康建议...',
            onChanged: controller.search,
            onClear: () => controller.search(''),
          ),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: controller.refreshAdvices,
        child: Obx(() {
          if (controller.isLoading.value) {
            return const LoadingState(
              message: '正在加载健康建议...',
            );
          }
          if (controller.advices.isEmpty) {
            return EmptyState(
              message: '暂无健康建议',
              icon: Icons.healing,
              onRetry: controller.loadAdvices,
            );
          }
          if (controller.error.value != null) {
            return ErrorState(
              message: controller.error.value!,
              onRetry: controller.loadAdvices,
            );
          }
          return HealthAdviceList(
            advices: controller.advices,
            onTap: controller.onAdviceTap,
          );
        }),
      ),
    );
  }
} 