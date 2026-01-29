# ------------------ Helpers ------------------

def row_to_dict(row):
    return dict(row) if row else None

# Cache for plant data to avoid repeated API calls
_plant_cache = {}

def convert_humidity_scale(atm_humidity):
    """Convert atmospheric_humidity (0-10 scale) to percentage range"""
    if atm_humidity is None:
        return None
    # Scale: 0 = <=10%, 10 = >=90%, roughly 8-10% per step
    # Return the midpoint of the range
    return min(10 + (atm_humidity * 8), 90)

def get_plant_by_id(plant_id):
    """Fetch plant data from Trefle API by ID"""
    if not plant_id:
        return None

    # Check cache first
    if plant_id in _plant_cache:
        return _plant_cache[plant_id]

    try:
        from backend.trefle import get_token, TREFLE_BASE
        import requests

        token = get_token()
        if not token:
            return None

        resp = requests.get(
            f'{TREFLE_BASE}/plants/{plant_id}',
            params={'token': token},
            timeout=3
        )
        if not resp.ok:
            return None

        p = resp.json().get('data', {})
        main_species = p.get('main_species', {})
        growth = main_species.get('growth', {})

        # Extract temperature ranges (using Celsius) from main_species.growth
        min_temp_obj = growth.get('minimum_temperature', {})
        max_temp_obj = growth.get('maximum_temperature', {})
        min_temp = min_temp_obj.get('deg_c') if min_temp_obj else None
        max_temp = max_temp_obj.get('deg_c') if max_temp_obj else None

        # Calculate temperature ranges only if data is available
        if min_temp is not None and max_temp is not None:
            # Calculate warning (optimal) range: 5°C buffer from critical edges
            temp_warning_min = min_temp + 5
            temp_warning_max = max_temp - 5
            # Ensure warning range makes sense
            if temp_warning_min >= temp_warning_max:
                temp_warning_min = min_temp + 2
                temp_warning_max = max_temp - 2
            temperature_ranges = {
                'warning': {'min': temp_warning_min, 'max': temp_warning_max},
                'critical': {'min': min_temp, 'max': max_temp}
            }
        else:
            temperature_ranges = None

        # Extract humidity from main_species.growth
        atm_humidity = growth.get('atmospheric_humidity')

        # Calculate humidity ranges only if data is available
        if atm_humidity is not None:
            optimal_humidity = convert_humidity_scale(atm_humidity)
            humid_warning_min = max(20, optimal_humidity - 15)
            humid_warning_max = min(80, optimal_humidity + 15)
            humid_critical_min = max(10, optimal_humidity - 30)
            humid_critical_max = min(95, optimal_humidity + 30)
            humidity_ranges = {
                'warning': {'min': humid_warning_min, 'max': humid_warning_max},
                'critical': {'min': humid_critical_min, 'max': humid_critical_max}
            }
        else:
            humidity_ranges = None

        plant_data = {
            'id': str(p.get('id')),
            'commonName': p.get('common_name') or p.get('scientific_name'),
            'scientificName': p.get('scientific_name'),
            'imageUrl': p.get('image_url') or '',
            'temperature': temperature_ranges,
            'humidity': humidity_ranges
        }
        # Cache the result
        _plant_cache[plant_id] = plant_data
        return plant_data
    except Exception as e:
        print(f'Error fetching plant {plant_id}: {e}')
        return None

def format_rpi(row):
    if not row:
        return None

    plant_data = None
    plant_id = row['plant_id'] if 'plant_id' in row.keys() else None
    if plant_id:
        try:
            plant_data = get_plant_by_id(plant_id)
        except Exception as e:
            print(f'Error getting plant data for RPI {row["id"]}: {e}')
            plant_data = None

    return {
        'id': row['id'],
        'rpiName': row['name'],
        'plant': plant_data,
        'currTemperature': row['curr_temp'],
        'currHumidity': row['curr_humid'],
        'connectionStatus': row['status']
    }
