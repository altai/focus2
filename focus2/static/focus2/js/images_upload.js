var module = angular.module('instances_spawn', ["common", "ui"]);

function basename(path) {
    return path.replace(/\\/g,'/').replace( /.*\//, '' );
}

function SpawnController($scope){
    $scope.form = {};
    $scope.form.image_type = "solid";
    $scope.form.solid_image = "";

    $scope.file_select = function (field_name) {
        var btn = $("#btn_" + field_name);
        mode = btn.text().toLowerCase();
        if (mode == "url") {
            $("#file_" + field_name).trigger("click");
            $scope.form[field_name] = "";
            mode = "File";
        } else {
            $scope.form[field_name] = "";
            mode = "URL";
        }
        btn.text(mode);
    }
    $("input[type=file]").change(function () {
        var $this = $(this);
        var field_name = $this.attr("id").substring(5);
        $scope.$apply(function(scope) {
            scope.form[field_name] = "file: " + basename($this.val());
        });
    });
}
