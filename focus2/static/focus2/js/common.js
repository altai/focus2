var module = angular.module('common', [])

module.filter('filesizeformat', function() {
    return function(sz) {
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
        return (sz / Math.pow(1024, pow_1024)).toFixed(2) +
            " " + suffixes[pow_1024 - 1];
    }
});

module.filter('fieldbyid', function() {
    return function(id, collection, field, id_field) {
        var c = window.data[collection];
        if (!id_field) {
            id_field = "id";
        }
        for (var i = c.length - 1; i >= 0; --i) {
            if (c[i][id_field] == id) {
                return c[i][field];
            }
        }
        return "";
    }
});


module.filter('diskformat', function() {
    return function(value) {
        var fmt = {
            "aki": "Amazon kernel image",
            "ari": "Amazon ramdisk image",
            "ami": "Amazon machine image",
        }
        return fmt[value] || value;
    }
});


function getHumanReadableLifespan(minutes) {
    // FIXME
    return 0;
    return (minutes).minutesAfter(new Date()).relative()
}


jQuery(function($) {
    $(".help-tooltip").tooltip();
    $("[rel=tooltip]").tooltip();
    if (typeof(Date.today) != "undefined") {
        $(".daterange").daterangepicker({
            ranges: {
                "Today": ["today", "today"],
                "Yesterday": ["yesterday", "yesterday"],
                "Last 7 Days": [Date.today().add({days: -6}), "today"],
                "Last 30 Days": [Date.today().add({days: -29}), "today"],
                "This Month": [Date.today().moveToFirstDayOfMonth(), Date.today().moveToLastDayOfMonth()],
                "Last Month": [Date.today().moveToFirstDayOfMonth().add({months: -1}), Date.today().moveToFirstDayOfMonth().add({days: -1})]
            }
        });
    }
});


/*
  Example:
  var qvalue = $.querystring('q', 'default-q-value');
 */
(function($){
    $.extend({
	querystring: function(name, dflt) {
	    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
	    return match && decodeURIComponent(match[1].replace(/\+/g, ' ')) || dflt;
	}
    });
})(jQuery);


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
