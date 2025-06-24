// import 'package:flutter/material.dart';
// import 'package:stuber/pages/map_page.dart';
// import 'package:google_maps_flutter/google_maps_flutter.dart';

// void main() {
//   // Initialize Flutter bindings
//   WidgetsFlutterBinding.ensureInitialized();
  
//   runApp(const MyApp());
// }

// class MyApp extends StatelessWidget {
//   const MyApp({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       debugShowCheckedModeBanner: false,
//       title: 'Google Maps Demo',
//       theme: ThemeData(
//         colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
//         useMaterial3: true,
//       ),
//       home: const MapPage(),
//     );
//   }
// }

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
  runApp(const MyApp());
}