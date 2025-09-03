class RideOfferCreate {
  final String startingLocation;
  final String destination;
  final int seatsAvailable;
  final double startingLatitude;
  final double startingLongitude;
  final double destinationLatitude;
  final double destinationLongitude;
  final DateTime departureDateTime;
  final double maxDetourDistance;

  RideOfferCreate({
    required this.startingLocation,
    required this.destination,
    required this.seatsAvailable,
    required this.startingLatitude,
    required this.startingLongitude,
    required this.destinationLatitude,
    required this.destinationLongitude,
    required this.departureDateTime,
    required this.maxDetourDistance,
  });

  Map<String, dynamic> toJson() {
    return {
      'starting_location': startingLocation,
      'destination': destination,
      'seats_available': seatsAvailable,
      'starting_latitude': startingLatitude,
      'starting_longitude': startingLongitude,
      'destination_latitude': destinationLatitude,
      'destination_longitude': destinationLongitude,
      'departure_datetime': departureDateTime.toIso8601String(),
      'max_detour_distance': maxDetourDistance,
    };
  }
}

class RideOfferResponse {
  final int id;
  final String startingLocation;
  final String destination;
  final int seatsAvailable;
  final double startingLatitude;
  final double startingLongitude;
  final double destinationLatitude;
  final double destinationLongitude;
  final DateTime departureDateTime;
  final double maxDetourDistance;
  final DateTime? createdAt;

  RideOfferResponse({
    required this.id,
    required this.startingLocation,
    required this.destination,
    required this.seatsAvailable,
    required this.startingLatitude,
    required this.startingLongitude,
    required this.destinationLatitude,
    required this.destinationLongitude,
    required this.departureDateTime,
    required this.maxDetourDistance,
    this.createdAt,
  });

  factory RideOfferResponse.fromJson(Map<String, dynamic> json) {
    return RideOfferResponse(
      id: json['id'],
      startingLocation: json['starting_location'],
      destination: json['destination'],
      seatsAvailable: json['seats_available'],
      startingLatitude: json['starting_latitude'].toDouble(),
      startingLongitude: json['starting_longitude'].toDouble(),
      destinationLatitude: json['destination_latitude'].toDouble(),
      destinationLongitude: json['destination_longitude'].toDouble(),
      departureDateTime: DateTime.parse(json['departure_datetime']),
      maxDetourDistance: json['max_detour_distance'].toDouble(),
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }
}
