var module = angular.module('instances_spawn', ["common", "ui"]);

function SpawnController($scope){
    var image_list = window.data.image;
    $scope.data = window.data;
    $scope.expiration_never = true;
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

    $scope.fw_rule_total = [];
    var fw_rule_set_by_id = {};
    var fw_rule_set = window.data.fw_rule_set;
    var i;
    for (i = 0; i < fw_rule_set.length; ++i) {
        fw_rule_set_by_id[fw_rule_set[i].id] = fw_rule_set[i];
    }

    $scope.on_fw_rules_changed = function () {
        var fw_rule_total = [];
        var fw_rule_set_ids = $scope.form.fw_rule_set;
        var i;
        for (i = 0; i < fw_rule_set_ids.length; ++i) {
            fw_rule_total = fw_rule_total.concat(fw_rule_set_by_id[fw_rule_set_ids[i]].rules);
        }
        $scope.fw_rule_total = fw_rule_total;
    };
}
