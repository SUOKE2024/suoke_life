import 'package:flutter/material.dart';
import 'agreement_zh.dart';
import 'agreement_en.dart';

class AgreementLocalizations {
  final Locale locale;
  
  AgreementLocalizations(this.locale);
  
  static AgreementLocalizations of(BuildContext context) {
    return Localizations.of<AgreementLocalizations>(context, AgreementLocalizations)!;
  }
  
  static const LocalizationsDelegate<AgreementLocalizations> delegate = _AgreementLocalizationsDelegate();
  
  static final Map<String, Map<String, String>> _localizedValues = {
    'en': AgreementEn.values,
    'zh': AgreementZh.values,
  };
  
  String get(String key) {
    final languageCode = locale.languageCode;
    final values = _localizedValues[languageCode] ?? AgreementEn.values;
    return values[key] ?? AgreementEn.values[key] ?? key;
  }
}

class _AgreementLocalizationsDelegate extends LocalizationsDelegate<AgreementLocalizations> {
  const _AgreementLocalizationsDelegate();
  
  @override
  bool isSupported(Locale locale) {
    return ['en', 'zh'].contains(locale.languageCode);
  }
  
  @override
  Future<AgreementLocalizations> load(Locale locale) async {
    return AgreementLocalizations(locale);
  }
  
  @override
  bool shouldReload(_AgreementLocalizationsDelegate old) => false;
} 