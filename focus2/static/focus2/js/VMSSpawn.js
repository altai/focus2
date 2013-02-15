var module = angular.module('VMSSpawn', []);

jQuery(function($) {
    $(".select2").select2();
});

function VMSSpawnController($scope){
    $scope.projects = window.data.projects;
    $scope.images = window.data.images;
}
