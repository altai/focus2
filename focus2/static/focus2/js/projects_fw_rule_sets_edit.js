var module = angular.module("projects_fw_rule_sets_edit", ["ui", "common"]);


module.directive("ngCopyDefault", function factory() {
    return function link(scope, element, attrs) {
        scope.$watch(attrs.ngCopyDefault, function(value) {
            var $element = $(element);
            var dest = $element.attr("ng-model");
            if (!scope[dest + "_edited"]) {
                scope[dest] = value;
            }
        });
    };
});


function FwRuleSetsController($scope) {
    $scope.fw_rules = window.data.fw_rules || [];
    $scope.fw_deleted = [];

    $scope.add_rule = function () {
        var new_rule = {
            "protocol": $scope.protocol,
            "source": $scope.source,
            "port-range-first": parseInt($scope.port_range_first) || -1,
            "port-range-last": parseInt($scope.port_range_last) || -1,
        };
        $scope.fw_rules.push(new_rule);
        $scope.port_range_first = undefined;
        $scope.port_range_last = undefined;
        $scope.port_range_last_edited = false;
    };

    $scope.remove_rule = function () {
        var index = this.$index;
        var old_arr = $scope.fw_rules;
        var id = old_arr[index]["id"];
        if (typeof(id) != "undefined")
            $scope.fw_deleted.push(id);
        var new_arr = old_arr.slice(0, index).concat(old_arr.slice(index + 1));
        $scope.fw_rules = new_arr;
    };
}
