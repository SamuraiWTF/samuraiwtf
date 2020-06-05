function runAndWaitForAction(action, module, href, message) {
    axios.get('/'+action+'/'+module).then(function (response) {
        console.log("Success!");
        console.log(response);
        renderActionsForStatus(response.data.name, response.data.status, href, message);
        pollForStatus(() => {
            return axios.get('/status/' + module);
            }).then(data => {
                renderActionsForStatus(data.name, data.status, href, "", data.actions);
                renderName(data.name, data.status, href);
                document.getElementById("notifications").classList.add('is-hidden');
            }).catch(() => console.log('Polling failed.'));
     })
    .catch(function (error) {
        console.log(error);
    });
}


function startModule(event, name, href='') {
    setNotification("Starting module: " + name);
    runAndWaitForAction('start', name, href, 'Starting...');
}

function stopModule(event, name, href='') {
    setNotification("Stopping module: " + name);
    runAndWaitForAction('stop', name, href, 'Stopping...');
}

function installModule(event, name, href='') {
    setNotification("Installing module: " + name);
    runAndWaitForAction('install', name, href, 'Installing...');
}

function removeModule(event, name, href='') {
    setNotification("Removing module: " + name);
    runAndWaitForAction('remove', name, href, 'Removing...');
}

function setNotification(message) {
    console.log("Notification: " + message);
    let spinner = '<span class="icon"><i class="fas fa-sun fa-spin"></i></span>'
    let fullMessage = spinner + " " + spinner + " " + spinner + message + spinner + " " + spinner + " " + spinner;
    document.getElementById("notifications").innerHTML = fullMessage;
    document.getElementById("notifications").classList.remove('is-hidden');
}

// The polling status check
function pollForStatus(fn, timeout, interval) {
    var endTime = Number(new Date()) + (timeout || 120000);
    interval = interval || 3000;

    var checkCondition = function(resolve, reject) {
        var ajax = fn();
        // dive into the ajax promise
        ajax.then( function(response){
            // If the condition is met, we're done!
            if(response.data.status !== 'changing') {
                resolve(response.data);
            }
            // If the condition isn't met but the timeout hasn't elapsed, go again
            else if (Number(new Date()) < endTime) {
                setTimeout(checkCondition, interval, resolve, reject);
            }
            // Didn't match and too much time, reject!
            else {
                reject(new Error('timed out for ' + fn + ': ' + arguments));
            }
        });
    };

    return new Promise(checkCondition);
}


function renderActionsForStatus(module, status, href='', changeText="Busy...", actions) {
    let action_icons = [];
    let params = 'this, \''+module+'\'';
    if (href !== '') {
        params = 'this, \''+module+'\', \''+href+'\'';
    }

    if (status === 'not installed' && actions.includes('install')) {
        action_icons.push('<a onclick="installModule('+params+')" style="margin-left: 5px;"><i class="fas fa-download fa-lg" title="install"></i></a>');
    }
    if (status === 'stopped' && actions.includes('start')) {
        action_icons.push('<a onclick="startModule('+params+')" class="has-text-link" style="margin-left: 5px;"><i class="fas fa-running fa-lg" title="start"></i></a>');
    }
    if (status === 'running' && actions.includes('stop')) {
        action_icons.push('<a onclick="stopModule('+params+')" class="has-text-danger" style="margin-left: 5px;"><i class="fas fa-hand-paper fa-lg" title="stop"></i></a></span>');
    }
    if ((status === 'installed' || status === 'stopped') && actions.includes('remove')) {
        action_icons.push('<a onclick="removeModule('+params+')" class="has-text-grey" style="margin-left: 5px;"><i class="fas fa-minus-circle fa-lg" title="uninstall"></i></a>');
    }
    if (status === 'changing') {
        action_icons.push('<span class="icon"><i class="fas fa-sun fa-spin fa-lg" title='+changeText+'></i></span>');
    }

    document.getElementById(module+"-actions").innerHTML = action_icons.join('');

}

function renderName(module, status, href='') {
    let name_parts = [];

    if (href == '') {
        name_parts.push(module);
    } else {
        if (status === 'running') {
            name_parts.push('<a class="button is-link" href="'+href+'" target="_blank" title="'+status+'">Open '+module+'</a> <br />');
        } else {
            name_parts.push('<button class="button is-link" title="'+status+'" disabled>Open '+module+'</button> <br /> ')
        }

        name_parts.push('<div class="tags has-addons status-bar">');

        if (status === 'not installed') {
            name_parts.push('<span class="tag is-dark">Status</span><span class="tag is-light">'+status+' <a onclick="installModule(this, \''+module+'\', \''+href+'\')" style="margin-left: 5px;"><i class="fas fa-download" title="install"></i></a></span>');
        } else if (status === 'stopped') {
            name_parts.push('<span class="tag is-dark">Status</span><span class="tag is-danger">'+status+'<a class="has-text-light" onclick="startModule(this, \''+module+'\', \''+href+'\')" style="margin-left: 5px;"><i class="fas fa-running" title="run"></i></a></span></div>');
        } else if (status == 'running') {
            name_parts.push('<span class="tag is-dark">Status</span><span class="tag is-success">'+status+'</span></i></a></span></div>');
        } else {
            name_parts.push('<span class="tag is-dark">Status</span><span class="tag is-light">'+status+'</span>');
        }

        name_parts.push('</div>');
    }

    document.getElementById(module+"-name").innerHTML = name_parts.join('');

}

console.log("katana.js loaded.");