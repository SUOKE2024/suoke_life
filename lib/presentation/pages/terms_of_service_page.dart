import 'package:flutter/material.dart';
import 'agreement_page.dart';

class TermsOfServicePage extends StatelessWidget {
  const TermsOfServicePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const AgreementPage(
      title: '用户协议',
      type: 'terms',
    );
  }
} 