import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/agreement_update.dart';
import '../../l10n/agreement_localizations.dart';

class AgreementUpdateDialog extends StatelessWidget {
  final AgreementUpdate update;
  final VoidCallback onView;
  final VoidCallback? onLater;

  const AgreementUpdateDialog({
    super.key,
    required this.update,
    required this.onView,
    this.onLater,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('yyyy年MM月dd日');
    final textTheme = Theme.of(context).textTheme;
    final l10n = AgreementLocalizations.of(context);

    return AlertDialog(
      title: Text(update.title),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (update.isRequired)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 8,
                vertical: 4,
              ),
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    size: 16,
                    color: Colors.red[700],
                  ),
                  const SizedBox(width: 4),
                  Text(
                    l10n.get('agreement_update_required'),
                    style: textTheme.bodySmall?.copyWith(
                      color: Colors.red[700],
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 16),
          Text(
            '${l10n.get('agreement_update_time')}: ${dateFormat.format(update.updateTime)}',
            style: textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            l10n.get('agreement_update_content'),
            style: textTheme.titleSmall,
          ),
          const SizedBox(height: 4),
          Text(
            update.summary,
            style: textTheme.bodyMedium,
          ),
        ],
      ),
      actions: [
        if (!update.isRequired && onLater != null)
          TextButton(
            onPressed: onLater,
            child: Text(l10n.get('agreement_view_later')),
          ),
        ElevatedButton(
          onPressed: onView,
          child: Text(
            update.isRequired ? 
                l10n.get('agreement_view_agree') : 
                l10n.get('agreement_view_now'),
          ),
        ),
      ],
    );
  }
} 