import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';

abstract class LegalDocumentController extends GetxController {
  final isLoading = true.obs;
  final content = ''.obs;

  String get title;
  Future<String> loadDocument();

  @override
  void onInit() {
    super.onInit();
    _loadContent();
  }

  Future<void> _loadContent() async {
    isLoading.value = true;
    try {
      content.value = await loadDocument();
    } finally {
      isLoading.value = false;
    }
  }

  void shareDocument() {
    Share.share(
      '$title：\n\n${content.value}',
      subject: title,
    );
  }

  Future<void> handleLink(String href) async {
    if (href.startsWith('http')) {
      final url = Uri.parse(href);
      if (await canLaunchUrl(url)) {
        await launchUrl(url);
      }
    } else if (href.startsWith('#')) {
      final route = href.substring(1);
      Get.toNamed('/legal/$route');
    }
  }
} 