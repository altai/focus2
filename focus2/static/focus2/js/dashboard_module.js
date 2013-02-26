var module = angular.module('dashboard_module', []);

module.directive('showWhenReady', function(){
    return function(scope, element, attrs){
        scope.$watch('show', function(){
            $(element).removeClass('hidden').show();
        })

    }
})

function DashboardController($scope, $http){
    $scope.groups = window.data.groups;
    $scope.cells = window.data.cells;

    // last line shows content, must be last
    $scope.show = true

    $scope.unpin = function(href){
        $http.post('/', {'href': href, 'employ': false}).success(function(){
            for (var i = 0; i < $scope.groups.length; i++){
                for (var j = 0; j < $scope.groups[i].links.length; j++){
                    if (href === $scope.groups[i].links[j].href){
                        $scope.groups[i].links[j].employed = false;
                        break;
                    }
                }
            }
            for (var i = 0; i < $scope.cells.length; i++){
                if (href === $scope.cells[i].href){
                    $scope.cells[i] = false;
                    break;
                }
            }
        })
    }

    $scope.pin = function(href){
        $http.post('/', {'href': href, 'employ': true}).success(function(){
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
                if ($scope.cells[i] == null){
                    $scope.cells[i] = {
                        href: link.href,
                        full_title: link.big_title,
                        img: link.big_url
                    };
                    break;
                }
            }
        })
    }

}
