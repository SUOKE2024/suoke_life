import 'package:flutter/material.dart';
import 'package:suoke_life/presentation/widgets/service_grid.dart';
import 'package:suoke_life/presentation/widgets/service_category_list.dart';

class ServicePage extends StatelessWidget {
  const ServicePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // 搜索栏
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: TextField(
                decoration: InputDecoration(
                  hintText: '搜索服务',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Colors.grey[100],
                ),
              ),
            ),
            
            // 常用服务网格
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16.0),
              child: ServiceGrid(),
            ),
            
            const SizedBox(height: 16),
            
            // 服务分类列表
            const Expanded(
              child: ServiceCategoryList(),
            ),
          ],
        ),
      ),
    );
  }
} 