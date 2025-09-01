// import 'package:flutter/material.dart';
// // import 'package:stuber/config/theme.dart';
// import 'package:stuber/common/widgets/navigation/main_layout.dart';

// class MyApp extends StatelessWidget {
//   const MyApp({Key? key}) : super(key: key);

//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       title: 'My Flutter App',
//       // theme: AppTheme.lightTheme,
//       // darkTheme: AppTheme.darkTheme,
//       themeMode: ThemeMode.system, // Respect system theme settings
//       home: const MainLayout(),
//       debugShowCheckedModeBanner: false,
//     );
//   }
// }


import 'package:flutter/material.dart';
// import 'package:stuber/config/theme.dart';
import 'package:stuber/auth/auth_gate.dart';

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
     print("🔍 app.dart called new");
    return MaterialApp(
      title: 'Stuber - Ride Share',
      // theme: AppTheme.lightTheme,
      // darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const AuthGate(), // Clean and simple!
      debugShowCheckedModeBanner: false,
    );
  }
}