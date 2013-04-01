var module = angular.module('instances_spawn', ["common"]);

function SpawnController($scope){
    var image_list = window.data.image;
    $scope.data = window.data;
    $scope.infinite_lifespan = true;
    var combos = [
        "project",
        "image",
        "instance_type",
        "fw_rule_set",
    ];
    $scope.form = {};
    for (var i = combos.length - 1; i >= 0; --i) {
        $scope.form[combos[i]] = $.querystring(combos[i], "");
    }
}
