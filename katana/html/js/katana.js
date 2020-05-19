
function startModule(event, name) {
    setNotification("Starting module: " + name);
    axios.get('/start/'+name).then(function (response) {
        console.log("Success!");
        console.log(response);
        renderActionsForStatus(response.data.name, response.data.status, "Starting...");
//        location.reload();  // TODO: change this to dynamically update status
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

function renderActionsForStatus(module, status, changeText="Busy...") {
    let action_icons = [];
    if (status === 'not installed') {
        action_icons.push('<a onclick="installModule(this, \''+module+'\')" style="margin-left: 5px;"><i class="fas fa-download fa-lg" title="install"></i></a>');
    }
    if (status === 'stopped') {
        action_icons.push('<a onclick="startModule(this, \''+module+'\')" class="has-text-link" style="margin-left: 5px;"><i class="fas fa-running fa-lg" title="start"></i></a>');
    }
    if (status === 'running') {
        action_icons.push('<a onclick="stopModule(this, \''+module+'\')" class="has-text-danger" style="margin-left: 5px;"><i class="fas fa-hand-paper fa-lg" title="stop"></i></a></span>');
    }
    if (status === 'installed' || status === 'stopped') {
        action_icons.push('<a onclick="removeModule(this, \''+module+'\')" class="has-text-grey" style="margin-left: 5px;"><i class="fas fa-minus-circle fa-lg" title="uninstall"></i></a>');
    }
    if (status === 'changing') {
        action_icons.push('<span class="icon"><i class="fas fa-sun fa-spin" title='+changeText+'></i></span>');
    }

    document.getElementById(module+"-actions").innerHTML = action_icons.join('');

}

//  def render_actions_for_status(self, status, module):
//        action_icons = []
//        if status == 'not installed':
//            action_icons.append(
//                f'<a onclick="installModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-download fa-lg" title="install"></i></a>')
//        if status == 'stopped':
//            action_icons.append(
//                f'<a onclick="startModule(this, \'{module}\')" class="has-text-link" style="margin-left: 5px;"><i class="fas fa-running fa-lg" title="start"></i></a>')
//        if status == 'running':
//            action_icons.append(
//                f'<a onclick="stopModule(this, \'{module}\')" class="has-text-danger" style="margin-left: 5px;"><i class="fas fa-hand-paper fa-lg" title="stop"></i></a></span>')
//        if status == 'installed' or status == 'stopped':
//            action_icons.append(
//                f'<a onclick="removeModule(this, \'{module}\')" class="has-text-grey" style="margin-left: 5px;"><i class="fas fa-minus-circle fa-lg" title="uninstall"></i></a>')
//        all_actions = ''.join(action_icons)
//        return f'<p class="control">{all_actions}</p>'
//
//    def render_target_name(self, status, module, href=None):
//        if status == 'not installed':
//            return f'<button class="button is-link" title="{status}" disabled>Open {module}</button> <br /> <div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-light">{status} <a onclick="installModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-download" title="install"></i></a></span></div>'
//        elif status == 'running':
//            return f'<a class="button is-link" href="{href}" target="_blank" title="{status}">Open {module}</a> <br /> <div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-success">{status}</span></i></a></span></div>'
//        elif status == 'stopped':
//            return f'<button class="button is-link" title="{status}" disabled>Open {module}</button> <br /> <div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-danger">{status}<a class="has-text-light" onclick="startModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-running" title="run"></i></a></span></div>'
//        else:
//            return module

console.log("katana.js loaded.");