// lib/screens/auth/signin_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import './auth_service.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 60),
              
              // Logo and Welcome Text
              _buildHeader(),
              
              const SizedBox(height: 48),
              
              // Google Sign In Button
              _buildGoogleSignInButton(),
              
              const SizedBox(height: 24),
              
              // Divider
              _buildDivider(),
              
              const SizedBox(height: 24),
              
              // Email Sign In Form
              _buildEmailSignInForm(),
              
              const SizedBox(height: 16),
              
              // Forgot Password Link
              _buildForgotPasswordLink(),
              
              const SizedBox(height: 32),
              
              // Sign In Button
              _buildSignInButton(),
              
              const SizedBox(height: 24),
              
              // Sign Up Link
              _buildSignUpLink(),
              
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        // App Logo/Icon
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
        
        // Title
        Text(
          'Welcome Back',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.grey[800],
          ),
          textAlign: TextAlign.center,
        ),
        
        const SizedBox(height: 8),
        
        // Subtitle
        Text(
          'Sign in to continue your journey',
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Colors.grey[600],
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildGoogleSignInButton() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : () {
          // _handleGoogleSignIn(); // Disabled for now like your signup
        },
        icon: _buildGoogleIcon(),
        label: const Text(
          'Continue with Google',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: Colors.black87,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: Colors.black87,
          elevation: 0,
          side: BorderSide(color: Colors.grey[300]!),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Widget _buildGoogleIcon() {
    // Simple placeholder - replace with actual Google logo
    return Container(
      width: 20,
      height: 20,
      decoration: const BoxDecoration(
        color: Colors.red,
        shape: BoxShape.circle,
      ),
      child: const Center(
        child: Text(
          'G',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return Row(
      children: [
        Expanded(
          child: Container(
            height: 1,
            color: Colors.grey[300],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'or sign in with email',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
          ),
        ),
        Expanded(
          child: Container(
            height: 1,
            color: Colors.grey[300],
          ),
        ),
      ],
    );
  }

  Widget _buildEmailSignInForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Email Field
          _buildTextField(
            controller: _emailController,
            labelText: 'Email Address',
            hintText: 'Enter your email',
            prefixIcon: Icons.email_outlined,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Please enter your email';
              }
              if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                return 'Please enter a valid email address';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Password Field
          _buildTextField(
            controller: _passwordController,
            labelText: 'Password',
            hintText: 'Enter your password',
            prefixIcon: Icons.lock_outline,
            obscureText: _obscurePassword,
            textInputAction: TextInputAction.done,
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                color: Colors.grey[600],
              ),
              onPressed: () {
                setState(() {
                  _obscurePassword = !_obscurePassword;
                });
              },
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your password';
              }
              return null;
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String labelText,
    required String hintText,
    required IconData prefixIcon,
    TextInputType keyboardType = TextInputType.text,
    TextInputAction textInputAction = TextInputAction.next,
    bool obscureText = false,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        textInputAction: textInputAction,
        obscureText: obscureText,
        validator: validator,
        decoration: InputDecoration(
          labelText: labelText,
          hintText: hintText,
          prefixIcon: Icon(
            prefixIcon,
            color: Colors.grey[600],
          ),
          suffixIcon: suffixIcon,
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: Colors.grey[300]!),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: Colors.grey[300]!),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: Colors.blue[600]!, width: 2),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Colors.red),
          ),
          labelStyle: TextStyle(color: Colors.grey[700]),
          hintStyle: TextStyle(color: Colors.grey[500]),
        ),
      ),
    );
  }

  Widget _buildForgotPasswordLink() {
    return Align(
      alignment: Alignment.centerRight,
      child: GestureDetector(
        onTap: () {
          // TODO: Implement forgot password functionality
          _showInfoMessage('Forgot password feature coming soon!');
        },
        child: Text(
          'Forgot password?',
          style: TextStyle(
            color: Colors.blue[600],
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  Widget _buildSignInButton() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        gradient: LinearGradient(
          colors: [Colors.blue[600]!, Colors.blue[700]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleEmailSignIn,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isLoading
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : const Text(
                'Sign In',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
      ),
    );
  }

  Widget _buildSignUpLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          "Don't have an account? ",
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 14,
          ),
        ),
        GestureDetector(
          onTap: () {
            // Navigate to signup screen
            Navigator.of(context).pop(); // Go back to signup if using navigation stack
            // Or use: Navigator.pushReplacementNamed(context, '/signup');
          },
          child: Text(
            'Sign Up',
            style: TextStyle(
              color: Colors.blue[600],
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _handleEmailSignIn() async {
    if (!_formKey.currentState!.validate()) {
      HapticFeedback.lightImpact();
      return;
    }
    
    setState(() => _isLoading = true);
    
    try {
      final response = await _authService.signInWithEmail(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      
      if (response?.user != null && mounted) {
        _showSuccessMessage('Welcome back! Sign in successful.');
         await Future.delayed(const Duration(milliseconds: 500));
  if (mounted) {
    Navigator.of(context).pop(); // Removes SignInScreen, lets AuthGate show MainLayout
  }
        // AuthGate will automatically handle navigation to main app
      }
    // } catch (error) {
    //   if (mounted) {
    //     String errorMessage = 'Sign in failed. Please try again.';
        
    //     if (error.toString().contains('Invalid login credentials')) {
    //       errorMessage = 'Invalid email or password. Please check your credentials.';
    //     } else if (error.toString().contains('Email not confirmed')) {
    //       errorMessage = 'Please verify your email before signing in.';
    //     }
        
    //     _showErrorMessage(errorMessage);
    //     HapticFeedback.lightImpact();
    //   }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(
              Icons.check_circle,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
        backgroundColor: Colors.green[600],
        duration: const Duration(seconds: 2),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        margin: const EdgeInsets.all(16),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showErrorMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(
              Icons.error_outline,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
        backgroundColor: Colors.red[600],
        duration: const Duration(seconds: 3),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        margin: const EdgeInsets.all(16),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showInfoMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(
              Icons.info_outline,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
        backgroundColor: Colors.blue[600],
        duration: const Duration(seconds: 2),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        margin: const EdgeInsets.all(16),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}