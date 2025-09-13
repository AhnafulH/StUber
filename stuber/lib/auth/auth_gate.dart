import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import './auth_service.dart';
import './signup_screen.dart';
import '../common/widgets/navigation/main_layout.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({Key? key}) : super(key: key);
  

  @override
  Widget build(BuildContext context) {
    print("🔍 auth_gate called new");
    return StreamBuilder<AuthState>(
      stream: AuthService().authStateChanges,
      builder: (context, snapshot) {
         print("🔍 StreamBuilder snapshot: ${snapshot.data}");
        print("🔍 Connection state: ${snapshot.connectionState}");
        print("🔍 Session exists: ${snapshot.data?.session != null}");
        print("🔍 User ID: ${snapshot.data?.session?.user?.id}");
        // Show loading screen while checking auth state
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const AuthLoadingScreen();
        }

        // Check if user is authenticated
        final session = snapshot.data?.session;
        print(session);
        
        if (session != null) {
          // User is signed in → show main app
          print('hiasdfhish');
          return const MainLayout();
        } else {
          // User is not signed in → show signup screen
          return const SignUpScreen();
        }
      },
    );
  }
}

class AuthLoadingScreen extends StatelessWidget {
  const AuthLoadingScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // App logo/icon
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.blue[600],
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(
                Icons.directions_car,
                color: Colors.white,
                size: 40,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // App name
            Text(
              'Stuber',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            
            const SizedBox(height: 8),
            
            Text(
              'Share rides, save money',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 16,
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Loading indicator
            SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2.5,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[600]!),
              ),
            ),
            
            const SizedBox(height: 16),
            
            Text(
              'Loading...',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }
}