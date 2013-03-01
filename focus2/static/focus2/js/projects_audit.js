var module = angular.module('projects_audit', ['ngResource', 'ui']);


module.factory('Search', function ($resource){
    return $resource('/projects/audit/', {api_marker: 1})
});


function DefaultCtrl($scope, $routeParams, $resource, Search, $location) {
    var date_format = "dd.MM.yyyy";
    var defaults = {
        page: 1,
        perPage: 10,
        users: "",
        date_range: new Date().add({months: -1}).toString(date_format) +
            " - " + new Date().toString(date_format),
    };

    var params = {
        page: parseInt($routeParams.page) || defaults.page,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
        users: $routeParams.users || defaults.users,
        date_range: $routeParams.date_range || defaults.date_range,
    };

    $scope.page = params.page;
    $scope.perPage = params.perPage;
    $scope.users = params.users.split(",");
    $scope.date_range = params.date_range.replace(/\./g, "/");;

    $scope.update_location = function() {
        var date_range = ($("#date_range").val() || "").replace(/\//g, ".");
        $location.path('/' + $scope.page + '/' + $scope.perPage + '/' + $scope.users.join(",") + '/' + date_range);
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
        when('/:page/:perPage/:users/:date_range', {templateUrl: template, controller: DefaultCtrl}).
        otherwise({redirectTo: '/'});
}]);
