import 'dart:async';
import 'package:flutter/material.dart';
import 'package:stuber/features/location_search_autocomplete/search_autocomplete.dart';

class LocationSuggestionsWidget extends StatefulWidget {
  final String mapboxAccessToken;
  final Function(LocationDetails) onLocationSelected;
  final TextEditingController controller;
  final double? userLatitude;
  final double? userLongitude;
  final List<String>? searchTypes;

  const LocationSuggestionsWidget({
    Key? key,
    required this.mapboxAccessToken,
    required this.onLocationSelected,
    required this.controller,
    this.userLatitude,
    this.userLongitude,
    this.searchTypes,
  }) : super(key: key);

  @override
  State<LocationSuggestionsWidget> createState() => _LocationSuggestionsWidgetState();
}

class _LocationSuggestionsWidgetState extends State<LocationSuggestionsWidget> {
  late MapboxSearchService _searchService;
  
  List<SearchSuggestion> _suggestions = [];
  bool _isLoading = false;
  String? _currentSessionToken;
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _searchService = MapboxSearchService(widget.mapboxAccessToken);
    widget.controller.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onSearchChanged);
    _debounceTimer?.cancel();
    super.dispose();
  }

  void _onSearchChanged() {
    _debounceTimer?.cancel();
    
    if (widget.controller.text.isNotEmpty && _currentSessionToken == null) {
      _currentSessionToken = _searchService.generateSessionToken();
    }
    
    if (widget.controller.text.isEmpty) {
      _currentSessionToken = null;
      setState(() {
        _suggestions.clear();
      });
      return;
    }

    _debounceTimer = Timer(const Duration(milliseconds: 300), () {
      _performSearch(widget.controller.text);
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
        country: 'CA',
      );

      setState(() {
        _suggestions = suggestions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _onSuggestionSelected(SearchSuggestion suggestion) async {
    if (_currentSessionToken == null) return;

    setState(() {
      _isLoading = true;
    });

    LocationDetails? finalLocationDetails;

    try {
      final locationDetails = await _searchService.retrieveLocation(
        suggestionId: suggestion.id,
        sessionToken: _currentSessionToken!,
      );

      if (locationDetails != null) {
        finalLocationDetails = locationDetails;
      } else {
        finalLocationDetails = await _searchService.suggestionToLocationDetailsWithCoords(suggestion);
      }
      
    } catch (e) {
      finalLocationDetails = await _searchService.suggestionToLocationDetailsWithCoords(suggestion);
    }

    setState(() {
      _isLoading = false;
      _suggestions.clear();
      widget.controller.text = suggestion.name;
    });

    _currentSessionToken = null;
    widget.onLocationSelected(finalLocationDetails);
  }

  @override
  Widget build(BuildContext context) {
    // Only return suggestions dropdown - NO input field
    if (_suggestions.isEmpty) return const SizedBox.shrink();
    
    return Container(
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
        padding: EdgeInsets.zero,
        itemCount: _suggestions.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final suggestion = _suggestions[index];
          return ListTile(
            leading: Icon(
              _getIconForType(suggestion.type),
              color: Colors.blue,
              size: 18,
            ),
            title: Text(
              suggestion.name,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 14,
              ),
            ),
            subtitle: Text(
              suggestion.address,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            dense: true,
            onTap: () => _onSuggestionSelected(suggestion),
          );
        },
      ),
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