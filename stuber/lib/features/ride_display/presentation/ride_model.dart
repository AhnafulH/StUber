class Driver {
  final String id;
  final String name;
  final String phoneNumber;
  final String profileImage;
  final double rating;

  Driver({
    required this.id,
    required this.name,
    required this.phoneNumber,
    required this.profileImage,
    required this.rating,
  });
}

class Car {
  final String id;
  final String make;
  final String model;
  final String color;
  final String licensePlate;
  final int year;

  Car({
    required this.id,
    required this.make,
    required this.model,
    required this.color,
    required this.licensePlate,
    required this.year,
  });

  String get fullName => '$year $make $model';
}

class Passenger {
  final String id;
  final String name;
  final String phoneNumber;

  Passenger({
    required this.id,
    required this.name,
    required this.phoneNumber,
  });
}

class Ride {
  final String id;
  final String startLocation;
  final String destination;
  final int numberOfPassengers;
  final DateTime dateTime;
  final String status; // e.g., 'pending', 'confirmed', 'completed'
  final Driver? driver;
  final Car? car;
  final List<Passenger> passengers;

  Ride({
    required this.id,
    required this.startLocation,
    required this.destination,
    required this.numberOfPassengers,
    required this.dateTime,
    this.status = 'pending',
    this.driver,
    this.car,
    this.passengers = const [],
  });
}