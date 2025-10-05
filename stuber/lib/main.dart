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

  // await _ensureAnonymousUser();

  runApp(const MyApp());
}

Future<void> _ensureAnonymousUser() async {
  print(' _ensureAnonymousUser() started');
  final supabase = Supabase.instance.client;
  
  if (supabase.auth.currentSession == null) {
    print('No session found, creating new user...');
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
