import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:stuber/features/profile/profile_screen.dart';
import 'package:stuber/common/widgets/navigation/bottom_nav_bar.dart';
import 'package:stuber/features/ride_flow/presentation/screens/ride_map_screen.dart';
import 'package:stuber/features/map/domain/location_test.dart'; //MyLocationWidget
import 'package:stuber/features/ride_display/presentation/ride_list.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class RideMatchResponse {
  final String driverName;
  final double price;

  RideMatchResponse({
    required this.driverName,
    required this.price,
  });

  factory RideMatchResponse.fromJson(Map<String, dynamic> json) {
    return RideMatchResponse(
      driverName: json['driver_name'],
      price: json['price'].toDouble(),
    );
  }
}

// Service to handle ride matches API calls
class RideMatchService {
  static const String baseUrl = 'http://10.21.71.179:8000'; // Your server IP
  
  static const Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  static Future<List<RideMatchResponse>> getRideMatches(String uuid) async {
    try {
      print('🔍 Fetching ride matches for UUID: $uuid');
      
      final response = await http.get(
        Uri.parse('$baseUrl/ride-matches?uuid=$uuid'),
        headers: headers,
      );

      print('📡 API Response Status: ${response.statusCode}');
      print('📡 API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body);
        final matches = jsonList.map((json) => RideMatchResponse.fromJson(json)).toList();
        
        print('✅ Found ${matches.length} ride matches');
        return matches;
      } else {
        print('❌ API Error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to fetch ride matches: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Network Error: $e');
      throw Exception('Error fetching ride matches: $e');
    }
  }
}



class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _selectedIndex = 0;
  List<RideMatchResponse>? _rideMatches;

  String getUserUuid() {
    final supabase = Supabase.instance.client;
    final currentSession = supabase.auth.currentSession;
    if (currentSession == null) {
      throw Exception("User must be logged in to get Ride Matches");
    }
    return currentSession.user.id;
  }
  
  // Main screens here
  static final List<Widget> _screens = [
    // const HomeScreen(),
    // const MapPage(),
    const RideShareScreen(),
    // const RideMapScreen(),
    // const SearchScreen(),
    const RideList(),
    MyLocationWidget(),
    // const LocationSearchScreen(),
    // const FavoritesScreen(),
    const ProfileScreen(),
  ];

  void _onItemTapped(int index) async {
    setState(() {
      _selectedIndex = index;
    });

    if (_selectedIndex == 1) {
      final uuid = getUserUuid();
      _rideMatches = await RideMatchService.getRideMatches(uuid); // Display the ride matches
    }
  }

  @override
  Widget build(BuildContext context) {
    print("🔍 main_layout called new");
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: AppBottomNavigationBar(
        selectedIndex: _selectedIndex,
        onItemSelected: _onItemTapped,
      ),
    );
  }
}