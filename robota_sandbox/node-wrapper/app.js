(function() {

    const express = require("express");
    const app = express();
    const https = require("https");
    const fs = require("fs");

    var serverPort = 50199;
    if (process.argv[2] !== undefined)
        serverPort = process.argv[2];

    function preprocessRequest (request, response, next) {
        console.log(">>> " + request.path);
        next();
    }

    app.use(preprocessRequest)
    app.use(express.static(__dirname + "/app"));
    app.listen(serverPort);
    console.log("Server started on port " + serverPort);

})()
