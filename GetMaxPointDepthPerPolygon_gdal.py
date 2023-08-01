from osgeo import ogr, osr

polygon_layer_file = r"..\GIS\shp\ResidentialLandUse_v01_R.shp"
point_layer_file = r"..\GIS\scripts\ResidentialLandUse_max_depths_per_cell_P.shp"
output_shapefile = r"..\GIS\shp\MaxDepths_Residential_PerProperty_v01_P.shp"

# Open the polygon layer
polygon_driver = ogr.GetDriverByName("ESRI Shapefile")
polygon_datasource = polygon_driver.Open(polygon_layer_file, 0)
polygon_layer = polygon_datasource.GetLayer()

# Open the point layer
point_driver = ogr.GetDriverByName("ESRI Shapefile")
point_datasource = point_driver.Open(point_layer_file, 0)
point_layer = point_datasource.GetLayer()

# Define a dictionary to store the maximum attribute value for each polygon feature
max_values = {}

# Iterate through each polygon feature
for polygon_feature in polygon_layer:
    polygon_geometry = polygon_feature.GetGeometryRef()
    polygon_extent = polygon_geometry.GetEnvelope()

    # Iterate through each point feature within the current polygon's extent
    for point_feature in point_layer:
        point_geometry = point_feature.GetGeometryRef()
        point_coords = (point_geometry.GetX(), point_geometry.GetY())

        # Check if the point is within the extent of the current polygon
        if polygon_extent[0] <= point_coords[0] <= polygon_extent[1] and polygon_extent[2] <= point_coords[1] <= polygon_extent[3]:
            # Get the attribute value of the current point feature
            attribute_value = point_feature.GetField("DEPTH2D")

            # Check if the current polygon is not in the max_values dictionary or if the attribute value is larger
            if polygon_feature.GetFID() not in max_values or attribute_value > max_values[polygon_feature.GetFID()]:
                # Update the max_values dictionary with the new maximum value
                max_values[polygon_feature.GetFID()] = attribute_value

    # Reset the point_layer filter after processing each polygon
    point_layer.ResetReading()

# Create a new shapefile to store the selected points
output_driver = ogr.GetDriverByName("ESRI Shapefile")
output_datasource = output_driver.CreateDataSource(output_shapefile)
output_layer = output_datasource.CreateLayer("max_points_within_polygons", srs=point_layer.GetSpatialRef(), geom_type=ogr.wkbPoint)

# Add fields to the new layer (copying fields from the original point layer)
point_layer_def = point_layer.GetLayerDefn()
for i in range(point_layer_def.GetFieldCount()):
    field_def = point_layer_def.GetFieldDefn(i)
    output_layer.CreateField(field_def)

# Add the selected point features to the new layer
for polygon_feature in polygon_layer:
    polygon_geometry = polygon_feature.GetGeometryRef()
    polygon_extent = polygon_geometry.GetEnvelope()

    for point_feature in point_layer:
        point_geometry = point_feature.GetGeometryRef()
        point_coords = (point_geometry.GetX(), point_geometry.GetY())

        if polygon_extent[0] <= point_coords[0] <= polygon_extent[1] and polygon_extent[2] <= point_coords[1] <= polygon_extent[3]:
            attribute_value = point_feature.GetField("DEPTH2D")

            if attribute_value == max_values[polygon_feature.GetFID()]:
                # Create a new feature and set its geometry and attributes
                new_feature = ogr.Feature(output_layer.GetLayerDefn())
                new_feature.SetGeometry(point_geometry)

                for i in range(point_layer_def.GetFieldCount()):
                    field_name = point_layer_def.GetFieldDefn(i).GetNameRef()
                    new_feature.SetField(field_name, point_feature.GetField(field_name))

                # Add the new feature to the output layer
                output_layer.CreateFeature(new_feature)

                # Cleanup
                new_feature = None

# Close the datasources
polygon_datasource = None
point_datasource = None
output_datasource = None
