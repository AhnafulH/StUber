import 'package:flutter/material.dart';
import 'package:stuber/features/ride_display/presentation/ride_model.dart';
import 'package:stuber/features/ride_display/presentation/ride_card.dart';

class RideList extends StatelessWidget {
  const RideList({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Sample data - replace with your actual data source
    final List<Ride> rides = [
      Ride(
        id: 'ride001',
        startLocation: '123 Main St, Downtown',
        destination: 'Airport Terminal 2',
        numberOfPassengers: 2,
        dateTime: DateTime.now().add(const Duration(hours: 2)),
        status: 'confirmed',
        driver: Driver(
          id: 'driver001',
          name: 'John Smith',
          phoneNumber: '+1234567890',
          profileImage: '', // Empty for demo - will show icon
          rating: 4.8,
        ),
        car: Car(
          id: 'car001',
          make: 'Toyota',
          model: 'Camry',
          color: 'Silver',
          licensePlate: 'ABC-1234',
          year: 2022,
        ),
        passengers: [
          Passenger(
            id: 'passenger001',
            name: 'Sarah Johnson',
            phoneNumber: '+1234567891',
          ),
        ],
      ),
      Ride(
        id: 'ride002',
        startLocation: 'Central Park',
        destination: '456 Oak Avenue, Uptown',
        numberOfPassengers: 3,
        dateTime: DateTime.now().add(const Duration(days: 1)),
        status: 'pending',
        driver: Driver(
          id: 'driver002',
          name: 'Emily Davis',
          phoneNumber: '+1234567892',
          profileImage: '', // Empty for demo
          rating: 4.9,
        ),
        car: Car(
          id: 'car002',
          make: 'Honda',
          model: 'Civic',
          color: 'Blue',
          licensePlate: 'XYZ-5678',
          year: 2021,
        ),
        passengers: [
          Passenger(
            id: 'passenger002',
            name: 'Mike Wilson',
            phoneNumber: '+1234567893',
          ),
          Passenger(
            id: 'passenger003',
            name: 'Lisa Brown',
            phoneNumber: '+1234567894',
          ),
        ],
      ),
      Ride(
        id: 'ride003',
        startLocation: 'Shopping Mall',
        destination: 'University Campus',
        numberOfPassengers: 1,
        dateTime: DateTime.now().subtract(const Duration(days: 1)),
        status: 'completed',
        driver: Driver(
          id: 'driver003',
          name: 'Robert Lee',
          phoneNumber: '+1234567895',
          profileImage: '', // Empty for demo
          rating: 4.7,
        ),
        car: Car(
          id: 'car003',
          make: 'Nissan',
          model: 'Altima',
          color: 'Black',
          licensePlate: 'DEF-9012',
          year: 2023,
        ),
        passengers: [],
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Rides'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: rides.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.directions_car,
                    size: 64,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'No rides found',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Book your first ride to get started!',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: rides.length,
              itemBuilder: (context, index) {
                return RideCard(
                  ride: rides[index],
                  onTap: () {
                    // Navigate to ride details or show more options
                    _showRideOptions(context, rides[index]);
                  },
                );
              },
            ),
    );
  }

  void _showRideOptions(BuildContext context, Ride ride) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'Ride Options',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.info),
              title: const Text('View Details'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to detailed view
              },
            ),
            ListTile(
              leading: const Icon(Icons.edit),
              title: const Text('Edit Ride'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to edit form
              },
            ),
            if (ride.driver != null) ...[
              ListTile(
                leading: const Icon(Icons.message),
                title: const Text('Message Driver'),
                onTap: () {
                  Navigator.pop(context);
                  // Open messaging
                },
              ),
            ],
            ListTile(
              leading: const Icon(Icons.cancel),
              title: const Text('Cancel Ride'),
              textColor: Colors.red,
              iconColor: Colors.red,
              onTap: () {
                Navigator.pop(context);
                // Show confirmation dialog
              },
            ),
          ],
        ),
      ),
    );
  }
}