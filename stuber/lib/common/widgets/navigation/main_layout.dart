import 'package:flutter/material.dart';
// import 'package:my_app/features/favorites/screens/favorites_screen.dart';
import 'package:stuber/features/home/home_screen.dart';
import 'package:stuber/features/profile/profile_screen.dart';
import 'package:stuber/features/search/search_screen.dart';
import 'package:stuber/common/widgets/navigation/bottom_nav_bar.dart';
import 'package:stuber/pages/map_page.dart'; // map  page
import 'package:stuber/features/ride_flow/presentation/screens/ride_map_screen.dart';
import 'package:stuber/features/ride_request/presentation/widget/bottom_sheet.dart';
import 'package:stuber/features/ride_flow/presentation/screens/ride_map_screen.dart';

class MainLayout extends StatefulWidget {
  const MainLayout({Key? key}) : super(key: key);

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _selectedIndex = 0;
  
  // Define your main screens here
  static final List<Widget> _screens = [
    // const HomeScreen(),
    // const MapPage(),
    const RideShareScreen(),
    // const RideMapScreen(),
    // const SearchScreen(),
    const MapPage(),
    // const FavoritesScreen(),
    const ProfileScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: AppBottomNavigationBar(
        selectedIndex: _selectedIndex,
        onItemSelected: _onItemTapped,
      ),
    );
  }
}