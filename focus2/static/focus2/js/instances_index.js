var inadequateArgumentNumber = function(parts, args){
  return 'Arguments and format fields length must be equal. Instead: args is ' + args.length + ', fields is ' + parts.length};

// TODO: move all format on the side of good
// WARNING: global prototype modification. Fix it!
String.prototype.format = function(args){
  console.log('ARGS', args);
  var parts = this.split('{}');
  if (parts.length-1 != args.length){
    throw inadequateArgumentNumber(parts, args);
  }
  for (var i=0; i < args.length; i++){
    parts[i] = parts[i]+args[i];
  }
  return parts.join('');
}

var module = angular.module('instances_index', ['ngResource', 'ui'],
    function($compileProvider){
      $compileProvider.directive('createControl', function($compile, $timeout){
        var controls = {
           'Name': {title: 'Name', help:'help', placeholder: 'Enter name', type: 'text'},
           'Ping Test': {title: 'Ping Test', help:'help', placeholder: 'Choose state', type: 'select'},
           'Id': {title: 'Id', help:'help', placeholder: 'Enter ID', type: 'select'},
           'Cost Per Day': {title: 'Cost Per Day', help:'help', placeholder: 'Limit per day cost', type: 'slider'},
           'IP': {title: 'IP', help:'help', placeholder: 'Enter title', type: 'ip'},
           'Created': {title: 'Created', help:'help', placeholder: 'Enter creation date', type: 'date'},
           'Project': {title: 'Project', help:'help', placeholder: 'Enter project name', type: 'select'},
           'User': {title: 'User', help:'help', placeholder: 'Enter user name', type: 'text'},
           'Image': {title: 'Image', help:'help', placeholder: 'Enter image name', type: 'select'},
           'Type': {title: 'Type', help:'help', placeholder: 'Enter type', type: 'select'}
        };

        return function(scope, element, attrs){
          var template = '<label class="control-label">{}'+
                         '<a href="#" rel="tooltip" data-original-title="{}"><i class="icon-question-sign"></i></a></label>'+
                         '<div class="controls" style="vertical-align: top">{}'+
                         '<a ng-click="deleteControl(x)" style="float: right"><i class="icon-remove-sign"></i></a></div>';
          var tag;
          var html;
          attrs.$observe('createControl', function(){
            var control = controls[attrs.createControl]
            switch (controls[attrs.createControl]['type']){
              case 'text':
                tag = '<input type="text" ng-model="{}" placeholder="{}"/>'.format(
                  Array(attrs.createControl, control['placeholder'])
                  );
                break;
              case 'ip':
                var inputs = '';
                for (var i=0; i < 4; i++){
                  inputs += '<input type="text" ng-model="df{}" class="ng-pristine ng-valid"/>'.format([i]);
                }
                tag = '<div class="cb-ip-widget">{}</div>'.format([inputs]);
                break;
              case 'date':
                tag = '<input type="text" ng-model="date" class="daterange ng-pristine ng-valid" placeholder="{}"/>'.format(
                  Array(control['placeholder']));
                break;
              case 'select':
                tag = '<select ng-model="{}" placeholder="{}" class="chzn-select ng-pristine ng-valid">'+
                      '<option value="0">0</option><option value="1">1</option>'+
                      '</select>';
                tag = tag.format(Array(attrs.createControl.replace(' ', ''), control['placeholder']));
                break;
            }

            html = template.format(Array(control['title'], control['help'], tag));
            element.append(html);
            $compile(element.contents())(scope);
            $('.daterange').daterangepicker({
                      ranges: {
                       'Today': ['today', 'today'],
                       'Yesterday': ['yesterday', 'yesterday'],
                       'Last 7 Days': [Date.today().add({ days: -6 }), 'today'],
                       'Last 30 Days': [Date.today().add({ days: -29 }), 'today'],
                       'This Month': [Date.today().moveToFirstDayOfMonth(), Date.today().moveToLastDayOfMonth()],
                       'Last Month': [Date.today().moveToFirstDayOfMonth().add({ months: -1 }), Date.today().moveToFirstDayOfMonth().add({ days: -1 })]
                       }
                    }
              );
            // FIXME: have no chosen method
            $('.chzn-select').chosen();
          })
        }
      })
    });
var template = 'partials/search.html';

module.factory('Instances', function ($resource){
    return $resource('/instances/', {api_marker: 1})
});

module.factory('SearchQueries', function ($resource){
  return $resource('/instances/searches/:_id', {_id: '@id'});
})

function DefaultCtrl($scope, $compile, $routeParams, $resource, $http, Instances, SearchQueries, $location){
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
        columnsDefinitions = {
       'Name': 'name',
       'Ping Test': 'state',
       'Id': 'id',
       'Cost Per Day': 'cost',
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
      inadequateArgumentNumber = function(parts, args){
        return 'Arguments and format fields length must be equal. Instead: args is ' + args.length + ', fields is ' + parts.length},

       format = function(string, args){
             var parts = string.split('{}');
             if (parts.length-1 != args.length){
               throw inadequateArgumentNumber(parts, args);
             }
             for (var i=0; i < args.length; i++){
               parts[i] = parts[i]+args[i];
             }
             return parts.join('');
       },
       sorter = function(a, b){return order.indexOf(a) - order.indexOf(b)},
       toDataItem = function(data_item){
         this.format = format;

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

    $scope.updateQueries = function(){
          $scope.searchQueries = SearchQueries.query();
      };

    $scope.query = params.query;
    $scope.page = params.page;
    $scope.columns = params.columns;
    $scope.perPage = params.perPage;
    $scope.perPageChoices = [10, 20, 50, 100];
    $scope.shownColumns = order.slice();
    $scope.hiddenColumns = [];
    $scope.instances = Instances.get(params);

    $scope.updateLocation = function(){
        if ($scope.perPage != defaults.perPage){
            $location.path($scope.query + '/' + $scope.page + '/' + $scope.columns.join() + '/' + $scope.perPage);
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

    $scope.changePage = function(page){
        $scope.page = page;
        $scope.update_location();
    }

    $scope.columnsData = function(name, row){
      var data_item = row.hasOwnProperty(columnsDefinitions[name]) ? row[columnsDefinitions[name]] : '';
      data_item = new toDataItem(data_item);
      if (data_item.isLink()){return data_item.toLink();}
      else if (data_item.isPingState()){return data_item.toPingTestState();}
      else {return data_item.toSimpleString();}
    }

    $scope.visibility = {
      'column_editor': false,
      'saved_searches': false,
      'builder': false
    }

    $scope.toggleVisibility = function(node){
      $scope.visibility[node] = !$scope.visibility[node];
    }

    $scope.horizontalDisplace = function(column_names, to_state){
      if (to_state == 'hide'){
        for (var i=0; i < column_names.length; i++){
          var index = $scope.shownColumns.indexOf(column_names[i]);
          $scope.hiddenColumns = $scope.hiddenColumns.concat($scope.shownColumns.splice(index, 1));
        }
      } else if (to_state == 'show') {
        for (var i=0; i < column_names.length; i++){
          var index = $scope.hiddenColumns.indexOf(column_names[i]),
            shownColumns = $scope.shownColumns.concat($scope.hiddenColumns.splice(index, 1));
          shownColumns.sort(sorter);
          $scope.shownColumns = shownColumns;
        }
      }
    }

    $scope.changeOrder = function(column_names, direction){
      for (var i = 0; i < column_names.length; i++){
        var index = $scope.shownColumns.indexOf(column_names[i]),
          new_index = direction == 'down' && index+1 || direction == 'up' && index-1;
          tmp = $scope.shownColumns[new_index];
        $scope.shownColumns[new_index] = $scope.shownColumns[index];
        $scope.shownColumns[index] = tmp;
      }
    }

    $scope.newSearch = function(query){
      if (query == undefined || query == '') return;

      var new_search = new SearchQueries({query: query});
      new_search.$save(function(new_query){
        $scope.searchQueries.push(new_query);
      });
      $scope.new_search_query = '';
    }

    $scope.deleteSearch = function(_id){
      SearchQueries.delete({_id:_id});
      var i = 0;
      while ($scope.searchQueries[i].id != _id) i++;
      $scope.searchQueries.splice(i, 1);
    }

    $scope.applyQuery = function(query){
      $scope.query = query;
    }



    $scope.$watch('shownColumns', function(){
      $scope.unselectedControls = $scope.shownColumns.slice();
    }, true);

    $scope.selectedControls = [];

    $scope.addControl = function(control){
      var index = $scope.unselectedControls.indexOf(control);
      $scope.selectedControls = $scope.selectedControls.concat(
          $scope.unselectedControls.splice(index, 1)
          );
    }

    $scope.deleteControl = function(control){
      $scope.unselectedControls = $scope.unselectedControls.concat(
          $scope.selectedControls.splice(index, 1)
          );
    }

    $scope.useBuiltQuery = function(query){
      // TODO: implement it!
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
