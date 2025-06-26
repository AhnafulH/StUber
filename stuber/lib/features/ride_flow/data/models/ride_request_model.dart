/**
 * Related files: repositories/ride_repository.dart
 * services/ride_service.dart
 * model/ride_request_model.dart
 * 
 * data structure on how ride request should be
 */

class RideRequest {
  final int? id;
  final String startingLocation;
  final double? startingLatitude;
  final double? startingLongitude;
  final String destination;
  final double? destinationLatitude;
  final double? destinationLongitude;
  final int seatsNeeded;
  final DateTime departureDateTime;
  // final String status;
  // final String? notes;
  final DateTime? createdAt;

  const RideRequest({
    this.id,
    required this.startingLocation,
    this.startingLatitude,
    this.startingLongitude,
    required this.destination,
    this.destinationLatitude,
    this.destinationLongitude,
    required this.seatsNeeded,
    required this.departureDateTime,
    // this.status = 'pending',
    // this.notes,
    this.createdAt,
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
      'seats_needed': seatsNeeded,
      'departure_datetime': departureDateTime.toIso8601String(),
      // 'status': status,
      // 'notes': notes,
    };
  }

  // Create from JSON (from Supabase)
  factory RideRequest.fromJson(Map<String, dynamic> json) {
    return RideRequest(
      id: json['id'],
      startingLocation: json['starting_location'],
      startingLatitude: json['starting_latitude']?.toDouble(),
      startingLongitude: json['starting_longitude']?.toDouble(),
      destination: json['destination'],
      destinationLatitude: json['destination_latitude']?.toDouble(),
      destinationLongitude: json['destination_longitude']?.toDouble(),
      seatsNeeded: json['seats_needed'],
      departureDateTime: DateTime.parse(json['departure_datetime']),
      // status: json['status'] ?? 'pending',
      // notes: json['notes'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
    );
  }

  @override
  String toString() {
    return 'RideRequest(from: $startingLocation, to: $destination, seats: $seatsNeeded, departure: $departureDateTime)';
  }
}