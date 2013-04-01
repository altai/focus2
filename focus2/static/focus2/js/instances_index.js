var module = angular.module('instances_index', ['ngResource', 'ui']);

module.factory('Search', function ($resource){
    return $resource('/instances/', {api_marker: 1})
});


function DefaultCtrl($scope, $routeParams, $resource, Search, $location){
    /* add func to update scope after an object */

    var defaults = {
        query: '',
        page: 1,
        columns: [],
        perPage: 10
    }

    var params = {
        query: $routeParams.query || defaults.query,
        page: parseInt($routeParams.page) || defaults.page,
        columns: $routeParams.columns || defaults.columns,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
    }

    $scope.query = params.query;
    $scope.page = params.page;
    $scope.columns = params.columns;
    $scope.perPage = params.perPage;

    $scope.update_location = function(){
        if ($scope.perPage != defaults.perPage){
            $location.path('/' + $scope.query + '/' + $scope.page + '/' + $scope.columns.join() + '/' + $scope.perPage);
        } else if ($scope.columns != defaults.columns){
            $location.path('/' + $scope.query + '/' + $scope.page + '/' + $scope.columns.join());
        } else if ($scope.page != defaults.page){
            $location.path('/' + $scope.query + '/' + $scope.page);
        } else if ($scope.query != defaults.query){
            $location.path('/' + $scope.query);
        } else {
            $location.path('/');
        }
    }

    $scope.change_page = function(page){
        $scope.page = page;
        $scope.update_location();
    }

    $scope.per_page_choices = [10, 20, 50, 100];
    $scope.search = Search.get(params);

    $scope.columns_definitions = [
        'Name',
        'Ping Test',
        'Id',
        'Cost Per Day',
        'VLAN',
        'IP',
        'Created',
        'Project',
        'User',
        'Image',
        'Type'
    ];

    $scope.columns_editor_visible = false;
    $scope.toggle_columns_editor_visibility = function(){
        $scope.columns_editor_visible = ! $scope.columns_editor_visible;
    }
}

var template = 'partials/search.html'

module.config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/', {templateUrl: template, controller: DefaultCtrl}).
        when('/:query', {templateUrl: template, controller: DefaultCtrl}).
        when('/:query/:page/', {templateUrl: template, controller: DefaultCtrl}).
        when('/:query/:page/:columns', {templateUrl: template, controller: DefaultCtrl}).
        when('/:query/:page/:columns/:perPage', {templateUrl: template, controller: DefaultCtrl}).
        otherwise({redirectTo: '/'});
}])

module.directive('floatAround', function(){
    /* keeps the element around target element */
    return function(scope, element, attrs){
        var $x = $(attrs.floatAround);
        console.log($x)
        /* element will be positioned below $x */
    }
})
