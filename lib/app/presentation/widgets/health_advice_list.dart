import 'package:flutter/material.dart';
import '../../data/models/health_advice.dart';
import 'health_advice_list_item.dart';
import 'package:get/get.dart';
import '../controllers/health_advice_controller.dart';
import 'health_advice_list_header.dart';

class HealthAdviceList extends StatelessWidget {
  final List<HealthAdvice> advices;
  final Function(HealthAdvice) onTap;

  const HealthAdviceList({
    Key? key,
    required this.advices,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<HealthAdviceController>();

    return RefreshIndicator(
      onRefresh: controller.refreshAdvices,
      child: CustomScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(
            child: HealthAdviceListHeader(advices: displayAdvices),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  return HealthAdviceListItem(
                    advice: displayAdvices[index],
                    onTap: () => onTap(displayAdvices[index]),
                  );
                },
                childCount: displayAdvices.length,
              ),
            ),
          ),
        ],
      ),
    );
  }
} 