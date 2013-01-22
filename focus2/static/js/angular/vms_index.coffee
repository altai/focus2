module = angular.module('VMSSearch', []);
module.directive 'openDialog',  () ->
  (scope, element, attrs) ->
    id = attrs['open-dialog']
    $('#' + id).modal()


