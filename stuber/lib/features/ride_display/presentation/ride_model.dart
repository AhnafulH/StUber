class Ride {
  final String id;
  final String startLocation;
  final String destination;
  final int numberOfPassengers;
  final DateTime dateTime;
  final String status; // e.g., 'pending', 'confirmed', 'completed'

  Ride({
    required this.id,
    required this.startLocation,
    required this.destination,
    required this.numberOfPassengers,
    required this.dateTime,
    this.status = 'pending',
  });
}