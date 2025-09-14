enum RideType { request, offer }

// Base interface for both ride types
abstract class RideItem {
  int get id;
  DateTime? get createdAt;
  String? get startingLocation;
  String? get destination;
  DateTime? get departureDatetime;
  String? get userUuid;
  Profile? get profile;
  RideType get rideType;
  
  // UI helper methods
  String get startLocation;
  String get endDestination;
  DateTime get dateTime;
  String get rideId;
}

class Profile {
  final String id;
  final String? fullName;
  final String? email;
  final String? phone;
  final String userType;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Profile({
    required this.id,
    this.fullName,
    this.email,
    this.phone,
    this.userType = 'rider',
    this.createdAt,
    this.updatedAt,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'] ?? '',
      fullName: json['full_name'],
      email: json['email'],
      phone: json['phone'],
      userType: json['user_type'] ?? 'rider',
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'user_type': userType,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}

class RideMatch {
  final int id;
  final int? driverId;
  final int? riderId;
  final double? price;
  final bool driverAccept;
  final bool riderAccept;
  final RideOffer? rideOffer;
  final RideRequest? rideRequest;

  RideMatch({
    required this.id,
    this.driverId,
    this.riderId,
    this.price,
    this.driverAccept = false,
    this.riderAccept = false,
    this.rideOffer,
    this.rideRequest,
  });

  factory RideMatch.fromJson(Map<String, dynamic> json) {
    return RideMatch(
      id: json['id'] ?? 0,
      driverId: json['driver_id'],
      riderId: json['rider_id'],
      price: json['price']?.toDouble(),
      driverAccept: json['driver_accept'] ?? false,
      riderAccept: json['rider_accept'] ?? false,
      rideOffer: json['Ride_Offer'] != null 
          ? RideOffer.fromJson(json['Ride_Offer'])
          : null,
      rideRequest: json['Ride_Request'] != null 
          ? RideRequest.fromJson(json['Ride_Request'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'driver_id': driverId,
      'rider_id': riderId,
      'price': price,
      'driver_accept': driverAccept,
      'rider_accept': riderAccept,
    };
  }

  // Helper getters
  bool get isBothAccepted => driverAccept && riderAccept;
  bool get isPending => !driverAccept || !riderAccept;
  String get status {
    if (isBothAccepted) return 'Confirmed';
    if (driverAccept && !riderAccept) return 'Waiting for rider';
    if (!driverAccept && riderAccept) return 'Waiting for driver';
    return 'Pending';
  }
}

class RideRequest implements RideItem {
  @override
  final int id;
  @override
  final DateTime? createdAt;
  @override
  final String? startingLocation;
  @override
  final String? destination;
  final int? seatsNeeded;
  final double? startingLatitude;
  final double? startingLongitude;
  final double? destinationLatitude;
  final double? destinationLongitude;
  @override
  final DateTime? departureDatetime;
  final Map<String, dynamic>? routeGeometry;
  @override
  final String? userUuid;
  @override
  final Profile? profile;

  @override
  RideType get rideType => RideType.request;

  RideRequest({
    required this.id,
    this.createdAt,
    this.startingLocation,
    this.destination,
    this.seatsNeeded,
    this.startingLatitude,
    this.startingLongitude,
    this.destinationLatitude,
    this.destinationLongitude,
    this.departureDatetime,
    this.routeGeometry,
    this.userUuid,
    this.profile,
  });

  factory RideRequest.fromJson(Map<String, dynamic> json) {
    return RideRequest(
      id: json['id'] ?? 0,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      startingLocation: json['starting_location'],
      destination: json['destination'],
      seatsNeeded: json['seats_needed'],
      startingLatitude: json['starting_latitude']?.toDouble(),
      startingLongitude: json['starting_longitude']?.toDouble(),
      destinationLatitude: json['destination_latitude']?.toDouble(),
      destinationLongitude: json['destination_longitude']?.toDouble(),
      departureDatetime: json['departure_datetime'] != null 
          ? DateTime.parse(json['departure_datetime']) 
          : null,
      routeGeometry: json['route_geometry'],
      userUuid: json['uuid'],
      profile: json['profiles'] != null 
          ? Profile.fromJson(json['profiles']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'created_at': createdAt?.toIso8601String(),
      'starting_location': startingLocation,
      'destination': destination,
      'seats_needed': seatsNeeded,
      'starting_latitude': startingLatitude,
      'starting_longitude': startingLongitude,
      'destination_latitude': destinationLatitude,
      'destination_longitude': destinationLongitude,
      'departure_datetime': departureDatetime?.toIso8601String(),
      'route_geometry': routeGeometry,
      'uuid': userUuid,
    };
  }

  // UI helper methods
  @override
  String get startLocation => startingLocation ?? 'Unknown location';
  @override
  String get endDestination => destination ?? 'Unknown destination';
  @override
  DateTime get dateTime => departureDatetime ?? DateTime.now();
  @override
  String get rideId => id.toString();
  
  // Request-specific getters
  int get numberOfSeats => seatsNeeded ?? 1;
  String get seatsLabel => 'Seats Needed';
}

class RideOffer implements RideItem {
  @override
  final int id;
  @override
  final DateTime? createdAt;
  @override
  final String? startingLocation;
  @override
  final String? destination;
  final int? seatsAvailable;
  final double? startingLatitude;
  final double? startingLongitude;
  final double? destinationLatitude;
  final double? destinationLongitude;
  @override
  final DateTime? departureDatetime;
  final double? maxDetourDistance;
  final Map<String, dynamic>? routeGeometry;
  @override
  final String? userUuid;
  @override
  final Profile? profile;

  @override
  RideType get rideType => RideType.offer;

  RideOffer({
    required this.id,
    this.createdAt,
    this.startingLocation,
    this.destination,
    this.seatsAvailable,
    this.startingLatitude,
    this.startingLongitude,
    this.destinationLatitude,
    this.destinationLongitude,
    this.departureDatetime,
    this.maxDetourDistance,
    this.routeGeometry,
    this.userUuid,
    this.profile,
  });

  factory RideOffer.fromJson(Map<String, dynamic> json) {
    return RideOffer(
      id: json['id'] ?? 0,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      startingLocation: json['starting_location'],
      destination: json['destination'],
      seatsAvailable: json['seats_available'],
      startingLatitude: json['starting_latitude']?.toDouble(),
      startingLongitude: json['starting_longitude']?.toDouble(),
      destinationLatitude: json['destination_latitude']?.toDouble(),
      destinationLongitude: json['destination_longitude']?.toDouble(),
      departureDatetime: json['departure_datetime'] != null 
          ? DateTime.parse(json['departure_datetime']) 
          : null,
      maxDetourDistance: json['max_detour_distance']?.toDouble(),
      routeGeometry: json['route_geometry'],
      userUuid: json['uuid'],
      profile: json['profiles'] != null 
          ? Profile.fromJson(json['profiles']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'created_at': createdAt?.toIso8601String(),
      'starting_location': startingLocation,
      'destination': destination,
      'seats_available': seatsAvailable,
      'starting_latitude': startingLatitude,
      'starting_longitude': startingLongitude,
      'destination_latitude': destinationLatitude,
      'destination_longitude': destinationLongitude,
      'departure_datetime': departureDatetime?.toIso8601String(),
      'max_detour_distance': maxDetourDistance,
      'route_geometry': routeGeometry,
      'uuid': userUuid,
    };
  }

  // UI helper methods
  @override
  String get startLocation => startingLocation ?? 'Unknown location';
  @override
  String get endDestination => destination ?? 'Unknown destination';
  @override
  DateTime get dateTime => departureDatetime ?? DateTime.now();
  @override
  String get rideId => id.toString();
  
  // Offer-specific getters
  int get numberOfSeats => seatsAvailable ?? 1;
  String get seatsLabel => 'Seats Available';
}