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
        status: 'pending',
      ),
      Ride(
        id: 'ride002',
        startLocation: 'Central Park',
        destination: '456 Oak Avenue, Uptown',
        numberOfPassengers: 1,
        dateTime: DateTime.now().add(const Duration(days: 1)),
        status: 'confirmed',
      ),
      Ride(
        id: 'ride003',
        startLocation: 'Shopping Mall',
        destination: 'University Campus',
        numberOfPassengers: 3,
        dateTime: DateTime.now().subtract(const Duration(days: 1)),
        status: 'completed',
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