// Model for creating ride requests (matches your FastAPI RideRequestCreate)

class RideRequestCreate {
  final String uuid;
  final String startingLocation;
  final String destination;
  final int seatsNeeded;
  final double startingLatitude;
  final double startingLongitude;
  final double destinationLatitude;
  final double destinationLongitude;
  final DateTime departureDateTime;
  final Map<String, dynamic>? routeGeometry;

  RideRequestCreate({
    required this.uuid,
    required this.startingLocation,
    required this.destination,
    required this.seatsNeeded,
    required this.startingLatitude,
    required this.startingLongitude,
    required this.destinationLatitude,
    required this.destinationLongitude,
    required this.departureDateTime,
    this.routeGeometry,
  });

  Map<String, dynamic> toJson() {
    return {
      'uuid': uuid,
      'starting_location': startingLocation,
      'destination': destination,
      'seats_needed': seatsNeeded,
      'starting_latitude': startingLatitude,
      'starting_longitude': startingLongitude,
      'destination_latitude': destinationLatitude,
      'destination_longitude': destinationLongitude,
      'departure_datetime': departureDateTime.toIso8601String(),
      'route_geometry': routeGeometry,
    };
  }
}

// Model for ride request response (matches your FastAPI RideRequest)
class RideRequestResponse {
  final int id;
  final String startingLocation;
  final String destination;
  final int seatsNeeded;
  final double startingLatitude;
  final double startingLongitude;
  final double destinationLatitude;
  final double destinationLongitude;
  final DateTime departureDateTime;
  final DateTime? createdAt;

  RideRequestResponse({
    required this.id,
    required this.startingLocation,
    required this.destination,
    required this.seatsNeeded,
    required this.startingLatitude,
    required this.startingLongitude,
    required this.destinationLatitude,
    required this.destinationLongitude,
    required this.departureDateTime,
    this.createdAt,
  });

  factory RideRequestResponse.fromJson(Map<String, dynamic> json) {
    return RideRequestResponse(
      id: json['id'],
      startingLocation: json['starting_location'],
      destination: json['destination'],
      seatsNeeded: json['seats_needed'],
      startingLatitude: json['starting_latitude'].toDouble(),
      startingLongitude: json['starting_longitude'].toDouble(),
      destinationLatitude: json['destination_latitude'].toDouble(),
      destinationLongitude: json['destination_longitude'].toDouble(),
      departureDateTime: DateTime.parse(json['departure_datetime']),
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
    );
  }
}