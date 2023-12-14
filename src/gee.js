// Colors, code from JRC TMF website

function rgb(r,g,b){  
    var bin = r << 16 | g << 8 | b;  
    return (function(h){  
        return new Array(7-h.length).join("0")+h;  
    })(bin.toString(16).toUpperCase());  
}

var PALETTEAnnualChanges = [
    rgb(0,90,0),      // val 1. Undisturbed Tropical moist forest (TMF)  
    rgb(100,155,35),  // val 2. Degraded TMF  
    rgb(255,135,15),  // val 3. Deforested land  
    rgb(210,250,60),  // val 4. Forest regrowth  
    rgb(0,140,190),   // val 5. Permanent or seasonal Water  
    rgb(255,255,255), // val 6. Other land cover  
];

var jrc_params = {
  min : 1,
  max : 6,
  palette: PALETTEAnnualChanges
}

function luc_counts(img) {
  
  var reducer_args = {
    reducer: ee.Reducer.count(),
    scale: 30,
    maxPixels: 1e13
  }
  
  var undisturbed = img.updateMask(img.eq(1)).reduceRegion(reducer_args);
  var uf = ee.Feature(null, undisturbed).set("LUC", "1");
  var undisturbed_f = ee.FeatureCollection([ uf ]);
  
  var degraded = img.updateMask(img.eq(2)).reduceRegion(reducer_args);
  var degf = ee.Feature(null, degraded).set("LUC", "2");
  var degraded_f = ee.FeatureCollection([ degf ]);
  
  var deforested = img.updateMask(img.eq(3)).reduceRegion(reducer_args);
  var deff = ee.Feature(null, deforested).set("LUC", "3");
  var deforested_f = ee.FeatureCollection([ deff ]);
  
  var regrowth = img.updateMask(img.eq(4)).reduceRegion(reducer_args);
  var regf = ee.Feature(null, regrowth).set("LUC", "4");
  var regrowth_f = ee.FeatureCollection([ regf ]);
  
  var water = img.updateMask(img.eq(5)).reduceRegion(reducer_args);
  var watf = ee.Feature(null, water).set("LUC", "5");
  var water_f = ee.FeatureCollection([ watf ]);
  
  var other = img.updateMask(img.eq(6)).reduceRegion(reducer_args);
  var othf = ee.Feature(null, other).set("LUC", "6");
  var other_f = ee.FeatureCollection([ othf ]);
  
  return undisturbed_f.merge(degraded_f.merge(deforested_f.merge(regrowth_f.merge(water_f.merge(other_f)))));
}

function analyse_year(year, area) {
  // JRC for region and year of interest
  var jrc_asia = ee.Image.load("projects/JRC/TMF/v1_" + year + "/AnnualChanges/" + area.jrc_region);
  
  // Clip to AOI
  var jrc_clipped = jrc_asia.clip(area.aoi);
  
  return {
    clipped: jrc_clipped,
    lucs: luc_counts(jrc_clipped)
  };
}

function analyse(areas, years, export_data, plot_data) {
  for (var c = 0; c < areas.length; c++) {
    var area = areas[c];
    
    // LUCs
    for (var i = 0; i < years.length; i++) {
      var year = years[i];
      var values = analyse_year(year, area);
      var lucs = values.lucs;
      var clipped = values.clipped;
      
      if (export_data) {
        Export.table.toDrive({
          collection: lucs,
          folder: "jrc_historic_analysis",
          description: ("jrc_counts_" + year + "_" + area.name),
          fileNamePrefix: ("jrc_counts_" + year + "_" + area.name)
        });
      }
      
      if (plot_data) {
        Map.addLayer(clipped.select("Dec2008"), jrc_params, ("jrc_" + year + "_" + area.name))
      }
    }
  }
}

var indonesia = {
  name: "Indonesia",
  aoi: countries.filter(ee.Filter.equals("ADM0_NAME", "Indonesia")),
  jrc_region: "1ASIA"
}

var malaysia = {
  name: "Malaysia",
  aoi: countries.filter(ee.Filter.equals("ADM0_NAME", "Malaysia")),
  jrc_region: "1ASIA"
}

var areas = [ indonesia ]

print("Indonesia area:", indonesia.aoi.first().geometry().area(), "msq");


Map.setCenter(103.28, -0.3, 10);

analyse(areas, [2021, 2022], false, true);

