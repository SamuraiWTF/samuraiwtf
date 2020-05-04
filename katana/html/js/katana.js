
function startModule(event, name) {
    setNotification("Starting module: " + name);
    axios.get('/start/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function stopModule(event, name) {
    setNotification("Stopping module: " + name);
    axios.get('/stop/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function installModule(event, name) {
    setNotification("Installing module: " + name + ". This may take a few moments...");
    axios.get('/install/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function removeModule(event, name) {
    setNotification("Removing module: " + name + ".  This may take a few moments...");
    axios.get('/remove/'+name).then(function (response) {
        console.log("Success!");
        location.reload();  // TODO: change this to dynamically update status
    })
    .catch(function (error) {
        console.log(error);
    });
}

function setNotification(message) {
    console.log("Notification: " + message);
    let spinner = '<span class="icon"><i class="fas fa-sun fa-spin"></i></span>'
    let fullMessage = spinner + " " + spinner + " " + spinner + message + spinner + " " + spinner + " " + spinner;
    document.getElementById("notifications").innerHTML = fullMessage;
    document.getElementById("notifications").classList.remove('is-hidden');
}



console.log("katana.js loaded.");