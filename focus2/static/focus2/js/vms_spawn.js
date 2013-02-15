var module = angular.module('vms_spawn', []);

function SpawnController($scope){
    var image_list = window.data.image;
    $scope.data = window.data;
    $scope.infinite_lifespan = true;
    $scope.form = {
        "project": "",
        "image": "",
        "instance_type": "",
        "fw_rule_set": "",
    };
}
