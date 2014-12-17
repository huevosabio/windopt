'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:CranepathCtrl
 * @description
 * # CranepathCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('CranepathCtrl', function ($scope, $location,$http,leafletData) {
    
    L.Icon.Default.imagePath = "images";
    
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
    
    $http.get('/api/cranepath/schedule')
    .success(function(data, status, headers, config) {
      //console.log(data);
      $scope.schedule = data.schedule;
      
      angular.extend($scope, {
        geojson: {
          data: data.schedule,
          onEachFeature: function (feature, layer) {
            var txt = "";
            if (feature.properties.activity === 'Crossing'){
              txt = "Activity: Crossing "+feature.properties.crossing+
              "<br>Cost: $"+feature.properties.cost;
            } else {
              txt = "Activity:"+feature.properties.activity+
              "<br>Cost: $"+feature.properties.cost;
            }
            layer.bindPopup(txt);
          },
          style: function (feature) {return {};},
          pointToLayer: function(feature, latlng) {
            if (feature.properties.activity === 'Crossing'){
              return new L.marker(latlng, {icon: L.icon(crossingIcon)})
              
            } else {return new L.marker(latlng, {icon: L.icon(turbineIcon)})}
            
          }
        }
      });
     
    })
    .error(function(data, status, headers, config) {
      console.log(data);
      $location.path('/zipupload');
    })
    .then(function(){
      $scope.centerMap();
    });
    
    var tilesDict = {
      openstreetmap: {
        url: "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        options: {
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }
      },
      opencyclemap: {
        url: "http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png",
        options: {
          attribution: 'All maps &copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, map data &copy; <a href="http://www.openstreetmap.org">OpenStreetMap</a> (<a href="http://www.openstreetmap.org/copyright">ODbL</a>'
        }
      },
      mapbox_terrain: {
        name: 'Mapbox Terrain',
        url: 'http://api.tiles.mapbox.com/v4/{mapid}/{z}/{x}/{y}.png?access_token={apikey}',
        type: 'xyz',
        options: {
          apikey: 'pk.eyJ1IjoiaHVldm9zYWJpbyIsImEiOiJmTHplSnY0In0.7eT8FT5PcjhjC6Z5mJaKCA',
          mapid: 'huevosabio.kgj8hgpp'
        }
      }
    };
    
    angular.extend($scope, {
      tiles: tilesDict.mapbox_terrain
    });
    
    $scope.centerMap = function() {
      leafletData.getMap().then(function(map) {
        var latlngs = [];
        for (var i in $scope.geojson.data.features) {
          if ($scope.geojson.data.features[i].geometry.type === 'Point'){
            var coord = $scope.geojson.data.features[0].geometry.coordinates;
            latlngs.push(L.GeoJSON.coordsToLatLng(coord));
          }
          else if ($scope.geojson.data.features[i].geometry.type === 'LineString'){
            for (var j in $scope.geojson.data.features[i].geometry.coordinates){
              var coord = $scope.geojson.data.features[i].geometry.coordinates[j];
              latlngs.push(L.GeoJSON.coordsToLatLng(coord));
            }
          } else {
            continue;
          }
        }
        map.fitBounds(latlngs);
      });
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