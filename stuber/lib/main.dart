import 'package:flutter/material.dart';
import 'package:stuber/app.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await dotenv.load(fileName: ".env");

  await Supabase.initialize(    
    url: dotenv.env['SUPABASE_URL']!,    
    anonKey: dotenv.env['SUPABASE_ANON_KEY']!,  
  );

  await _ensureAnonymousUser();
  
  runApp(const MyApp());
}

Future<void> _ensureAnonymousUser() async {
  final supabase = Supabase.instance.client;
  
  // Check if user is already signed in
  if (supabase.auth.currentSession == null) {
    try {
      await supabase.auth.signInAnonymously();
      print('Anonymous user created: ${supabase.auth.currentUser?.id}');
    } catch (e) {
      print('Error creating anonymous user: $e');
    }
  } else {
    print('Existing user session found: ${supabase.auth.currentUser?.id}');
  }
}