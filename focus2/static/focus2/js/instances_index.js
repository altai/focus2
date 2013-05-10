var inadequateArgumentNumber = function(parts, args){
  return 'Arguments and format fields length must be equal. Instead: args is ' + args.length + ', fields is ' + parts.length};

// TODO: move all format on the side of good
// WARNING: global prototype modification. Fix it!
String.prototype.format = function(args){
  var parts = this.split('{}');
  if (parts.length-1 != args.length){
    throw inadequateArgumentNumber(parts, args);
  }
  for (var i=0; i < args.length; i++){
    parts[i] = parts[i]+args[i];
  }
  return parts.join('');
}

var module = angular.module('instances_index', ['ngResource', 'ui']);

// Run blocks. Module initialization
module.run(function($rootScope){
  $rootScope.visibility = {
      'column_editor': false,
      'saved_searches': false,
      'builder': false
    };
  $rootScope.order = [
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
    ];
  $rootScope.shownColumns = $rootScope.order.slice();
  $rootScope.hiddenColumns = [];
});

// Services
module.factory('Instances', function($resource){
    return $resource('/instances/', {api_marker: 1})
});

module.factory('SearchQueries', function($resource){
  return $resource('/instances/searches/:_id', {_id: '@id'});
});

module.factory('applyQuery', function($rootScope){
  return function(newQuery){
    $rootScope.query = newQuery;
  }
});

module.factory('visibility', function($rootScope){
  return {
    get: $rootScope.visibility,
    toggle: function(node){
      $rootScope.visibility[node] = !$rootScope.visibility[node];
      }
  }
});

module.factory('sorter', function($rootScope){
  return function(a, b){
      return $rootScope.order.indexOf(a) - $rootScope.order.indexOf(b)
    };
});

module.factory('columnsResource', function($rootScope, sorter){
  return {
    show: function(column_name){
      var index = $rootScope.hiddenColumns.indexOf(column_name);
      var shownColumns = $rootScope.shownColumns.concat($rootScope.hiddenColumns.splice(index, 1));
      shownColumns.sort(sorter);
      $rootScope.shownColumns = shownColumns;
      },
    hide: function(column_name){
      var index = $rootScope.shownColumns.indexOf(column_name);
      $rootScope.hiddenColumns = $rootScope.hiddenColumns.concat(
          $rootScope.shownColumns.splice(index, 1)
        );
      },
    move: function(index_offset, column_name){
        var index = $rootScope.shownColumns.indexOf(column_name);
        var new_index = index+index_offset;
        var tmp = $rootScope.shownColumns[new_index];
        $rootScope.shownColumns[new_index] = $rootScope.shownColumns[index];
        $rootScope.shownColumns[index] = tmp;
    },
    down: function(column_name){
      return this.move(1, column_name);
    },
    up: function(column_name){
      return this.move(-1, column_name);
    },
    copy: function(){
      return $rootScope.shownColumns.slice();
    },
    get: {
      shown: $rootScope.shownColumns,
      hidden: $rootScope.hiddenColumns
    }
    }
});

// Controllers
module.controller('Location', function($scope, $routeParams, $location, applyQuery){
    /* add func to update scope after an object */

    var defaults = { // Default scope values
        query: '',
        page: 1,
        columns: [],
        perPage: 10
    };
    var params = {
        query: $routeParams.query || defaults.query,
        page: parseInt($routeParams.page) || defaults.page,
        columns: $routeParams.columns || defaults.columns,
        perPage: parseInt($routeParams.perPage) || defaults.perPage,
    };

    $scope.query = applyQuery(params.query);
    $scope.page = params.page;
    $scope.columns = params.columns;
    $scope.perPage = params.perPage;
    $scope.perPageChoices = [10, 20, 50, 100];

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

    $scope.applyQuery = applyQuery;
});

module.controller('SearchQueryEditor', function($scope, SearchQueries){
    $scope.searchQueries = SearchQueries.query();

    $scope.addQuery = function(query){
      if (query == undefined || query == '') return;

      var new_search = new SearchQueries({query: query});

      new_search.$save(function(new_query){
        new_query.$get(
            function(r){
              $scope.searchQueries.push(r);
            });
     });

      $scope.newSearchQuery = '';
    }

    $scope.deleteQuery = function(_id){
      SearchQueries.delete({_id:_id});
      var i = 0;
      while ($scope.searchQueries[i].id != _id) i++;
      $scope.searchQueries.splice(i, 1);
    }
})

module.controller('Button', function($scope, visibility){
  $scope.toggleVisibility = visibility.toggle;
  $scope.visibility = visibility.get;
});

module.controller('ColumnsEditor', function($scope, visibility, columnsResource){
    $scope.horizontalDisplace = function(column_names, to_state){
      if (to_state == 'hide'){
        for (var i=0; i < column_names.length; i++){
          columnsResource.hide(column_names[i])
        }
      } else if (to_state == 'show') {
        for (var i=0; i < column_names.length; i++){
          columnsResource.show(columns_names[i])
        }
      }
    }

    $scope.changeOrder = function(column_names, direction){
      for (var i = 0; i < column_names.length; i++){
        if (direction=='down'){
          columnsResource.down(column_names[i]);
        } else if (direction=='up'){
          columnsResource.up(column_names[i]);
        }
      }
    }
});

module.directive('ColumnsData', function(){
// TODO: implement ColumnData as directive
})

module.controller('ColumnsData', function($scope, Instances){
    var toDataItem = function(data_item){ // Data item type/constructor function
        this.data_item = this.data_item;
        this.isLink = function(){
          return typeof this.data_item == 'object' &&
            'href' in this.data_item &&
            'id' in this.data_item &&
            'name' in this.data_item;
        }

        this.toLink = function(){
          args = [];
          for (i in this.data_item){
            args.push(data_item[i]);
          }
          string = '<a href={} id={}>{}</a>';
          return string.format(args);
        }

        this.isPingState = function(){
          return typeof this.data_item == "string" &&
            this.data_item == this.data_item.toUpperCase() &&
            !Date.parse(data_item) &&
            this.data_item.length;
        }

        this.toPingTestState = function(){
          args = this.data_item == 'ERROR' ? ['red']: ['green'];
          string = '<div style="margin: 10px; width: 20px; height: 20px; background-color: {};text-indent: -100px; border-radius: 10px; overflow: hidden;"></div>';
          return string.format(args);
        }

        this.toSimpleString = function(){
          if (typeof this.data_item == "string"){
            string = '<span>{}</span>';
            args = [data_item];
          } else {
            string = '<span>' + Array(data_item.length).join('{}\n') + '</span>';
            args = this.data_item;
          }
          return string.format(args);
        }
    };
    var columnsDefinitions = { // Definition columns control
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
    };

    $scope.instances = Instances();

    $scope.columnsData = function(name, row){
      var data_item = row.hasOwnProperty(columnsDefinitions[name]) ? row[columnsDefinitions[name]] : '';
      data_item = new toDataItem(data_item);
      if (data_item.isLink()){return data_item.toLink();}
      else if (data_item.isPingState()){return data_item.toPingTestState();}
      else {return data_item.toSimpleString();}
    }
});

module.controller('QueryBuilder', function($scope, visibility, columnsResource, sorter){
  $scope.visibility = visibility.get;
  $scope.toggleVisibility = visibility.toggle;
  $scope.selectedControls = [];
  $scope.unselectedControls = columnsResource.copy();

  $scope.$watch('unselectedControls', function(){
    $scope.unselectedControls.sort(sorter);
  })

  $scope.addControl = function(control){
    var index = $scope.unselectedControls.indexOf(control);
    $scope.selectedControls = $scope.selectedControls.concat(
        $scope.unselectedControls.splice(index, 1)
        );
  }

  $scope.deleteControl = function(control){
    var index = $scope.selectedControls.indexOf(control);
    $scope.unselectedControls = $scope.unselectedControls.concat(
        $scope.selectedControls.splice(index, 1)
        );
  }
  $scope.buildQuery = function(){
    $rootScope.query = $rootScope.rawQuery;
  }
})

module.directive('createControl', function($compile, $timeout){
  var controls = {
     'Name': {
       title: 'Name',
       help:'help',
       placeholder: 'Enter name',
       type: '<input type="text" ng-model="{}" placeholder="{}"/>'},
     'Ping Test': {
       title: 'Ping Test',
       help:'help',
       placeholder: 'Choose state',
       type: 'select'},
     'Id': {
       title: 'Id',
       help:'help',
       placeholder: 'Enter ID',
       type: 'select'},
     'Cost Per Day': {
       title: 'Cost Per Day',
       help:'help',
       placeholder: 'Limit per day cost',
       type: 'slider'},
     'IP': {
       title: 'IP',
       help:'help',
       placeholder: 'Enter title',
       type: 'ip'},
     'Created': {
       title: 'Created',
       help:'help',
       placeholder: 'Enter creation date',
       type: 'date'},
     'Project': {
       title: 'Project',
       help:'help',
       placeholder: 'Enter project name',
       type: 'select'},
     'User': {
       title: 'User',
       help:'help',
       placeholder: 'Enter user name',
       type: 'text'},
     'Image': {
       title: 'Image',
       help:'help',
       placeholder: 'Enter image name',
       type: 'select'},
     'Type': {
       title: 'Type',
       help:'help',
       placeholder: 'Enter type',
       type: 'select'}
  };
  var scope = {
      createControl: '@',
      Name: '@',
      PingTest: '@',
      ID: '@',
      CostPerDay: '@',
      IP1: '@',
      IP2: '@',
      IP3: '@',
      IP4: '@',
      Created: '@',
      Project: '@',
      User: '@',
      Image: '@',
      Type: '@'
    };
  var link = function(scope, element, attrs){
      attrs.$observe('createControl', function(){
        var control = controls[attrs.createControl];
        var modelName = attrs.createControl.replace(' ', '');
        var text_input = '<input type="text" ng-model="{{ name }}" placeholder="{{ placeholder }}"/>';
        var ip_wizard = function(){
            var inputs = '';
            for (var i=0; i < 4; i++){
              inputs += '<input type="text" ng-model="IP{}" class="ng-pristine ng-valid"/>'.format([modelName + i]);
            }
            return '<div class="cb-ip-widget">{}</div>'.format([inputs]);
          };
        var datePicker = '<input type="text" ng-model="{{ name }}" class="daterange ng-pristine ng-valid" placeholder="{{ placeholder }}"/>';
        var select = '<select multiple ng-model="{{ name }}" class="select ng-pristine ng-valid">'+
                  '<option value="0">0</option>'+
                  '<option value="1">1</option>'+
                  '</select>';
        var slider = '<input type="text" class="slider" ng-model="costPerDay" value="0"/><div>Cost per day: ${{ costFrom }} - ${{ costTo }}</div>';

        scope.costFrom = 0;
        scope.costTo = 500;
        switch (control['type']){
          case 'text':
            $compile(text_input)(control);
            break;
          case 'ip':
            $compile(ip_wizard)(control);
            break;
          case 'date':
            $compile(datePicker)(control);
            break;
          case 'select':
            $compile(select)(control);
            break;
          case 'slider':
            $compile(slider)({costFrom: scope.costFrom, costTo: scope.costTo});
        };

        // TODO: render template with control dependencies
        $compile(template)(control);

        element.find('.daterange').daterangepicker({
                  ranges: {
                   'Today': ['today', 'today'],
                   'Yesterday': ['yesterday', 'yesterday'],
                   'Last 7 Days': [Date.today().add({ days: -6 }), 'today'],
                   'Last 30 Days': [Date.today().add({ days: -29 }), 'today'],
                   'This Month': [Date.today().moveToFirstDayOfMonth(), Date.today().moveToLastDayOfMonth()],
                   'Last Month': [Date.today().moveToFirstDayOfMonth().add({ months: -1 }), Date.today().moveToFirstDayOfMonth().add({ days: -1 })]
                   }
            });
        element.find('.select').select2({
              placeholder: control['placeholder']
            });
        element.find('.slider').slider({
              max: 500,
              orientation: 'horizontal',
              selection: 'after',
              handle: 'squere',
              value: [scope.costFrom, scope.costTo]
        }).on('slide', function(e){
          scope.$apply(function(){
            scope.costFrom = e.value[0];
            scope.costTo = e.value[1];
          });
        });
        $compile(element.contents())(scope);
      })
    };
   var template = '<label class="control-label">{{ title }}'+
                  '<a href="#" rel="tooltip" data-original-title="{{ help }}"><i class="icon-question-sign"></i></a></label>'+
                  '<div class="controls" style="vertical-align: top">{{ tag }}'+
                  '<a ng-click="deleteControl(\'{{ title }}\')" style="float: right"><i class="icon-remove-sign"></i></a></div>';

  return {
    transclude: true,
    restrict: 'A',
    scope: scope,
    template: template,
    link: link
  }
});

var template = 'partials/search.html';

module.config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/', {templateUrl: template, controller: 'Location'}).
        when('/:query', {templateUrl: template, controller: 'Location'}).
        when('/:query/:page/', {templateUrl: template, controller: 'Location'}).
        when('/:query/:page/:columns', {templateUrl: template, controller: 'Location'}).
        when('/:query/:page/:columns/:perPage', {templateUrl: template, controller: 'Location'}).
        otherwise({redirectTo: '/'});
}])

module.directive('floatAround', function(){
    /* keeps the element around target element */
    return function(scope, element, attrs){
        var $x = $(attrs.floatAround);
        /* element will be positioned below $x */
    }
})
