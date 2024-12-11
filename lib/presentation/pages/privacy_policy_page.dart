import 'package:flutter/material.dart';
import 'agreement_page.dart';

class PrivacyPolicyPage extends StatelessWidget {
  const PrivacyPolicyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const AgreementPage(
      title: '隐私政策',
      type: 'privacy',
    );
  }
} 