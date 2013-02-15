var module = angular.module('common', [])

module.filter('filesizeformat', function() {
    return function(sz) {
        var suffixes = [
            "KiB",
            "MiB",
            "GiB",
            "TiB",
        ];
        console.log(sz);
        var pow_1024 = Math.floor((Math.log(sz) / Math.LN2 / 10));
        if (pow_1024 < 1) {
            return sz + " B";
        }
        return (sz / Math.pow(1024, pow_1024)).toFixed(2) +
            " " + suffixes[pow_1024 - 1];
    }
});

function getHumanReadableLifespan(minutes) {
    return (minutes).minutesAfter(new Date()).relative()
}


jQuery(function($) {
    $(".select2").each(function () {
        var options = {};
        var $this = $(this);
        options.allowClear = (typeof($this.attr("allow-clear")) != undefined);
        $this.select2(options);
    });                       
});

module.directive('slider', function(){
    return function(scope, element, attrs){
        var init = 10000
        $(element).slider({
            range: "max",
            min: 1,
            max: 100500,
            value: init,
            slide: function( event, ui ) {
                scope.$apply('human_readable_lifespan="' + getHumanReadableLifespan(ui.value) + '"')
            }
        })
        scope.human_readable_lifespan = getHumanReadableLifespan(init);
    }
});
