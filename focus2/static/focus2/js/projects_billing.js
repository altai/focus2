var module = angular.module('projects_billing', ['ngResource', 'ui']);


module.factory('Search', function ($resource){
    return $resource('/projects/billing/', {api_marker: 1})
});


module.filter('totalcost', function() {
    return function(data) {
        if (!data)
            return "";
        var total = 0.0;
        var i;
        for (i = data.length - 1; i >= 0; --i) {
            total += data[i]["cost"];
        }
        return total;
    }
});


module.filter('costformat', function() {
    return function(val) {
        return (val || 0.0).toFixed(2);
    }
});


function DefaultCtrl($scope, $routeParams, $resource, Search, $location) {
    var today = new Date().toString("dd.MM.yyyy");
    var defaults = {
        page: 1,
        perPage: 10,
        resources: "",
        date_range: today + " - " + today,
    };

    var params = {
        page: parseInt($routeParams.page) || defaults.page,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
        resources: $routeParams.resources || defaults.resources,
        date_range: $routeParams.date_range || defaults.date_range,
    };

    $scope.page = params.page;
    $scope.perPage = params.perPage;
    $scope.resources = params.resources.split(",");
    $scope.date_range = params.date_range.replace(/\./g, "/");;

    $scope.update_location = function() {
        var date_range = ($("#date_range").val() || "").replace(/\//g, ".");
        $location.path('/' + $scope.page + '/' + $scope.perPage + '/' + $scope.resources.join(",") + '/' + date_range);
    }

    $scope.change_page = function(page){
        $scope.page = page;
        $scope.update_location();
    }

    $scope.per_page_choices = [10, 20, 50, 100];
    $scope.search = Search.get(params);
    init_daterangepickers();
}

var template = 'partials/search.html';

module.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/', {templateUrl: template, controller: DefaultCtrl}).
        when('/:page/:perPage/:resources/:date_range', {templateUrl: template, controller: DefaultCtrl}).
        otherwise({redirectTo: '/'});
}]);
