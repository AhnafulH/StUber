import 'package:flutter/material.dart';
// cype
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Material 3 Bottom Navigation',
      theme: ThemeData(
        useMaterial3: true, // Enable Material 3
        colorSchemeSeed: Colors.blue, // Sets the base color for the theme
        brightness: Brightness.light,
      ),
      darkTheme: ThemeData(
        useMaterial3: true, // Enable Material 3
        colorSchemeSeed: Colors.blue,
        brightness: Brightness.dark,
      ),
      themeMode: ThemeMode.system, // Respect system theme
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;
  
  // Pages to display based on the selected index
  static final List<Widget> _pages = [
    const Center(child: Text('Home', style: TextStyle(fontSize: 24))),
    const Center(child: Text('Search', style: TextStyle(fontSize: 24))),
    const Center(child: Text('Favorites', style: TextStyle(fontSize: 24))),
    const Center(child: Text('Profile', style: TextStyle(fontSize: 24))),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Material 3 Navigation Bar'),
        centerTitle: true,
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        onDestinationSelected: _onItemTapped,
        selectedIndex: _selectedIndex,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.search_outlined),
            selectedIcon: Icon(Icons.search),
            label: 'Search',
          ),
          NavigationDestination(
            icon: Icon(Icons.favorite_outline),
            selectedIcon: Icon(Icons.favorite),
            label: 'Favorites',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}