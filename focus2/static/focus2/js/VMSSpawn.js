var module = angular.module('VMSSpawn', []);

jQuery(function($) {
    $(".select2").select2();
});

function VMSSpawnController($scope){
    var image_list = window.data.image;
    for (var i = image_list.length - 1; i >= 0; --i) {
        image_list[i]["hr-size"] = getHumanReadableSizeBytes(image_list[i]["size"]);
    }
    $scope.data = window.data;
    $scope.infinite_lifespan = true;
    $scope.form = {};
}
