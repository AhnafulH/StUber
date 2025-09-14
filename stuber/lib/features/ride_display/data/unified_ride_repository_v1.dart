import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:stuber/features/ride_display/presentation/ride_model.dart';

class UnifiedRideRepository {
  final _client = Supabase.instance.client;

  // Get all rides (both requests and offers) for the current user
  Future<List<RideItem>> getUserRides() async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      // Fetch ride requests and offers concurrently
      final futures = await Future.wait([
        _getUserRideRequests(userId),
        _getUserRideOffers(userId),
      ]);

      final List<RideItem> allRides = [
        ...futures[0], // ride requests
        ...futures[1], // ride offers
      ];

      // Sort by departure time (most recent first)
      allRides.sort((a, b) {
        final aTime = a.departureDatetime ?? DateTime.now();
        final bTime = b.departureDatetime ?? DateTime.now();
        return bTime.compareTo(aTime);
      });

      return allRides;
    } catch (e) {
      throw Exception('Failed to fetch user rides: $e');
    }
  }

  // Get all available rides (for browsing)
  Future<List<RideItem>> getAllAvailableRides() async {
    try {
      // Fetch all ride requests and offers concurrently
      final futures = await Future.wait([
        _getAllRideRequests(),
        _getAllRideOffers(),
      ]);

      final List<RideItem> allRides = [
        ...futures[0], // ride requests
        ...futures[1], // ride offers
      ];

      // Sort by departure time (upcoming rides first)
      allRides.sort((a, b) {
        final aTime = a.departureDatetime ?? DateTime.now();
        final bTime = b.departureDatetime ?? DateTime.now();
        return aTime.compareTo(bTime);
      });

      return allRides;
    } catch (e) {
      throw Exception('Failed to fetch available rides: $e');
    }
  }

  // Get rides by type
  Future<List<RideItem>> getRidesByType(RideType rideType) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      switch (rideType) {
        case RideType.request:
          return await _getUserRideRequests(userId);
        case RideType.offer:
          return await _getUserRideOffers(userId);
      }
    } catch (e) {
      throw Exception('Failed to fetch rides by type: $e');
    }
  }

  // Private methods for fetching specific types

  Future<List<RideRequest>> _getUserRideRequests(String userId) async {
    final response = await _client
        .from('Ride_Request')
        .select('''
          *,
          profiles(*)
        ''')
        .eq('uuid', userId)
        .order('departure_datetime', ascending: false);

    return response.map<RideRequest>((json) => RideRequest.fromJson(json)).toList();
  }

  Future<List<RideOffer>> _getUserRideOffers(String userId) async {
    final response = await _client
        .from('Ride_Offer')
        .select('''
          *,
          profiles(*)
        ''')
        .eq('uuid', userId)
        .order('departure_datetime', ascending: false);

    return response.map<RideOffer>((json) => RideOffer.fromJson(json)).toList();
  }

  Future<List<RideRequest>> _getAllRideRequests() async {
    final response = await _client
        .from('Ride_Request')
        .select('''
          *,
          profiles(*)
        ''')
        .gte('departure_datetime', DateTime.now().toIso8601String())
        .order('departure_datetime', ascending: true);

    return response.map<RideRequest>((json) => RideRequest.fromJson(json)).toList();
  }

  Future<List<RideOffer>> _getAllRideOffers() async {
    final response = await _client
        .from('Ride_Offer')
        .select('''
          *,
          profiles(*)
        ''')
        .gte('departure_datetime', DateTime.now().toIso8601String())
        .order('departure_datetime', ascending: true);

    return response.map<RideOffer>((json) => RideOffer.fromJson(json)).toList();
  }

  // CRUD operations for Ride Requests

  Future<RideRequest> createRideRequest({
    required String startingLocation,
    required String destination,
    required int seatsNeeded,
    required DateTime departureDatetime,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
    Map<String, dynamic>? routeGeometry,
  }) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final response = await _client.from('Ride_Request').insert({
        'starting_location': startingLocation,
        'destination': destination,
        'seats_needed': seatsNeeded,
        'departure_datetime': departureDatetime.toIso8601String(),
        'starting_latitude': startingLatitude,
        'starting_longitude': startingLongitude,
        'destination_latitude': destinationLatitude,
        'destination_longitude': destinationLongitude,
        'route_geometry': routeGeometry,
        'uuid': userId,
      }).select('''
        *,
        profiles(*)
      ''').single();

      return RideRequest.fromJson(response);
    } catch (e) {
      throw Exception('Failed to create ride request: $e');
    }
  }

  // CRUD operations for Ride Offers

  Future<RideOffer> createRideOffer({
    required String startingLocation,
    required String destination,
    required int seatsAvailable,
    required DateTime departureDatetime,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
    double? maxDetourDistance,
    Map<String, dynamic>? routeGeometry,
  }) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final response = await _client.from('Ride_Offer').insert({
        'starting_location': startingLocation,
        'destination': destination,
        'seats_available': seatsAvailable,
        'departure_datetime': departureDatetime.toIso8601String(),
        'starting_latitude': startingLatitude,
        'starting_longitude': startingLongitude,
        'destination_latitude': destinationLatitude,
        'destination_longitude': destinationLongitude,
        'max_detour_distance': maxDetourDistance,
        'route_geometry': routeGeometry,
        'uuid': userId,
      }).select('''
        *,
        profiles(*)
      ''').single();

      return RideOffer.fromJson(response);
    } catch (e) {
      throw Exception('Failed to create ride offer: $e');
    }
  }

  // Update operations

  Future<RideRequest> updateRideRequest({
    required int rideId,
    String? startingLocation,
    String? destination,
    int? seatsNeeded,
    DateTime? departureDatetime,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
    Map<String, dynamic>? routeGeometry,
  }) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final updateData = <String, dynamic>{};
      if (startingLocation != null) updateData['starting_location'] = startingLocation;
      if (destination != null) updateData['destination'] = destination;
      if (seatsNeeded != null) updateData['seats_needed'] = seatsNeeded;
      if (departureDatetime != null) updateData['departure_datetime'] = departureDatetime.toIso8601String();
      if (startingLatitude != null) updateData['starting_latitude'] = startingLatitude;
      if (startingLongitude != null) updateData['starting_longitude'] = startingLongitude;
      if (destinationLatitude != null) updateData['destination_latitude'] = destinationLatitude;
      if (destinationLongitude != null) updateData['destination_longitude'] = destinationLongitude;
      if (routeGeometry != null) updateData['route_geometry'] = routeGeometry;

      final response = await _client
          .from('Ride_Request')
          .update(updateData)
          .eq('id', rideId)
          .eq('uuid', userId)
          .select('''
            *,
            profiles(*)
          ''')
          .single();

      return RideRequest.fromJson(response);
    } catch (e) {
      throw Exception('Failed to update ride request: $e');
    }
  }

  Future<RideOffer> updateRideOffer({
    required int rideId,
    String? startingLocation,
    String? destination,
    int? seatsAvailable,
    DateTime? departureDatetime,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
    double? maxDetourDistance,
    Map<String, dynamic>? routeGeometry,
  }) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final updateData = <String, dynamic>{};
      if (startingLocation != null) updateData['starting_location'] = startingLocation;
      if (destination != null) updateData['destination'] = destination;
      if (seatsAvailable != null) updateData['seats_available'] = seatsAvailable;
      if (departureDatetime != null) updateData['departure_datetime'] = departureDatetime.toIso8601String();
      if (startingLatitude != null) updateData['starting_latitude'] = startingLatitude;
      if (startingLongitude != null) updateData['starting_longitude'] = startingLongitude;
      if (destinationLatitude != null) updateData['destination_latitude'] = destinationLatitude;
      if (destinationLongitude != null) updateData['destination_longitude'] = destinationLongitude;
      if (maxDetourDistance != null) updateData['max_detour_distance'] = maxDetourDistance;
      if (routeGeometry != null) updateData['route_geometry'] = routeGeometry;

      final response = await _client
          .from('Ride_Offer')
          .update(updateData)
          .eq('id', rideId)
          .eq('uuid', userId)
          .select('''
            *,
            profiles(*)
          ''')
          .single();

      return RideOffer.fromJson(response);
    } catch (e) {
      throw Exception('Failed to update ride offer: $e');
    }
  }

  // Delete operations

  Future<void> deleteRideRequest(int rideId) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      await _client.from('Ride_Request').delete()
          .eq('id', rideId)
          .eq('uuid', userId);
    } catch (e) {
      throw Exception('Failed to delete ride request: $e');
    }
  }

  Future<void> deleteRideOffer(int rideId) async {
    try {
      final userId = _client.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      await _client.from('Ride_Offer').delete()
          .eq('id', rideId)
          .eq('uuid', userId);
    } catch (e) {
      throw Exception('Failed to delete ride offer: $e');
    }
  }

  // Delete unified method
  Future<void> deleteRide(RideItem ride) async {
    switch (ride.rideType) {
      case RideType.request:
        await deleteRideRequest(ride.id);
        break;
      case RideType.offer:
        await deleteRideOffer(ride.id);
        break;
    }
  }

  // Search functionality
  Future<List<RideItem>> searchRides({
    String? startingLocation,
    String? destination,
    DateTime? fromDate,
    DateTime? toDate,
    RideType? rideType,
  }) async {
    try {
      List<Future<List<RideItem>>> futures = [];

      if (rideType == null || rideType == RideType.request) {
        futures.add(_searchRideRequests(startingLocation, destination, fromDate, toDate));
      }
      if (rideType == null || rideType == RideType.offer) {
        futures.add(_searchRideOffers(startingLocation, destination, fromDate, toDate));
      }

      final results = await Future.wait(futures);
      final List<RideItem> allRides = results.expand((list) => list).toList();

      // Sort by departure time
      allRides.sort((a, b) {
        final aTime = a.departureDatetime ?? DateTime.now();
        final bTime = b.departureDatetime ?? DateTime.now();
        return aTime.compareTo(bTime);
      });

      return allRides;
    } catch (e) {
      throw Exception('Failed to search rides: $e');
    }
  }

  Future<List<RideItem>> _searchRideRequests(String? startingLocation, String? destination, DateTime? fromDate, DateTime? toDate) async {
    var query = _client.from('Ride_Request').select('''
      *,
      profiles(*)
    ''');

    if (startingLocation != null && startingLocation.isNotEmpty) {
      query = query.ilike('starting_location', '%$startingLocation%');
    }
    if (destination != null && destination.isNotEmpty) {
      query = query.ilike('destination', '%$destination%');
    }
    if (fromDate != null) {
      query = query.gte('departure_datetime', fromDate.toIso8601String());
    }
    if (toDate != null) {
      query = query.lte('departure_datetime', toDate.toIso8601String());
    }

    final response = await query.order('departure_datetime', ascending: true);
    return response.map<RideItem>((json) => RideRequest.fromJson(json)).toList();
  }

  Future<List<RideItem>> _searchRideOffers(String? startingLocation, String? destination, DateTime? fromDate, DateTime? toDate) async {
    var query = _client.from('Ride_Offer').select('''
      *,
      profiles(*)
    ''');

    if (startingLocation != null && startingLocation.isNotEmpty) {
      query = query.ilike('starting_location', '%$startingLocation%');
    }
    if (destination != null && destination.isNotEmpty) {
      query = query.ilike('destination', '%$destination%');
    }
    if (fromDate != null) {
      query = query.gte('departure_datetime', fromDate.toIso8601String());
    }
    if (toDate != null) {
      query = query.lte('departure_datetime', toDate.toIso8601String());
    }

    final response = await query.order('departure_datetime', ascending: true);
    return response.map<RideItem>((json) => RideOffer.fromJson(json)).toList();
  }
}