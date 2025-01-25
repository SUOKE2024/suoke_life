import 'package:flutter/material.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';
import 'package:go_router/go_router.dart';

class ProfileSetupCard extends StatefulWidget {
  const ProfileSetupCard({Key? key}) : super(key: key);

  @override
  State<ProfileSetupCard> createState() => _ProfileSetupCardState();
}

class _ProfileSetupCardState extends State<ProfileSetupCard> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  void _register() {
    if (_formKey.currentState!.validate()) {
      // TODO: Implement registration logic
      context.go('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _usernameController,
                decoration: InputDecoration(
                  labelText: localizations.translate('username_label'),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return localizations.translate('username_required');
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: localizations.translate('email_label'),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return localizations.translate('email_required');
                  }
                  if (!value.contains('@')) {
                    return 'Please enter a valid email';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: localizations.translate('password_label'),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return localizations.translate('password_required');
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _register,
                child: Text(localizations.translate('register_button')),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 