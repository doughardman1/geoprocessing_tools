// Define a geometry for London
var londonGeometry = ee.Geometry.Rectangle([-0.5104, 51.2868, 0.3340, 51.6919]);

// Define visualization parameters
var vis_params = {
  bands: ['SR_B5', 'SR_B4', 'SR_B3'],
  min: 0,
  max: 3000,
  gamma: 1.2
};

// Update the filterBounds to use the London geometry
var l8_composite = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterDate('2023-01-01', '2024-01-01')
                  .filterBounds(londonGeometry)
                  .filter(ee.Filter.lt('CLOUD_COVER', 10))
                  .median()
                  .clip(londonGeometry);

// Add the layer to the map
Map.addLayer(l8_composite, vis_params, 'L8 Composite');

// Export the data to Drive with the updated geometry
Export.image.toDrive({
  image: l8_composite.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']),
  description: 'London_L8_B1to7',
  folder: 'London_L8',
  scale: 30,
  region: londonGeometry,
  fileDimensions: 7680,
  maxPixels: 10e11,
  crs: 'EPSG:27700'
});
