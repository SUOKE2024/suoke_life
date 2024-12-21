import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/user_agreement_controller.dart';

class UserAgreementPage extends BasePage<UserAgreementController> {
  const UserAgreementPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('用户协议'),
      actions: [
        IconButton(
          icon: const Icon(Icons.share),
          onPressed: controller.shareAgreement,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return Markdown(
        data: controller.content.value,
        selectable: true,
        styleSheet: MarkdownStyleSheet(
          h1: Get.textTheme.headlineMedium,
          h2: Get.textTheme.titleLarge,
          h3: Get.textTheme.titleMedium,
          p: Get.textTheme.bodyMedium,
          listBullet: Get.textTheme.bodyMedium,
          blockquote: Get.textTheme.bodyMedium?.copyWith(
            color: Colors.grey[600],
            fontStyle: FontStyle.italic,
          ),
          code: Get.textTheme.bodyMedium?.copyWith(
            fontFamily: 'monospace',
            backgroundColor: Colors.grey[200],
          ),
          codeblockDecoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        onTapLink: (text, href, title) {
          if (href != null) {
            controller.handleLink(href);
          }
        },
      );
    });
  }
} 