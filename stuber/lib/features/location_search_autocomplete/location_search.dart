import 'package:flutter/material.dart';
import 'package:stuber/features/location_search_autocomplete/search_autocomplete.dart';

class LocationSearchScreen extends StatefulWidget {
  const LocationSearchScreen({Key? key}) : super(key: key);

  @override
  State<LocationSearchScreen> createState() => _LocationSearchScreenState();
}

class _LocationSearchScreenState extends State<LocationSearchScreen> {
  LocationDetails? _pickupLocation;
  LocationDetails? _destinationLocation;
  bool _showRideOptions = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Where to?'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Quick Actions
            _buildQuickActions(),
            
            const SizedBox(height: 24),
            
            // Pickup Location
            _buildLocationCard(
              title: 'Pickup Location',
              icon: Icons.radio_button_checked,
              iconColor: Colors.green,
              location: _pickupLocation,
              child: LocationSearchWidget(
                mapboxAccessToken: "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4b24zOTkwazdwMnJvaDhva3c1bmRsIn0.IoyYuI4vuqow-6P-5fQaew",
                hintText: 'Enter pickup location...',
                onLocationSelected: (location) {
                  setState(() {
                    _pickupLocation = location;
                    _checkIfReadyForRide();
                  });
                },
                searchTypes: ['address', 'poi', 'place'],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Destination Location
            _buildLocationCard(
              title: 'Destination',
              icon: Icons.location_on,
              iconColor: Colors.red,
              location: _destinationLocation,
              child: LocationSearchWidget(
                mapboxAccessToken: "pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4b24zOTkwazdwMnJvaDhva3c1bmRsIn0.IoyYuI4vuqow-6P-5fQaew",
                hintText: 'Where do you want to go?',
                onLocationSelected: (location) {
                  setState(() {
                    _destinationLocation = location;
                    _checkIfReadyForRide();
                  });
                },
                searchTypes: ['poi', 'address', 'place'],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Recent Searches
            _buildRecentSearches(),
            
            const SizedBox(height: 24),
            
            // Ride Options (shown when both locations are selected)
            if (_showRideOptions)
              _buildRideOptions(),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _buildQuickActionButton(
              icon: Icons.home,
              label: 'Home',
              onTap: () => _setQuickLocation('home'),
            ),
            const SizedBox(width: 12),
            _buildQuickActionButton(
              icon: Icons.work,
              label: 'Work',
              onTap: () => _setQuickLocation('work'),
            ),
            const SizedBox(width: 12),
            _buildQuickActionButton(
              icon: Icons.local_airport,
              label: 'Airport',
              onTap: () => _searchForCategory('airport'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              Icon(icon, color: Colors.blue, size: 24),
              const SizedBox(height: 4),
              Text(
                label,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLocationCard({
    required String title,
    required IconData icon,
    required Color iconColor,
    required LocationDetails? location,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: iconColor, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          child,
          if (location != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      location.fullAddress,
                      style: const TextStyle(fontSize: 12, color: Colors.green),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRecentSearches() {
    // Mock recent searches - replace with actual data
    final recentSearches = [
      {'name': 'Starbucks Coffee', 'address': '123 Main St, Toronto, ON'},
      {'name': 'Union Station', 'address': 'Front St W, Toronto, ON'},
      {'name': 'CN Tower', 'address': '290 Bremner Blvd, Toronto, ON'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Searches',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: recentSearches.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final search = recentSearches[index];
              return ListTile(
                leading: const Icon(Icons.history, color: Colors.grey),
                title: Text(search['name']!),
                subtitle: Text(
                  search['address']!,
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // Handle recent search selection
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildRideOptions() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Choose Your Ride',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildRideOption(
            icon: Icons.directions_car,
            title: 'StuberGo',
            subtitle: 'Affordable rides',
            price: '\$12-15',
            time: '5 min',
          ),
          const SizedBox(height: 12),
          _buildRideOption(
            icon: Icons.local_taxi,
            title: 'StuberX',
            subtitle: 'Premium comfort',
            price: '\$18-22',
            time: '8 min',
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _bookRide,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.black,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Book Ride',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRideOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required String price,
    required String time,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, size: 32, color: Colors.blue),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                price,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                time,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _setQuickLocation(String type) {
    // Handle quick location selection (home/work)
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$type location selected')),
    );
  }

  void _searchForCategory(String category) {
    // Handle category search (airport, etc.)
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Searching for $category...')),
    );
  }

  void _checkIfReadyForRide() {
    setState(() {
      _showRideOptions = _pickupLocation != null && _destinationLocation != null;
    });
  }

  void _bookRide() {
    if (_pickupLocation != null && _destinationLocation != null) {
      // Navigate to ride tracking or confirmation screen
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Booking your ride...')),
      );
    }
  }
}