var module = angular.module('instances_index', ['ngResource', 'ui']);

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

module.factory('Instances', function ($resource){
    return $resource('/instances/', {api_marker: 1})
});


module.controller('DefaultCtrl', function($scope, $compile, $routeParams, $resource, $http, Instances, SearchQueries, $location){
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
    // Inner variables
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
    var order = [ // Ultimate defaut columns order
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
    // Inner methods
    var sorter = function(a, b){ // Sorting rule, used as Array.sort callback
      return order.indexOf(a) - order.indexOf(b)
    };
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

    //scope manipulations
    $scope.updateQueries = function(){
          $scope.searchQueries = SearchQueries.query();
      };

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

    $scope.selectedControls = [];

    $scope.$watch('shownColumns', function(){
      $scope.unselectedControls = $scope.shownColumns.slice();
    }, true);

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

    $scope.buildQuery = function(query){
      console.log(query);
      console.log($scope);
    }
});

module.directive('createControl', function($compile, $timeout){
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

  return {
    link: function(scope, element, attrs){
      var template = '<label class="control-label">{}'+
                     '<a href="#" rel="tooltip" data-original-title="{}"><i class="icon-question-sign"></i></a></label>'+
                     '<div class="controls" style="vertical-align: top">{}'+
                     '<a ng-click="deleteControl(x)" style="float: right"><i class="icon-remove-sign"></i></a></div>';
      var tag;
      var html;
      attrs.$observe('createControl', function(){
        var control = controls[attrs.createControl];
        var modelName = attrs.createControl.replace(' ', '');
        scope.costFrom = 0;
        scope.costTo = 500;
        switch (controls[attrs.createControl]['type']){
          case 'text':
            tag = '<input type="text" ng-model="{}" placeholder="{}"/>'.format(
              Array(modelName, control['placeholder'])
              );
            break;
          case 'ip':
            var inputs = '';
            for (var i=0; i < 4; i++){
              inputs += '<input type="text" ng-model="df{}" class="ng-pristine ng-valid"/>'.format([modelName + i]);
            }
            tag = '<div class="cb-ip-widget">{}</div>'.format([inputs]);
            break;
          case 'date':
            tag = '<input type="text" ng-model="{}" class="daterange ng-pristine ng-valid" placeholder="{}"/>'.format(
              Array(modelName, control['placeholder']));
            break;
          case 'select':
            tag = '<select multiple ng-model="{}" class="select ng-pristine ng-valid">'+
                  '<option value="0">0</option>'+
                  '<option value="1">1</option>'+
                  '</select>';
            tag = tag.format([modelName]);
            break;
          case 'slider':
            tag = '<input type="text" class="slider" ng-model="costPerDay" value="0"/><div>Cost per day: ${{ costFrom }} - ${{ costTo }}</div>';
        }

        html = template.format(Array(control['title'], control['help'], tag));
        element.append(html);

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
    },
    controller: function($scope){
      console.log($scope.$parent);
      console.log($scope);
    }
  }
});

var template = 'partials/search.html';

module.config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/', {templateUrl: template, controller: 'DefaultCtrl'}).
        when('/:query', {templateUrl: template, controller: 'DefaultCtrl'}).
        when('/:query/:page/', {templateUrl: template, controller: 'DefaultCtrl'}).
        when('/:query/:page/:columns', {templateUrl: template, controller: 'DefaultCtrl'}).
        when('/:query/:page/:columns/:perPage', {templateUrl: template, controller: 'DefaultCtrl'}).
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
