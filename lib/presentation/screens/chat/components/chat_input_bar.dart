import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChatInputBar extends ConsumerStatefulWidget {
  final Function(String) onSendText;
  final Function()? onAttachmentPressed;
  final Function()? onCameraPressed;
  final Function()? onMicPressed;
  final bool isLoading;
  
  const ChatInputBar({
    Key? key,
    required this.onSendText,
    this.onAttachmentPressed,
    this.onCameraPressed,
    this.onMicPressed,
    this.isLoading = false,
  }) : super(key: key);

  @override
  ConsumerState<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends ConsumerState<ChatInputBar> {
  final TextEditingController _textController = TextEditingController();
  bool _isComposing = false;

  @override
  void initState() {
    super.initState();
    _textController.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    setState(() {
      _isComposing = _textController.text.isNotEmpty;
    });
  }

  void _handleSubmitted(String text) {
    if (text.trim().isEmpty) return;
    
    _textController.clear();
    setState(() {
      _isComposing = false;
    });
    
    widget.onSendText(text);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            offset: const Offset(0, -1),
            blurRadius: 3,
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: widget.onAttachmentPressed,
              color: Theme.of(context).colorScheme.secondary,
            ),
            Expanded(
              child: TextField(
                controller: _textController,
                decoration: InputDecoration(
                  hintText: '请输入消息...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(20.0),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Theme.of(context).brightness == Brightness.dark
                      ? Colors.grey[800]
                      : Colors.grey[200],
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 8.0,
                  ),
                  suffixIcon: widget.onCameraPressed != null
                      ? IconButton(
                          icon: const Icon(Icons.camera_alt),
                          onPressed: widget.onCameraPressed,
                          color: Theme.of(context).colorScheme.secondary,
                        )
                      : null,
                ),
                keyboardType: TextInputType.multiline,
                maxLines: null,
                textInputAction: TextInputAction.newline,
                onSubmitted: _isComposing ? _handleSubmitted : null,
              ),
            ),
            const SizedBox(width: 8.0),
            _isComposing
                ? IconButton(
                    icon: widget.isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          )
                        : Icon(
                            Icons.send,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                    onPressed: widget.isLoading
                        ? null
                        : () => _handleSubmitted(_textController.text),
                  )
                : IconButton(
                    icon: const Icon(Icons.mic),
                    onPressed: widget.onMicPressed,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
          ],
        ),
      ),
    );
  }
} 