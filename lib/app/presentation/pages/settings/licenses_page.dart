import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/licenses_controller.dart';

class LicensesPage extends GetView<LicensesController> {
  const LicensesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('开源许可'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView.builder(
          itemCount: controller.licenses.length,
          itemBuilder: (context, index) {
            final license = controller.licenses[index];
            return ListTile(
              title: Text(license.name),
              subtitle: Text(license.version),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => controller.showLicenseDetail(license),
            );
          },
        );
      }),
    );
  }
} 