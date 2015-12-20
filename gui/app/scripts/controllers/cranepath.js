'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:CranepathCtrl
 * @description
 * # CranepathCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('CranepathCtrl', function ($scope, $location,$http,leafletData, currentProject) {
    $scope.mapLoaded = false;
    $scope.bdLoaded = false;
    
    L.Icon.Default.imagePath = 'images';
    
    var turbineIcon = {
      iconUrl:'/images/turbine.png',
      iconSize:[20, 40],
      iconAnchor:[7, 40]
    };
      
    var crossingIcon = {
      iconUrl:'/images/marker-icon.png',
      iconSize:[25, 40],
      iconAnchor:[12, 40]
    };

    var tilesDict = {
      openstreetmap: {
        name: "OpenStreetMap",
        url: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        type: 'xyz',
        options: {
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }
      },
      opencyclemap: {
        name: "OpenCycleMap",
        url: 'http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png',
        type: 'xyz',
        options: {
          attribution: 'All maps &copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, map data &copy; <a href="http://www.openstreetmap.org">OpenStreetMap</a> (<a href="http://www.openstreetmap.org/copyright">ODbL</a>'
        }
      },
      mapbox_terrain: {
        name: 'Mapbox Terrain',
        url: 'http://api.tiles.mapbox.com/v4/{mapid}/{z}/{x}/{y}.png?access_token={apikey}',
        type: 'xyz',
        layerOptions: {
          apikey: 'pk.eyJ1IjoiaHVldm9zYWJpbyIsImEiOiJmTHplSnY0In0.7eT8FT5PcjhjC6Z5mJaKCA',
          mapid: 'huevosabio.kgj8hgpp'
        }
      }
    };

    angular.extend($scope, {
      world: {
        lat: 0,
        lng: 0,
        zoom: 3
      },
      layers: {
        baselayers: tilesDict,
        overlays:{}
      }
    });
    
    $http.get('/api/cranepath/schedule/' + currentProject.project.name)
    .success(function(data, status, headers, config) {
      $scope.schedule = data.schedule;
      
      $scope.costSeries = [];
      $scope.costs = {};
      
      for (var i in data.schedule.features){
        var activity = data.schedule.features[i].properties.activity;
        if (activity === 'Turbine Erection' || activity === 'boundary'){
          continue;
        } else {
          var name = data.schedule.features[i].properties.activity;
          
          if (name === 'crossing'){
            name = name +'-'+data.schedule.features[i].properties.detail;
          }
          if ($scope.costs[name] === undefined){
            $scope.costs[name] = data.schedule.features[i].properties.cost;
          } else{
            $scope.costs[name]+= data.schedule.features[i].properties.cost;
          }
        }
        
      }
      
      for (var i in $scope.costs){
        $scope.costSeries.push({
            name:i,
            y:$scope.costs[i]
        });
      }
      
      
      angular.extend($scope.layers.overlays, {
        geojson: {
          name: "Schedule",
          type: "geoJSONShape",
          visible: true,
          data: data.schedule,
          layerOptions: {
            onEachFeature: function (feature, layer) {
              var txt = '';
              if (feature.properties.activity === 'crossing'){
                txt = 'Activity: Crossing '+feature.properties.detail+
                '<br>Cost: $'+feature.properties.cost;
              } else {
                txt = 'Activity: '+feature.properties.activity+
                '<br>Cost: $'+feature.properties.cost;
              }
              layer.bindPopup(txt);
            },
            style: function (feature) {return {};},
            pointToLayer: function(feature, latlng) {
              if (feature.properties.activity === 'crossing'){
                return new L.marker(latlng, {icon: L.icon(crossingIcon)})
              
              } else {return new L.marker(latlng, {icon: L.icon(turbineIcon)})}
            }
          },
         }
        });
      //add Turbines
      angular.extend($scope.layers.overlays, {
        turbines:{
          name: "Turbines",
          type: "geoJSONShape",
          visible: false,
          layerOptions: {
            pointToLayer: function(feature, latlng) {
              return new L.marker(latlng, {icon: L.icon(turbineIcon)})
            },
          },
          data: data.turbines
        }
      });

      //add Boundary
      angular.extend($scope.layers.overlays, {
        boundary:{
          name: "Boundary",
          type: "geoJSONShape",
          visible: true,
          layerOptions:{
            style: {
              color: '#00D',
              fillColor: 'green',
              weight: 2.0,
              opacity: 0.6,
              fillOpacity: 0.2
            }
          },
          data: data.boundary
        }
      });

      //add all features
      for (var feature in data.features){
        var name = data.features[feature].name;
        var layer = {};
        layer[name] = {
          name: name,
          type: "geoJSONShape",
          visible: false,
          data: data.features[feature].geojson
        }
        angular.extend($scope.layers.overlays, layer);
      }
     
    })
    .error(function(data, status, headers, config) {
      console.log(data);
      $location.path('/zipupload');
    })
    .then(function(){
      $scope.mapLoaded = true;
      $scope.bdLoaded = true;
      $scope.centerMap();
    });
    
    
    angular.extend($scope, {
      tiles: tilesDict.mapbox_terrain
    });
    
    $scope.centerMap = function() {
      leafletData.getMap().then(function(map) {
        var latlngs = [];
        for (var i in $scope.layers.overlays.geojson.data.features) {
          if ($scope.layers.overlays.geojson.data.features[i].geometry.type === 'Point'){
            var coord = $scope.layers.overlays.geojson.data.features[0].geometry.coordinates;
            latlngs.push(L.GeoJSON.coordsToLatLng(coord));
          }
          else if ($scope.layers.overlays.geojson.data.features[i].geometry.type === 'LineString'){
            for (var j in $scope.layers.overlays.geojson.data.features[i].geometry.coordinates){
              var coord = $scope.layers.overlays.geojson.data.features[i].geometry.coordinates[j];
              latlngs.push(L.GeoJSON.coordsToLatLng(coord));
            }
          } else {
            continue;
          }
        }
        map.fitBounds(latlngs);
      });
    };
    $scope.goToZip = function(){
        $location.path('/zipupload');
    };
  });

Number.prototype.formatMoney = function(c, d, t){
  var n = this, 
      c = isNaN(c = Math.abs(c)) ? 2 : c, 
      d = d == undefined ? "." : d, 
      t = t == undefined ? "," : t, 
      s = n < 0 ? "-" : "", 
      i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", 
      j = (j = i.length) > 3 ? j % 3 : 0;
  return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 };
