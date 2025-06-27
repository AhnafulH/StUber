class RideOfferModel {
  final int? id;
  final String startingLocation;
  final double? startingLatitude;
  final double? startingLongitude;
  final String destination;
  final double? destinationLatitude;
  final double? destinationLongitude;
  final int seatsAvailable;
  final DateTime departureDateTime;
  final DateTime? createdAt;
  final int? maxDetourDistance;

  const RideOfferModel({
    this.id,
    required this.startingLocation,
    this.startingLatitude,
    this.startingLongitude,
    required this.destination,
    this.destinationLatitude,
    this.destinationLongitude,
    required this.seatsAvailable,
    required this.departureDateTime,
    this.createdAt,
    this.maxDetourDistance,
  });

  // Convert to JSON for Supabase
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'starting_location': startingLocation,
      'starting_latitude': startingLatitude,
      'starting_longitude': startingLongitude,
      'destination': destination,
      'destination_latitude': destinationLatitude,
      'destination_longitude': destinationLongitude,
      'seats_available': seatsAvailable,
      'departure_datetime': departureDateTime.toIso8601String(),
      'max_detour_distance': maxDetourDistance,
    };
  }

  // Create from JSON (from Supabase)
  factory RideOfferModel.fromJson(Map<String, dynamic> json) {
    return RideOfferModel(
      id: json['id'],
      startingLocation: json['starting_location'],
      startingLatitude: json['starting_latitude']?.toDouble(),
      startingLongitude: json['starting_longitude']?.toDouble(),
      destination: json['destination'],
      destinationLatitude: json['destination_latitude']?.toDouble(),
      destinationLongitude: json['destination_longitude']?.toDouble(),
      seatsAvailable: json['seats_available'],
      departureDateTime: DateTime.parse(json['departure_datetime']),
      maxDetourDistance: json['max_detour_distance'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
    );
  }

  @override
  String toString() {
    return 'RideOffer(from: $startingLocation, to: $destination, seats: $seatsAvailable, departure: $departureDateTime)';
  }
}