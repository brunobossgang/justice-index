"""
Approximate lat/lon coordinates for US federal judicial district courthouses.
Used for geographic bubble maps on the dashboard.
"""

# District code → (lat, lon, state_abbrev) for major courthouse in each district
DISTRICT_COORDS = {
    1: (38.895, -77.036, "DC"),       # D.C.
    2: (42.360, -71.058, "MA"),       # D. Massachusetts
    3: (41.825, -71.410, "RI"),       # D. Rhode Island
    4: (41.308, -72.928, "CT"),       # D. Connecticut
    5: (43.649, -72.320, "VT"),       # D. Vermont
    6: (40.715, -74.003, "NY"),       # S.D. New York
    7: (42.886, -78.878, "NY"),       # W.D. New York
    8: (40.680, -73.976, "NY"),       # E.D. New York
    9: (42.652, -73.757, "NY"),       # N.D. New York
    10: (40.714, -74.173, "NJ"),      # D. New Jersey
    11: (39.952, -75.164, "PA"),      # E.D. Pennsylvania
    12: (40.441, -79.996, "PA"),      # W.D. Pennsylvania
    13: (40.338, -76.412, "PA"),      # M.D. Pennsylvania
    14: (39.290, -76.612, "MD"),      # D. Maryland
    15: (36.847, -75.978, "VA"),      # E.D. Virginia
    16: (37.271, -79.941, "VA"),      # W.D. Virginia
    17: (35.480, -80.216, "NC"),      # M.D. North Carolina
    18: (34.226, -77.945, "NC"),      # E.D. North Carolina
    19: (35.595, -82.551, "NC"),      # W.D. North Carolina
    20: (34.001, -81.035, "SC"),      # D. South Carolina
    21: (33.749, -84.388, "GA"),      # N.D. Georgia
    22: (32.076, -81.088, "GA"),      # S.D. Georgia
    23: (31.579, -84.176, "GA"),      # M.D. Georgia
    24: (30.332, -81.655, "FL"),      # M.D. Florida
    25: (25.775, -80.194, "FL"),      # S.D. Florida
    26: (30.438, -84.281, "FL"),      # N.D. Florida
    30: (32.361, -86.279, "AL"),      # M.D. Alabama
    31: (33.521, -86.803, "AL"),      # N.D. Alabama
    32: (30.694, -88.043, "AL"),      # S.D. Alabama
    33: (32.299, -90.185, "MS"),      # S.D. Mississippi
    34: (34.257, -88.703, "MS"),      # N.D. Mississippi
    35: (36.163, -86.782, "TN"),      # M.D. Tennessee
    36: (35.046, -85.310, "TN"),      # E.D. Tennessee
    37: (35.149, -90.049, "TN"),      # W.D. Tennessee
    40: (38.186, -84.875, "KY"),      # E.D. Kentucky
    41: (38.254, -85.760, "KY"),      # W.D. Kentucky
    42: (39.961, -82.999, "OH"),      # S.D. Ohio
    43: (41.505, -81.694, "OH"),      # N.D. Ohio
    44: (42.331, -83.046, "MI"),      # E.D. Michigan
    45: (42.963, -85.668, "MI"),      # W.D. Michigan
    50: (41.878, -87.630, "IL"),      # N.D. Illinois
    51: (38.627, -90.199, "IL"),      # S.D. Illinois
    52: (40.116, -89.131, "IL"),      # C.D. Illinois
    53: (39.768, -86.158, "IN"),      # S.D. Indiana
    54: (41.079, -85.139, "IN"),      # N.D. Indiana
    55: (43.038, -87.907, "WI"),      # E.D. Wisconsin
    56: (43.073, -89.401, "WI"),      # W.D. Wisconsin
    60: (44.977, -93.265, "MN"),      # D. Minnesota
    61: (41.256, -95.934, "NE"),      # D. Nebraska (Omaha)
    63: (38.627, -90.199, "MO"),      # E.D. Missouri
    64: (39.100, -94.578, "MO"),      # W.D. Missouri
    65: (41.591, -93.604, "IA"),      # S.D. Iowa
    66: (42.500, -96.400, "IA"),      # N.D. Iowa
    67: (47.926, -97.033, "ND"),      # D. North Dakota
    68: (43.550, -96.700, "SD"),      # D. South Dakota
    70: (38.895, -94.686, "KS"),      # D. Kansas
    80: (35.468, -97.516, "OK"),      # W.D. Oklahoma
    81: (36.154, -95.993, "OK"),      # N.D. Oklahoma
    82: (34.746, -96.678, "OK"),      # E.D. Oklahoma
    83: (34.746, -92.290, "AR"),      # E.D. Arkansas
    84: (35.390, -94.399, "AR"),      # W.D. Arkansas
    85: (29.762, -95.363, "TX"),      # S.D. Texas
    86: (32.780, -96.799, "TX"),      # N.D. Texas
    87: (31.760, -106.486, "TX"),     # W.D. Texas
    88: (30.268, -97.743, "TX"),      # E.D. Texas (Tyler)
    89: (30.451, -91.187, "LA"),      # M.D. Louisiana
    90: (29.951, -90.071, "LA"),      # E.D. Louisiana
    91: (32.509, -93.750, "LA"),      # W.D. Louisiana
    93: (39.740, -104.990, "CO"),     # D. Colorado
    94: (40.760, -111.891, "UT"),     # D. Utah
    95: (41.140, -104.820, "WY"),     # D. Wyoming
    96: (35.085, -106.651, "NM"),     # D. New Mexico
    97: (33.449, -112.074, "AZ"),     # D. Arizona
    98: (36.167, -115.149, "NV"),     # D. Nevada
    99: (43.613, -116.203, "ID"),     # D. Idaho
    100: (46.872, -113.994, "MT"),    # D. Montana
    101: (47.659, -117.426, "WA"),    # E.D. Washington
    102: (47.605, -122.330, "WA"),    # W.D. Washington
    103: (45.515, -122.679, "OR"),    # D. Oregon
    104: (37.775, -122.418, "CA"),    # N.D. California
    105: (34.052, -118.244, "CA"),    # C.D. California
    106: (32.717, -117.163, "CA"),    # S.D. California
    107: (38.582, -121.494, "CA"),    # E.D. California
    110: (21.307, -157.858, "HI"),    # D. Hawaii
    111: (61.218, -149.900, "AK"),    # D. Alaska
    113: (38.530, -121.469, "GU"),    # D. Guam (approx)
    114: (18.466, -66.106, "PR"),     # D. Puerto Rico
    115: (18.342, -64.931, "VI"),     # D. Virgin Islands
}
