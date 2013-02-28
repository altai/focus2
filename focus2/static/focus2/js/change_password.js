var module = angular.module('change_password', ["common"]);

function ChangePasswordController($scope){
    $scope.new_password = '';
    $scope.confirm_password = '';

    $scope.wha = function() {
        return $scope.new_password == $scope.confirm_password;
    }

    $scope.password_match = function() {
        return $scope.wha() && ($scope.new_password != '');
    }

    $scope.too_short = function() {
        return $scope.new_password.length < 6;
    }

    $scope.$on('hideAllWindows', function(){

    });
}
