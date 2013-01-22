#!/usr/bin/env node
var watchr = require('watchr');
var path = require('path');
var child_process = require('child_process');

watchr.watch({
    path: "./focus2/templates",
    listeners: {
        change: function(_, filePath, _, _){
            if (filePath.match(/\.haml$/)){
                var newFilePath = filePath.replace(/\.haml$/, '.html');
                var cmd = 'haml --format html5 ' + filePath + ' ' + newFilePath;
                child_process.exec(
                    cmd,
                    function (error, stdout, stderr) {
                        console.log(cmd)
                        console.log(stdout);
                        console.log(stderr);
                        if (error !== null) {
                            console.log('watchr exec error: ' + error);
                        }
                    })
            }
        }
    }
});
