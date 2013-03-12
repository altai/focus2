var module = angular.module('projects_fw_rule_sets_edit', ["common"]);


module.directive('ngCopyDefault', function factory() {
    return function link(scope, element, attrs) {
        scope.$watch(attrs.ngCopyDefault, function(value) {
            if (!scope.done) {
                $(element).val(value);
            }
        });
    };
});


function FwRuleSetsController($scope) {
    $scope.fw_rules = window.data.fw_rules || [];

    $scope.add_rule = function () {
        console.log("hello");
        var new_rule = {
            'protocol': $scope.protocol,
            'source': $scope.source,
            'port-range-first': $scope.port_range_first,
            'port-range-last': $scope.port_range_last,
        };
        console.log(new_rule);
        $scope.fw_rules.push(new_rule);
    };

    $scope.remove_rule = function () {
        var index = this.$index;
        var old_arr = $scope.fw_rules;
        var new_arr = old_arr.slice(0, index).concat(old_arr.slice(index + 1));
        $scope.fw_rules = new_arr;
    };
}
