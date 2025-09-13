// lib/services/auth_service.dart
// import 'package:google_sign_in/google_sign_in.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AuthService {
  final SupabaseClient _supabase = Supabase.instance.client;
  
  // Configure Google Sign In using environment variable
  // final GoogleSignIn _googleSignIn = GoogleSignIn(
  //   clientId: dotenv.env['GOOGLE_CLIENT_ID']!,
  // );

  // Email Sign Up
  Future<AuthResponse?> signUpWithEmail({
    required String email,
    required String password,
    required String fullName,
    String? phone, // Add phone parameter
  }) async {
    try {
      final response = await _supabase.auth.signUp(
        email: email,
        password: password,
        data: {
          'full_name': fullName,
          'user_type': 'rider', // Set default as rider
          'created_at': DateTime.now().toIso8601String(),
        },
      );

      // Create profile in profiles table with phone number
      if (response.user != null) {
        await _createOrUpdateProfile(
          userId: response.user!.id,
          fullName: fullName,
          email: email,
          phone: phone, // Pass phone to profile creation
        );
      }

      return response;
    } on AuthException catch (error) {
      throw Exception('Authentication error: ${error.message}');
    } catch (error) {
      throw Exception('Sign up failed: $error');
    }
  }

  // Google Sign In
  // Future<AuthResponse?> signInWithGoogle() async {
  //   try {
  //     final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
  //     if (googleUser == null) {
  //       // User cancelled the sign-in
  //       return null;
  //     }

  //     final GoogleSignInAuthentication googleAuth = 
  //         await googleUser.authentication;

  //     final response = await _supabase.auth.signInWithIdToken(
  //       provider: OAuthProvider.google,
  //       idToken: googleAuth.idToken!,
  //       accessToken: googleAuth.accessToken!,
  //     );

  //     // Create or update user profile after Google sign in
  //     if (response.user != null) {
  //       await _createOrUpdateProfile(
  //         userId: response.user!.id,
  //         fullName: googleUser.displayName ?? 'Google User',
  //         email: googleUser.email,
  //         photoUrl: googleUser.photoUrl,
  //         // Note: Google doesn't provide phone number, so phone will be null
  //         // User can add phone later in profile settings
  //       );
  //     }

  //     return response;
  //   } on AuthException catch (error) {
  //     throw Exception('Google authentication error: ${error.message}');
  //   } catch (error) {
  //     throw Exception('Google sign in failed: $error');
  //   }
  // }

  // Email Sign In
  Future<AuthResponse?> signInWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _supabase.auth.signInWithPassword(
        email: email,
        password: password,
      );
      return response;
    } on AuthException catch (error) {
      throw Exception('Sign in error: ${error.message}');
    } catch (error) {
      throw Exception('Sign in failed: $error');
    }
  }

  // Create or update user profile in profiles table
  Future<void> _createOrUpdateProfile({
    required String userId,
    required String fullName,
    required String email,
    // String? photoUrl,
    String? phone, // Add phone parameter
  }) async {
    try {
      await _supabase.from('profiles').upsert({
        'id': userId,
        'full_name': fullName,
        'email': email,
        // 'photo_url': photoUrl,
        'phone': phone, // Store phone in database
        'user_type': 'rider',
        'created_at': DateTime.now().toIso8601String(),
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (error) {
      // Don't throw here as this is a secondary operation
      print('Failed to create/update profile: $error');
    }
  }

  // Sign Out
  Future<void> signOut() async {
    try {
      // await _googleSignIn.signOut();
      await _supabase.auth.signOut();
    } catch (error) {
      throw Exception('Sign out failed: $error');
    }
  }

  // Get current user
  User? getCurrentUser() {
    return _supabase.auth.currentUser;
  }

  // Listen to auth state changes
  Stream<AuthState> get authStateChanges => _supabase.auth.onAuthStateChange;

  // Commented out methods - uncomment when needed later:
  
  // Get user profile
  // Future<Map<String, dynamic>?> getUserProfile() async {
  //   final user = getCurrentUser();
  //   if (user == null) return null;

  //   try {
  //     final response = await _supabase
  //         .from('profiles')
  //         .select()
  //         .eq('id', user.id)
  //         .single();
      
  //     return response;
  //   } catch (error) {
  //     print('Failed to get user profile: $error');
  //     return null;
  //   }
  // }

  // Update user profile
  // Future<void> updateUserProfile({
  //   required String fullName,
  //   String? phone,
  //   String? photoUrl,
  // }) async {
  //   final user = getCurrentUser();
  //   if (user == null) throw Exception('No authenticated user');

  //   try {
  //     await _supabase.from('profiles').update({
  //       'full_name': fullName,
  //       'phone': phone,
  //       'photo_url': photoUrl,
  //       'updated_at': DateTime.now().toIso8601String(),
  //     }).eq('id', user.id);
  //   } catch (error) {
  //     throw Exception('Failed to update profile: $error');
  //   }
  // }

  // Reset Password
  // Future<void> resetPassword({required String email}) async {
  //   try {
  //     await _supabase.auth.resetPasswordForEmail(email);
  //   } on AuthException catch (error) {
  //     throw Exception('Password reset error: ${error.message}');
  //   } catch (error) {
  //     throw Exception('Password reset failed: $error');
  //   }
  // }

  // Check if user email is verified
  // bool isEmailVerified() {
  //   final user = getCurrentUser();
  //   return user?.emailConfirmedAt != null;
  // }

  // Resend verification email
  // Future<void> resendVerificationEmail() async {
  //   try {
  //     final user = getCurrentUser();
  //     if (user?.email != null) {
  //       await _supabase.auth.resend(
  //         type: OtpType.signup,
  //         email: user!.email!,
  //       );
  //     }
  //   } on AuthException catch (error) {
  //     throw Exception('Failed to resend verification: ${error.message}');
  //   } catch (error) {
  //     throw Exception('Failed to resend verification: $error');
  //   }
  // }
}