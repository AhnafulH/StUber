import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:stuber/features/ride_display/presentation/ride_model.dart';

class RideCard extends StatelessWidget {
  final RideItem rideItem;
  final VoidCallback? onTap;

  const RideCard({
    Key? key,
    required this.rideItem,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with ride type and ID
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_getRideTypeLabel(rideItem.rideType)} #${rideItem.id}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey,
                    ),
                  ),
                  // Ride type badge
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getRideTypeColor(rideItem.rideType),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getRideTypeIcon(rideItem.rideType),
                          size: 14,
                          color: Colors.white,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _getRideTypeLabel(rideItem.rideType).toUpperCase(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              // Route information
              Row(
                children: [
                  Column(
                    children: [
                      Container(
                        width: 12,
                        height: 12,
                        decoration: const BoxDecoration(
                          color: Colors.green,
                          shape: BoxShape.circle,
                        ),
                      ),
                      Container(
                        width: 2,
                        height: 30,
                        color: Colors.grey.shade300,
                      ),
                      Container(
                        width: 12,
                        height: 12,
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          rideItem.startLocation,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 20),
                        Text(
                          rideItem.endDestination,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Date, time, and seats info
              Row(
                children: [
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.calendar_today,
                      label: 'Date',
                      value: rideItem.departureDatetime != null
                          ? DateFormat('MMM dd, yyyy').format(rideItem.departureDatetime!)
                          : 'Not set',
                    ),
                  ),
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.access_time,
                      label: 'Time',
                      value: rideItem.departureDatetime != null
                          ? DateFormat('hh:mm a').format(rideItem.departureDatetime!)
                          : 'Not set',
                    ),
                  ),
                  Expanded(
                    child: _InfoItem(
                      icon: _getSeatsIcon(rideItem.rideType),
                      label: _getSeatsLabel(rideItem),
                      value: '${_getSeatsValue(rideItem)}',
                    ),
                  ),
                ],
              ),
              
              // Additional info for Ride Offers
              if (rideItem.rideType == RideType.offer) ...[
                const SizedBox(height: 12),
                _buildOfferSpecificInfo(),
              ],
              
              // User info if available
              if (rideItem.profile != null) ...[
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),
                Row(
                  children: [
                    CircleAvatar(
                      radius: 16,
                      backgroundColor: _getRideTypeColor(rideItem.rideType).withOpacity(0.2),
                      child: Text(
                        rideItem.profile!.fullName?.isNotEmpty == true
                            ? rideItem.profile!.fullName![0].toUpperCase()
                            : '?',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: _getRideTypeColor(rideItem.rideType),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            rideItem.profile!.fullName ?? 'Unknown User',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: _getUserTypeColor(rideItem.profile!.userType),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  rideItem.profile!.userType,
                                  style: const TextStyle(
                                    fontSize: 10,
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                              if (rideItem.profile!.phone != null) ...[
                                const SizedBox(width: 8),
                                Text(
                                  rideItem.profile!.phone!,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOfferSpecificInfo() {
    if (rideItem is RideOffer) {
      final offer = rideItem as RideOffer;
      if (offer.maxDetourDistance != null) {
        return Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: Colors.blue.shade200),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.route,
                size: 16,
                color: Colors.blue.shade700,
              ),
              const SizedBox(width: 6),
              Text(
                'Max detour: ${offer.maxDetourDistance!.toStringAsFixed(1)} km',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue.shade700,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        );
      }
    }
    return const SizedBox.shrink();
  }

  String _getRideTypeLabel(RideType type) {
    switch (type) {
      case RideType.request:
        return 'Request';
      case RideType.offer:
        return 'Offer';
    }
  }

  Color _getRideTypeColor(RideType type) {
    switch (type) {
      case RideType.request:
        return Colors.orange;
      case RideType.offer:
        return Colors.green;
    }
  }

  IconData _getRideTypeIcon(RideType type) {
    switch (type) {
      case RideType.request:
        return Icons.search;
      case RideType.offer:
        return Icons.local_offer;
    }
  }

  IconData _getSeatsIcon(RideType type) {
    switch (type) {
      case RideType.request:
        return Icons.person_add;
      case RideType.offer:
        return Icons.airline_seat_recline_normal;
    }
  }

  String _getSeatsLabel(RideItem rideItem) {
    if (rideItem is RideRequest) {
      return 'Needed';
    } else if (rideItem is RideOffer) {
      return 'Available';
    }
    return 'Seats';
  }

  int _getSeatsValue(RideItem rideItem) {
    if (rideItem is RideRequest) {
      return rideItem.numberOfSeats;
    } else if (rideItem is RideOffer) {
      return rideItem.numberOfSeats;
    }
    return 1;
  }

  Color _getUserTypeColor(String userType) {
    switch (userType.toLowerCase()) {
      case 'rider':
        return Colors.blue;
      case 'driver':
        return Colors.green;
      case 'admin':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }
}

class _InfoItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoItem({
    Key? key,
    required this.icon,
    required this.label,
    required this.value,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(
          icon,
          size: 20,
          color: Colors.grey.shade600,
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}