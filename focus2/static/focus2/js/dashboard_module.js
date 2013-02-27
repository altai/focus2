'use strict';

var module = angular.module('dashboard_module', []);

module.directive('showWhenReady', function(){
    return function(scope, element, attrs){
        scope.$watch('show', function(){
            $(element).removeClass('hidden').show();
        })

    }
})

module.directive('eatClick', function() {
    return function(scope, element, attrs) {
        $(element).click(function(event) {
            event.preventDefault();
        });
    }
})

module.directive('dragFromLeft', function(){
    return function(scope, element, attrs){
        var link = scope.$eval(attrs.dragFromLeft);
        $(element).draggable({
            helper: function (){
                return $(this).clone().
                    css('width', '130px').
                    css('height', '20px').
                    css('background-color', '#dddddd').
                    css('padding', '10px 10px 10px 20px');
            },
            containment: '.all-links',
            appendTo: "body",
            scope: "cells",
            revert: "invalid"
        }).data('link', link);
    }
})

module.directive('dropFromLeft', function($http){
    return function(scope, element, attrs){
        $(element).data('index', parseInt(scope.$eval('$index'))).droppable({
            scope: "cells",
            drop: function(event, ui){
                var link = ui.draggable.data('link'); // set when dragged from the left
                var cell = ui.draggable.data('cell');
                var index = scope.$eval('$index')
                for (var i = 0; i < scope.cells.length; i++){
                    var x = scope.cells[i];
                    if (x){
                        if (link && link.href == x.href) return;
                    }
                }
                if (link){
                    // dragged from the left
                    var existing_cell = scope.$eval('cells[' + index + ']');
                    if (existing_cell){
                        // there was something and we dragged another something from link list at the left
                        var cmd = 'cells[' + index + '] = false';
                        scope.$apply(cmd);
                        for (var i = 0; i < scope.groups.length; i++){
                            for (var j = 0; j < scope.groups[i].links; j++){
                                if (existing_cell.href == scope.groups[i].links[j].href){
                                    scope.$apply('groups[' + i + '].links[' + j + '].href.employed = false')
                                }
                            }
                        }
                        $http.post('/', {changes: [
                            {
                                href: existing_cell.href,
                                index: null
                            }
                        ]})
                    } else {
                        // we dragged something from link list at the left
                        // and nothing to do on this level
                    }
                    link.employed = true;
                    var cmd = 'cells[' + index + '] = {href: \'' + link.href + '\', img: \'' + link.big_url + '\', full_title: \'' + link.big_title  + '\'}';
                    scope.$apply(cmd);
                    
                    $http.post('/', {changes: [
                            {
                                href: link.href,
                                index: index
                            }
                        ]})
                } else if (cell) {
                    // dragged from another cell
                    var target_cell = scope.$eval('cells[' + index + ']');
                    if (target_cell){
                        var cmd = 'cells[' + ui.draggable.data('index') + '] =  {href: \'' + target_cell.href + '\', img: \'' + target_cell.img + '\', full_title: \'' + target_cell.full_title  + '\'}';
                    } else {
                        var cmd = 'cells[' + ui.draggable.data('index') + '] = false;'
                    }
                    scope.$apply(cmd);
                    
                    var cmd = 'cells[' + index + '] = {href: \'' + cell.href + '\', img: \'' + cell.img + '\', full_title: \'' + cell.full_title  + '\'}';
                    scope.$apply(cmd)
                    if (target_cell){
                        $http.post('/', {changes: [
                            {
                                href: cell.href,
                                index: index
                            },
                            {
                                href: target_cell.href,
                                index: ui.draggable.data('index')
                            }
                        ]})
                    } else {
                        $http.post('/', {changes: [
                            {
                                href: cell.href,
                                index: index
                            }
                        ]})
                    }
                }
            },
            hoverClass: 'drop-hover'
        });
    }
})

module.directive('draggableCell', function(){
    return function(scope, element, attrs){
        $(element).
            draggable({
                scope: "cells",
                containment: '.quick-links',
                appendTo: 'body',
                revert: "invalid",
                stack: 'a.thumbnail'
            }).
            data('cell', scope.$eval('cell')).
            data('index', scope.$eval('$index'));
    }
})

function DashboardController($scope, $http){
    $scope.groups = window.data.groups;
    $scope.cells = window.data.cells;

    $scope.unpin = function(href){
        for (var i = 0; i < $scope.groups.length; i++){
            for (var j = 0; j < $scope.groups[i].links.length; j++){
                if (href === $scope.groups[i].links[j].href){
                    $scope.groups[i].links[j].employed = false;
                    break;
                }
            }
        }
        for (var i = 0; i < $scope.cells.length; i++){
            if ($scope.cells[i] && href === $scope.cells[i].href){
                $scope.cells[i] = false;
                break;
            }
        }
        $http.post('/', {'href': href, 'employ': false});
    }

    $scope.pin = function(href){
        for (var i = 0; i < $scope.cells.length; i++){
            if ($scope.cells[i] && $scope.cells[i].href == href) return;
        }
        var link;
        for (var i = 0; i < $scope.groups.length; i++){
            for (var j = 0; j < $scope.groups[i].links.length; j++){
                if (href === $scope.groups[i].links[j].href){
                    $scope.groups[i].links[j].employed = true;
                    link = $scope.groups[i].links[j]
                    break;
                }
            }
        }
        for (var i = 0; i < $scope.cells.length; i++){
            if (!$scope.cells[i]){
                $scope.cells[i] = {
                    href: link.href,
                    full_title: link.big_title,
                    img: link.big_url
                };
                break;
            }
        }
        $http.post('/', {'href': href, 'employ': true});
    }

    $scope.show = true; // last line shows content, must be last
}
