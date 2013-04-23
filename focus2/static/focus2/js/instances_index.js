var module = angular.module('instances_index', ['ngResource', 'ui']),
   template = 'partials/search.html'

module.factory('Instances', function ($resource){
    return $resource('/instances/', {api_marker: 1})
});

module.factory('SearchQueries', function ($resource){
  return $resource('/instances/searches/:_id', {_id: '@id'});
})

function DefaultCtrl($scope, $routeParams, $resource, $http, Instances, SearchQueries, $location){
    /* add func to update scope after an object */

    var defaults = {
        query: '',
        page: 1,
        columns: [],
        perPage: 10
    },
        params = {
        query: $routeParams.query || defaults.query,
        page: parseInt($routeParams.page) || defaults.page,
        columns: $routeParams.columns || defaults.columns,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
    },
        columns_definitions = {
       'Name': 'name',
       'Ping Test': 'state',
       'Id': 'id',
       'Cost Per Day': 'cost',
//       'VLAN': 'vlan',
       'IP': 'ipv4',
       'Created': 'created',
       'Project': 'project',
       'User': 'created-by',
       'Image': 'image',
       'Type': 'instance-type'
    },
        order = [
       'Name',
       'Ping Test',
       'Id',
       'Cost Per Day',
       'IP',
       'Created',
       'Project',
       'User',
       'Image',
       'Type'
    ],
       sorter = function(a, b){return order.indexOf(a) - order.indexOf(b)},
       toDataItem = function(data_item){
         this.format = function(string, args){
             var parts = string.split('{}');
             for (var i=0; i < args.length; i++){
               parts[i] = parts[i]+args[i];
             }
             return parts.join('');
         }

         this.isLink = function(){
           return typeof data_item == 'object' &&
             'href' in data_item &&
             'id' in data_item &&
             'name' in data_item;
         }

         this.toLink = function(){
           args = [];
           for (i in data_item){
             args.push(data_item[i]);
           }
           string = '<a href={} id={}>{}</a>';
           return this.format(string, args);
         }

         this.isPingState = function(){
           return typeof data_item == "string" &&
             data_item == data_item.toUpperCase() &&
             !Date.parse(data_item) &&
             data_item.length;
         }

         this.toPingTestState = function(){
           args = data_item == 'ERROR' ? ['red']: ['green'];
           string = '<div style="margin: 10px; width: 20px; height: 20px; background-color: {};text-indent: -100px; border-radius: 10px; overflow: hidden;"></div>';
           return this.format(string, args);
         }

         this.toSimpleString = function(){
           if (typeof data_item == "string"){
             string = '<span>{}</span>';
             args = [data_item];
           } else {
             string = '<span>' + Array(data_item.length).join('{}\n') + '</span>';
             args = data_item;
           }
           return this.format(string, args);
         }
     };

    $scope.update_queries = function(){
          $scope.search_queries = SearchQueries.query();
      };

    $scope.query = params.query;
    $scope.page = params.page;
    $scope.columns = params.columns;
    $scope.perPage = params.perPage;
    $scope.per_page_choices = [10, 20, 50, 100];
    $scope.shown_columns = order.slice();
    $scope.hidden_columns = [];
    $scope.instances = Instances.get(params);

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

    $scope.columns_data = function(name, row){
      var data_item = row.hasOwnProperty(columns_definitions[name]) ? row[columns_definitions[name]] : '';
      data_item = new toDataItem(data_item);
      if (data_item.isLink()){return data_item.toLink();}
      else if (data_item.isPingState()){return data_item.toPingTestState();}
      else {return data_item.toSimpleString();}
    }

    $scope.visibility = {
      'column_editor': false,
      'saved_searches': false
    }

    $scope.toggle_visibility = function(node){
      $scope.visibility[node] = !$scope.visibility[node];
    }

    $scope.horizontalDisplace = function(column_names, to_state){
      if (to_state == 'hide'){
        for (var i=0; i < column_names.length; i++){
          var index = $scope.shown_columns.indexOf(column_names[i]);
          $scope.hidden_columns = $scope.hidden_columns.concat($scope.shown_columns.splice(index, 1));
        }
      } else if (to_state == 'show') {
        for (var i=0; i < column_names.length; i++){
          var index = $scope.hidden_columns.indexOf(column_names[i]),
            shown_columns = $scope.shown_columns.concat($scope.hidden_columns.splice(index, 1));
          shown_columns.sort(sorter);
          $scope.shown_columns = shown_columns;
        }
      }
    }

    $scope.changeOrder = function(column_names, direction){
      for (var i = 0; i < column_names.length; i++){
        var index = $scope.shown_columns.indexOf(column_names[i]),
          new_index = direction == 'down' && index+1 || direction == 'up' && index-1;
          tmp = $scope.shown_columns[new_index];
        $scope.shown_columns[new_index] = $scope.shown_columns[index];
        $scope.shown_columns[index] = tmp;
      }
    }

    $scope.newSearch = function(query){
      if (query == undefined || query == '') return;

      var new_search = new SearchQueries({query: query});
      new_search.$save(function(new_query){
        $scope.search_queries.push(new_query);
      });
      $scope.new_search_query = '';
    }

    $scope.deleteSearch = function(_id){
      SearchQueries.delete({_id:_id});
      var i = 0;
      while ($scope.search_queries[i].id != _id) i++;
      $scope.search_queries.splice(i, 1);
    }

    $scope.applyQuery = function(query){
      $scope.query = query;
    }
}

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
        /* element will be positioned below $x */
    }
})
