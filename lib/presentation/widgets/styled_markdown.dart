import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:url_launcher/url_launcher.dart';

class StyledMarkdown extends StatelessWidget {
  final String data;
  final bool selectable;

  const StyledMarkdown({
    super.key,
    required this.data,
    this.selectable = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Markdown(
      data: data,
      selectable: selectable,
      styleSheet: MarkdownStyleSheet(
        h1: theme.textTheme.headlineLarge,
        h2: theme.textTheme.headlineMedium,
        h3: theme.textTheme.headlineSmall,
        p: theme.textTheme.bodyLarge,
      ),
      onTapLink: (text, href, title) {
        if (href != null) {
          launchUrl(Uri.parse(href));
        }
      },
    );
  }
} 