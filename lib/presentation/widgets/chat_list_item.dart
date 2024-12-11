import 'package:flutter/material.dart';
import 'package:timeago/timeago.dart' as timeago;

class ChatListItem extends StatelessWidget {
  final String avatar;
  final String name;
  final String lastMessage;
  final DateTime timestamp;
  final int unreadCount;
  final VoidCallback onTap;
  final bool isPinned;
  final bool isMuted;

  const ChatListItem({
    super.key,
    required this.avatar,
    required this.name,
    required this.lastMessage,
    required this.timestamp,
    this.unreadCount = 0,
    required this.onTap,
    this.isPinned = false,
    this.isMuted = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        color: isPinned ? theme.colorScheme.surfaceVariant.withOpacity(0.3) : null,
        child: Row(
          children: [
            Stack(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundImage: AssetImage(avatar),
                ),
                if (unreadCount > 0)
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.error,
                        shape: BoxShape.circle,
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Text(
                        unreadCount > 99 ? '99+' : unreadCount.toString(),
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onError,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (isPinned)
                        Padding(
                          padding: const EdgeInsets.only(right: 4),
                          child: Icon(
                            Icons.push_pin,
                            size: 16,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      Expanded(
                        child: Text(
                          name,
                          style: theme.textTheme.titleMedium,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        timeago.format(timestamp, locale: 'zh'),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      if (isMuted)
                        Padding(
                          padding: const EdgeInsets.only(right: 4),
                          child: Icon(
                            Icons.volume_off,
                            size: 16,
                            color: theme.colorScheme.outline,
                          ),
                        ),
                      Expanded(
                        child: Text(
                          lastMessage,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: unreadCount > 0
                                ? theme.colorScheme.onSurface
                                : theme.colorScheme.outline,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 