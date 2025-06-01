import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

// Models
class SearchSuggestion {
  final String id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final String type; // poi, address, place
  final String? category;

  SearchSuggestion({
    required this.id,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.type,
    this.category,
  });

  factory SearchSuggestion.fromJson(Map<String, dynamic> json) {
    // For Search Box API, coordinates might be in different places
    double latitude = 0.0;
    double longitude = 0.0;
    
    // Try to extract coordinates from various possible locations
    if (json['geometry'] != null && json['geometry']['coordinates'] != null) {
      final coordinates = json['geometry']['coordinates'];
      if (coordinates is List && coordinates.length >= 2) {
        longitude = (coordinates[0] as num).toDouble();
        latitude = (coordinates[1] as num).toDouble();
      }
    } else if (json['center'] != null) {
      final center = json['center'];
      if (center is List && center.length >= 2) {
        longitude = (center[0] as num).toDouble();
        latitude = (center[1] as num).toDouble();
      }
    }
    
    // Extract name - the API response shows 'name' is directly in the json
    String name = json['name']?.toString() ?? 'Unknown Location';
    
    // Extract address - API shows 'full_address' and 'place_formatted'
    String address = json['full_address']?.toString() ?? 
                     json['place_formatted']?.toString() ?? 
                     json['address']?.toString() ?? 
                     'Address not available';
    
    // Extract ID - API shows 'mapbox_id'
    String id = json['mapbox_id']?.toString() ?? 
                json['id']?.toString() ?? 
                '';
    
    // Extract type - API shows 'feature_type'
    String type = json['feature_type']?.toString() ?? 'address';
    
    // Extract category from poi_category
    String? category;
    if (json['poi_category'] != null && json['poi_category'] is List) {
      final categories = json['poi_category'] as List;
      if (categories.isNotEmpty) {
        category = categories.first.toString();
      }
    }
    
    print('Parsed suggestion: $name, ID: $id, Coordinates: ($latitude, $longitude)'); // Debug log
    
    return SearchSuggestion(
      id: id,
      name: name,
      address: address,
      latitude: latitude,
      longitude: longitude,
      type: type,
      category: category,
    );
  }
}

class LocationDetails {
  final String id;
  final String name;
  final String fullAddress;
  final double latitude;
  final double longitude;
  final String? phoneNumber;
  final String? website;
  final Map<String, dynamic>? openingHours;

  LocationDetails({
    required this.id,
    required this.name,
    required this.fullAddress,
    required this.latitude,
    required this.longitude,
    this.phoneNumber,
    this.website,
    this.openingHours,
  });

  factory LocationDetails.fromJson(Map<String, dynamic> json) {
    // For Search Box API retrieve response - follows GeoJSON Feature format
    double latitude = 0.0;
    double longitude = 0.0;
    
    // Extract coordinates from geometry.coordinates (GeoJSON format)
    if (json['geometry'] != null && json['geometry']['coordinates'] != null) {
      final coordinates = json['geometry']['coordinates'];
      if (coordinates is List && coordinates.length >= 2) {
        longitude = (coordinates[0] as num).toDouble();
        latitude = (coordinates[1] as num).toDouble();
      }
    }
    
    // Also try properties.coordinates as backup
    final properties = json['properties'] ?? {};
    if (latitude == 0.0 && longitude == 0.0 && properties['coordinates'] != null) {
      final coords = properties['coordinates'];
      if (coords['longitude'] != null && coords['latitude'] != null) {
        longitude = (coords['longitude'] as num).toDouble();
        latitude = (coords['latitude'] as num).toDouble();
      }
    }
    
    // Extract properties according to documentation
    String name = properties['name']?.toString() ?? 
                  properties['name_preferred']?.toString() ?? 
                  'Unknown Location';
    
    String fullAddress = properties['full_address']?.toString() ?? 
                         properties['place_formatted']?.toString() ?? 
                         properties['address']?.toString() ?? 
                         'Address not available';
    
    String id = properties['mapbox_id']?.toString() ?? 
                json['id']?.toString() ?? 
                '';
    
    // Contact info and other properties
    String? phoneNumber = properties['tel']?.toString() ?? 
                          properties['phone']?.toString();
    
    String? website = properties['website']?.toString();
    
    print('Parsed retrieve location: $name at ($latitude, $longitude)'); // Debug log
    
    return LocationDetails(
      id: id,
      name: name,
      fullAddress: fullAddress,
      latitude: latitude,
      longitude: longitude,
      phoneNumber: phoneNumber,
      website: website,
      openingHours: properties['opening_hours'],
    );
  }
}

// Search Service
class MapboxSearchService {
  static const String _baseUrl = 'https://api.mapbox.com/search/searchbox/v1';
  final String _accessToken;
  final Uuid _uuid = const Uuid();

  MapboxSearchService(this._accessToken);

  // Generate unique session token for each search interaction
  String generateSessionToken() {
    return _uuid.v4();
  }

  // Get search suggestions as user types
  Future<List<SearchSuggestion>> getSuggestions({
    required String query,
    required String sessionToken,
    double? latitude,
    double? longitude,
    int limit = 10,
    List<String>? types, // ['poi', 'address', 'place']
    String? country, // 'CA' for Canada
  }) async {
    if (query.trim().isEmpty) return [];

    try {
      final uri = Uri.parse('$_baseUrl/suggest').replace(queryParameters: {
        'q': query,
        'access_token': _accessToken,
        'session_token': sessionToken,
        'limit': limit.toString(),
        if (latitude != null && longitude != null) 
          'proximity': '$longitude,$latitude',
        if (types != null && types.isNotEmpty)
          'types': types.join(','),
        if (country != null)
          'country': country,
        'language': 'en', // Set language
      });

      print('Making request to: ${uri.toString()}'); // Debug log

      final response = await http.get(uri);
      print('Response status: ${response.statusCode}'); // Debug log
      print('Response body: ${response.body}'); // Debug log

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Handle different response structures
        List<dynamic> suggestionsData;
        if (data['suggestions'] != null) {
          suggestionsData = data['suggestions'] as List;
        } else if (data['features'] != null) {
          suggestionsData = data['features'] as List;
        } else {
          print('Unexpected response structure: $data');
          return [];
        }
        
        final suggestions = suggestionsData
            .map((item) {
              print('Parsing suggestion item: $item'); // Debug log
              return SearchSuggestion.fromJson(item);
            })
            .toList();
        
        print('Parsed ${suggestions.length} suggestions'); // Debug log
        for (var suggestion in suggestions) {
          print('Suggestion: ${suggestion.name} - ${suggestion.address}'); // Debug log
        }
        
        return suggestions;
      } else {
        print('API Error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to get suggestions: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting suggestions: $e');
      return [];
    }
  }

  // Get detailed information when user selects a suggestion
  Future<LocationDetails?> retrieveLocation({
    required String suggestionId,
    required String sessionToken,
  }) async {
    try {
      // Correct URL format: PUT ID IN PATH, not query parameter
      final uri = Uri.parse('$_baseUrl/retrieve/$suggestionId').replace(queryParameters: {
        'access_token': _accessToken,
        'session_token': sessionToken,
      });

      print('Retrieve request to: ${uri.toString()}'); // Debug log

      final response = await http.get(uri);
      print('Retrieve response status: ${response.statusCode}'); // Debug log
      print('Retrieve response body: ${response.body}'); // Debug log

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Based on documentation, response is a FeatureCollection
        if (data['features'] != null && (data['features'] as List).isNotEmpty) {
          final feature = data['features'][0];
          return LocationDetails.fromJson(feature);
        } else {
          print('No features found in retrieve response');
          return null;
        }
      } else {
        print('Retrieve API Error: ${response.statusCode} - ${response.body}');
        // Return null to indicate failure, we'll handle this in the widget
        return null;
      }
    } catch (e) {
      print('Error retrieving location: $e');
      return null;
    }
  }

  // Get coordinates for a location using forward geocoding as fallback
  Future<Map<String, double>?> getCoordinatesForAddress(String address) async {
    try {
      // Use the geocoding API as fallback for coordinates
      final uri = Uri.parse('https://api.mapbox.com/geocoding/v5/mapbox.places/${Uri.encodeComponent(address)}.json').replace(queryParameters: {
        'access_token': _accessToken,
        'limit': '1',
      });

      final response = await http.get(uri);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final features = data['features'] as List;
        
        if (features.isNotEmpty) {
          final coordinates = features[0]['center'];
          if (coordinates is List && coordinates.length >= 2) {
            return {
              'longitude': (coordinates[0] as num).toDouble(),
              'latitude': (coordinates[1] as num).toDouble(),
            };
          }
        }
      }
    } catch (e) {
      print('Error getting coordinates for address: $e');
    }
    return null;
  }

  // Helper method to convert SearchSuggestion to LocationDetails with coordinate lookup
  Future<LocationDetails> suggestionToLocationDetailsWithCoords(SearchSuggestion suggestion) async {
    double lat = suggestion.latitude;
    double lng = suggestion.longitude;
    
    // If coordinates are missing (0.0, 0.0), try to get them
    if (lat == 0.0 && lng == 0.0) {
      final coords = await getCoordinatesForAddress(suggestion.address);
      if (coords != null) {
        lat = coords['latitude']!;
        lng = coords['longitude']!;
        print('Got coordinates for ${suggestion.name}: ($lat, $lng)');
      }
    }
    
    return LocationDetails(
      id: suggestion.id,
      name: suggestion.name,
      fullAddress: suggestion.address,
      latitude: lat,
      longitude: lng,
      phoneNumber: null,
      website: null,
      openingHours: null,
    );
  }
}

// Search Widget
class LocationSearchWidget extends StatefulWidget {
  final String mapboxAccessToken;
  final Function(LocationDetails) onLocationSelected;
  final double? userLatitude;
  final double? userLongitude;
  final String hintText;
  final List<String>? searchTypes;

  const LocationSearchWidget({
    Key? key,
    required this.mapboxAccessToken,
    required this.onLocationSelected,
    this.userLatitude,
    this.userLongitude,
    this.hintText = 'Search for places...',
    this.searchTypes,
  }) : super(key: key);

  @override
  State<LocationSearchWidget> createState() => _LocationSearchWidgetState();
}

class _LocationSearchWidgetState extends State<LocationSearchWidget> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  late MapboxSearchService _searchService;
  
  List<SearchSuggestion> _suggestions = [];
  bool _isLoading = false;
  String? _currentSessionToken;
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _searchService = MapboxSearchService(widget.mapboxAccessToken);
    _controller.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    _debounceTimer?.cancel();
    super.dispose();
  }

  void _onSearchChanged() {
    // Cancel previous timer
    _debounceTimer?.cancel();
    
    // Start new session if query is not empty
    if (_controller.text.isNotEmpty && _currentSessionToken == null) {
      _currentSessionToken = _searchService.generateSessionToken();
    }
    
    // Clear session if query is empty
    if (_controller.text.isEmpty) {
      _currentSessionToken = null;
      setState(() {
        _suggestions.clear();
      });
      return;
    }

    // Debounce search requests
    _debounceTimer = Timer(const Duration(milliseconds: 300), () {
      _performSearch(_controller.text);
    });
  }

  Future<void> _performSearch(String query) async {
    if (query.trim().isEmpty || _currentSessionToken == null) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final suggestions = await _searchService.getSuggestions(
        query: query,
        sessionToken: _currentSessionToken!,
        latitude: widget.userLatitude,
        longitude: widget.userLongitude,
        types: widget.searchTypes,
        country: 'CA', // Set to Canada, change as needed
      );

      setState(() {
        _suggestions = suggestions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      print('Search error: $e');
    }
  }

  Future<void> _onSuggestionSelected(SearchSuggestion suggestion) async {
    if (_currentSessionToken == null) return;

    print('Selected suggestion: ${suggestion.name} with ID: ${suggestion.id}'); // Debug log

    setState(() {
      _isLoading = true;
    });

    LocationDetails? finalLocationDetails;

    try {
      // Try to get detailed information first
      final locationDetails = await _searchService.retrieveLocation(
        suggestionId: suggestion.id,
        sessionToken: _currentSessionToken!,
      );

      if (locationDetails != null) {
        finalLocationDetails = locationDetails;
        print('Got detailed location from retrieve: ${finalLocationDetails.name}');
      } else {
        // Retrieve returned null (404 error), use fallback with coordinate lookup
        print('Retrieve failed, using fallback with coordinate lookup');
        finalLocationDetails = await _searchService.suggestionToLocationDetailsWithCoords(suggestion);
      }
      
    } catch (e) {
      // Exception occurred, use fallback with coordinate lookup
      print('Retrieve threw exception, using fallback with coordinate lookup: $e');
      finalLocationDetails = await _searchService.suggestionToLocationDetailsWithCoords(suggestion);
    }

    setState(() {
      _isLoading = false;
      _suggestions.clear();
      _controller.text = suggestion.name;
    });

    // End current session
    _currentSessionToken = null;
    _focusNode.unfocus();

    print('Final location: ${finalLocationDetails.name} at ${finalLocationDetails.latitude}, ${finalLocationDetails.longitude}');
    widget.onLocationSelected(finalLocationDetails);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search Input Field
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: TextField(
            controller: _controller,
            focusNode: _focusNode,
            decoration: InputDecoration(
              hintText: widget.hintText,
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _isLoading
                  ? const Padding(
                      padding: EdgeInsets.all(12.0),
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    )
                  : _controller.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _controller.clear();
                            _focusNode.unfocus();
                          },
                        )
                      : null,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              filled: true,
              fillColor: Colors.white,
            ),
          ),
        ),
        
        // Suggestions List
        if (_suggestions.isNotEmpty)
          Container(
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _suggestions.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final suggestion = _suggestions[index];
                return ListTile(
                  leading: Icon(
                    _getIconForType(suggestion.type),
                    color: Colors.blue,
                  ),
                  title: Text(
                    suggestion.name,
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  subtitle: Text(
                    suggestion.address,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  onTap: () => _onSuggestionSelected(suggestion),
                );
              },
            ),
          ),
      ],
    );
  }

  IconData _getIconForType(String type) {
    switch (type.toLowerCase()) {
      case 'poi':
        return Icons.place;
      case 'address':
        return Icons.home;
      case 'place':
        return Icons.location_city;
      default:
        return Icons.location_on;
    }
  }
}

// Example Usage Screen
class RideBookingScreen extends StatefulWidget {
  @override
  State<RideBookingScreen> createState() => _RideBookingScreenState();
}

class _RideBookingScreenState extends State<RideBookingScreen> {
  static const String MAPBOX_ACCESS_TOKEN = 'YOUR_MAPBOX_ACCESS_TOKEN_HERE';
  
  LocationDetails? _pickupLocation;
  LocationDetails? _destinationLocation;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Book a Ride'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Pickup Location Search
            _buildLocationCard(
              title: 'Pickup Location',
              location: _pickupLocation,
              child: LocationSearchWidget(
                mapboxAccessToken: MAPBOX_ACCESS_TOKEN,
                hintText: 'Enter pickup location...',
                onLocationSelected: (location) {
                  setState(() {
                    _pickupLocation = location;
                  });
                },
                // You can get user's current location and pass here
                // userLatitude: currentLat,
                // userLongitude: currentLng,
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Destination Location Search
            _buildLocationCard(
              title: 'Destination',
              location: _destinationLocation,
              child: LocationSearchWidget(
                mapboxAccessToken: MAPBOX_ACCESS_TOKEN,
                hintText: 'Where to?',
                onLocationSelected: (location) {
                  setState(() {
                    _destinationLocation = location;
                  });
                },
                // Include POIs, addresses, and places
                searchTypes: ['poi', 'address', 'place'],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Book Ride Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _pickupLocation != null && _destinationLocation != null
                    ? _bookRide
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Book Ride',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationCard({
    required String title,
    required LocationDetails? location,
    required Widget child,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            const SizedBox(height: 12),
            child,
            if (location != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        location.fullAddress,
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _bookRide() {
    // Implement ride booking logic
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ride Booked!'),
        content: Text(
          'From: ${_pickupLocation!.name}\n'
          'To: ${_destinationLocation!.name}\n\n'
          'A driver will be assigned shortly.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}