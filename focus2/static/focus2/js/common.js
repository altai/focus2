var module = angular.module('common', [])

function getHumanReadableSizeBytes(sz) {
    var suffixes = [
        "KiB",
        "MiB",
        "GiB",
        "TiB",
    ];
    var pow_1024 = Math.floor((Math.log(sz) / Math.LN2 / 10));
    if (pow_1024 < 1) {
        return sz + " B";
    }
    return (sz / Math.pow(1024, pow_1024)).toFixed(2) + " " + suffixes[pow_1024 - 1];
}

function getHumanReadableLifespan(minutes) {
    return (minutes).minutesAfter(new Date()).relative()
}

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
        scope.human_readable_lifespan = getHumanReadableLifespan(init)
    }
})
