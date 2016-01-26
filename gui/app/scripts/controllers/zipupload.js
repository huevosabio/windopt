'use strict';

/**
 * @ngdoc function
 * @name windopsApp.controller:ZipuploadCtrl
 * @description
 * # ZipuploadCtrl
 * Controller of the windopsApp
 */
angular.module('windopsApp')
  .controller('ZipuploadCtrl',
  function($scope, $upload, $location, $alert, $http, currentProject) {
  $scope.onFileSelect = function($files) {
    //$files: an array of files selected, each file has name, size, and type.
    $scope.selectedFiles = $files;
    $scope.progress = [];
    for (var i = 0; i < $files.length; i++) {
      var file = $files[i];
      $scope.upload = $upload.upload({
        url: 'api/cranepath/zipupload', //upload.php script, node.js route, or servlet url
        method: 'POST',
        //headers: {'header-key': 'header-value'},
        //withCredentials: true,
        data: {"project": currentProject.project.name},
        file: file // or list of files ($files) for html5 only
        //fileName: 'doc.jpg' or ['1.jpg', '2.jpg', ...] // to modify the name of the file(s)
        // customize file formData name ('Content-Disposition'), server side file variable name. 
        //fileFormDataName: myFile, //or a list of names for multiple files (html5). Default is 'file' 
        // customize how data is added to formData. See #40#issuecomment-28612000 for sample code
        //formDataAppender: function(formData, key, val){}
      }).progress(function(evt) {
        $scope.progress[i-1] = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
      }).success(function(data, status, headers, config) {
        // file is uploaded successfully
         for (i in data.messages){ 
          $alert({
                content: data.messages[i],
                animation: 'fadeZoomFadeDown',
                type: 'warning',
                duration: 3,
                placement:'top-right'
          });
         }
        $location.path('/layerlist');
      })
      .error(function(data, status, headers, config) {
        // error uploading
          $alert({
                content: "Error uploading: " + data.message,
                animation: 'fadeZoomFadeDown',
                type: 'danger',
                duration: 3,
                placement:'top-right'
          });
        delete $scope.selectedFiles;
        delete $scope.progress;
      })
      //.then(success, error, progress); 
      // access or attach event listeners to the underlying XMLHttpRequest.
      //.xhr(function(xhr){xhr.upload.addEventListener(...)})
    }
    /* alternative way of uploading, send the file binary with the file's content-type.
       Could be used to upload files to CouchDB, imgur, etc... html5 FileReader is needed. 
       It could also be used to monitor the progress of a normal http post/put request with large data*/
    // $scope.upload = $upload.http({...})  see 88#issuecomment-31366487 for sample code.
  };
});