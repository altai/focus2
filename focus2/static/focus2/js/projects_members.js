var module = angular.module('projects_members', ['ngResource', 'ui']);


module.factory('Search', function ($resource){
    return $resource('/projects/members/', {api_marker: 1})
});


function DefaultCtrl($scope, $routeParams, $resource, Search, $location) {
    var defaults = {
        page: 1,
        perPage: 10,
        projects: "",
        query: "",
    };

    var params = {
        page: parseInt($routeParams.page) || defaults.page,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
        projects: $routeParams.projects || defaults.projects,
        query: $routeParams.query || defaults.query,
    };

    $scope.page = params.page;
    $scope.perPage = params.perPage;
    $scope.projects = params.projects.split(",");
    $scope.query = params.query;

    $scope.update_location = function() {
        $location.path('/' + $scope.page + '/' + $scope.perPage + '/' + $scope.projects.join(",") + '/' + $scope.query);
    }

    $scope.change_page = function(page){
        $scope.page = page;
        $scope.update_location();
    }

    $scope.per_page_choices = [10, 20, 50, 100];
    $scope.search = Search.get(params);
}

var template = 'partials/search.html';

module.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/', {templateUrl: template, controller: DefaultCtrl}).
        when('/:page/:perPage/:projects/:query', {templateUrl: template, controller: DefaultCtrl}).
        otherwise({redirectTo: '/'});
}]);
