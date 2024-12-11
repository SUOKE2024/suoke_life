import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:share_plus/share_plus.dart';
import '../../services/agreement_service.dart';

class AgreementPage extends StatefulWidget {
  final String title;
  final String type;

  const AgreementPage({
    super.key,
    required this.title,
    required this.type,
  });

  @override
  State<AgreementPage> createState() => _AgreementPageState();
}

class _AgreementPageState extends State<AgreementPage> {
  final _agreementService = AgreementService.instance;
  String? _content;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadContent();
  }

  Future<void> _loadContent() async {
    try {
      final content = await _agreementService.getAgreement(widget.type);
      setState(() {
        _content = content;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = '加载失败: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _shareContent() async {
    if (_content == null) return;
    
    await Share.share(
      '${widget.title}\n\n$_content',
      subject: widget.title,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: _content == null ? null : _shareContent,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _error!,
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _isLoading = true;
                  _error = null;
                });
                _loadContent();
              },
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    return Markdown(
      data: _content!,
      selectable: true,
      styleSheet: MarkdownStyleSheet(
        h1: Theme.of(context).textTheme.headlineMedium,
        h2: Theme.of(context).textTheme.headlineSmall,
        h3: Theme.of(context).textTheme.titleLarge,
        p: Theme.of(context).textTheme.bodyLarge,
      ),
    );
  }
} 