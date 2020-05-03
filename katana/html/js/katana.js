
function startModule(event, name) {
    console.log("Starting module: " + name);
    axios.get('/start/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function stopModule(event, name) {
    console.log("Stopping module: " + name);
    axios.get('/stop/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function installModule(event, name) {
    console.log("Installing module: " + name);
    axios.get('/install/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function removeModule(event, name) {
    console.log("Removing module: " + name);
    axios.get('/remove/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}


console.log("katana.js loaded.");