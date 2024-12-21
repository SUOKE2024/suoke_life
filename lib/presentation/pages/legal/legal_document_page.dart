import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:url_launcher/url_launcher.dart';

class LegalDocumentPage extends StatelessWidget {
  final String title;
  final String content;

  const LegalDocumentPage({
    Key? key,
    required this.title,
    required this.content,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: Markdown(
        data: content,
        selectable: true,
        onTapLink: (text, href, title) {
          if (href != null) {
            launchUrl(Uri.parse(href));
          }
        },
        styleSheet: MarkdownStyleSheet(
          h1: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Get.theme.primaryColor,
          ),
          h2: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Get.theme.primaryColor,
          ),
          h3: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
          p: TextStyle(
            fontSize: 16,
            height: 1.5,
          ),
          listBullet: TextStyle(
            color: Get.theme.primaryColor,
          ),
          blockquote: TextStyle(
            color: Colors.grey[700],
            fontStyle: FontStyle.italic,
          ),
          code: TextStyle(
            backgroundColor: Colors.grey[200],
            fontFamily: 'monospace',
          ),
          codeblockDecoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }
} 