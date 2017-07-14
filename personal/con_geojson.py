from geojson import FeatureCollection

# no hole within polygon
geojson_raw = { "type": "FeatureCollection",
                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                "features": [{ "type": "Feature",
                    "properties": {"area": "user_defined"},
                    "geometry": { "type": "Polygon",
                                "coordinates": [[[8.72,12.28],
                                                 [29.34,0.92],
                                                 [20.63,-6.24],
                                                 [8.72,12.28]]]}
                             }
            ]
}
data = FeatureCollection(geojson_raw)
cut_poly = data['features']['features'][0]['geometry']
print len(cut_poly['coordinates'])