import cherrypy
import os
import sys
import katanacore
import threading


class KatanaServer(object):

    def __init__(self) -> None:
        super().__init__()
        self.threads = {}

    @cherrypy.expose
    def index(self):
        modules = self.list_modules()
        columns = [
            f'<div class="column"><h2 class="subtitle is-2"><img class="cat-header" src="/images/targets.svg"></img> Targets</h2>{self.build_targets_table(modules.get("targets", []))}</div>',
            f'<div class="column"><h2 class="subtitle is-2"><img class="cat-header" src="/images/tools.svg"></img> Tools</h2>{self.build_tools_table(modules.get("tools", []))}</div>']

        all_columns = ''.join(columns)
        all_links = self.list_external_links()
        return f'<html><head>{all_links}</head><body>' \
               f'<div id="header-section"><div id="header-img-wrap"><img id="header-image" src="/images/katana-logo.svg"></div></div>' \
               f'<section class="section"><div class="container">' \
               f'<div class="columns">{all_columns}</div>' \
               f'<div class="columns"><div class="column"><h2 class="subtitle is-2"><img class="cat-header" src="/images/base-services.svg"></img> Base Services</h2>{self.build_targets_table(modules.get("base", []))}</div></div>' \
               f'</div></section>' \
               f'<section><div id="notifications" class="is-hidden notification"></div></section>' \
               f'<footer class="footer"><div class="content has-text-centered">Katana is part of the open source <a href="https://github.com/SamuraiWTF/samuraiwtf">Samurai WTF Project on GitHub</a>.</div></footer></body></html>'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self, module):
        if self.module_is_busy(module):
            return {'name': module, 'status': 'changing'}
        else:
            return {'name': module, 'status': katanacore.status_module(module)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def start(self, module):
        if not self.module_is_busy(module):
            t = threading.Thread(target=katanacore.start_module, args=(module,))
            self.threads[module] = t
            t.start()
        return {'name': module, 'status': 'changing'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stop(self, module):
        if not self.module_is_busy(module):
            t = threading.Thread(target=katanacore.stop_module, args=(module,))
            self.threads[module] = t
            t.start()
        return {'name': module, 'status': 'changing'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def install(self, module):
        if not self.module_is_busy(module):
            t = threading.Thread(target=katanacore.install_module, args=(module,))
            self.threads[module] = t
            t.start()
        return {'name': module, 'status': 'changing'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def remove(self, module):
        if not self.module_is_busy(module):
            t = threading.Thread(target=katanacore.remove_module, args=(module,))
            self.threads[module] = t
            t.start()
        return {'name': module, 'status': 'changing'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self):
        results = self.list_modules()
        return {'results': results}

    def module_is_busy(self, module):
        if module in self.threads:
            t = self.threads.get(module)
            if t.is_alive():
                return True
            else:
                self.threads.pop(module, None)
                return False
        else:
            return False

    def build_targets_table(self, target_list):
        rows = []
        for module in target_list:
            name = module.get('name')
            actions = self.render_actions_for_status(module.get('status', 'unknown'), name, module.get('href'))
            rendered_name = self.render_target_name(module.get('status', 'unknown'), name, module.get('href'))
            rows.append(
                f'<tr><td id="{name}-name">{rendered_name}</td><td>{module["description"]}</td><td id="{name}-actions">{actions}</td></tr>')
        all_rows = ''.join(rows)
        return f'<table class="table"><tr><th>Name</th><th>Description</th><th>Actions</th></tr>{all_rows}</table>'

    def build_tools_table(self, tool_list):
        rows = []
        for module in tool_list:
            actions = self.render_actions_for_status(module.get('status', 'unknown'), module.get('name'))
            name = module["name"]

            rows.append(
                f'<tr><td id="{name}-name">{name}</td><td>{module["description"]}</td><td id="{name}-actions">{actions}</td></tr>')
        all_rows = ''.join(rows)
        return f'<table class="table"><tr><th>Name</th><th>Description</th><th>Actions</th></tr>{all_rows}</table>'

    def list_modules(self):
        module_list = katanacore.list_modules()
        results = {}
        for module in module_list:
            if module.get_category() not in results:
                results[module.get_category()] = []

            status = katanacore.status_module(module.get_name())
            results[module.get_category()].append(
                {'name': module.get_name(), 'description': module.get_description(), 'status': status,
                 'href': module.get_href()})
        for category in results:
            sorted_list = sorted(results[category], key=lambda i: i['name'])
            results[category] = sorted_list
        return results

    def list_external_links(self):
        links = [
            '<link rel="stylesheet" href="/css/bulma.min.css">',
            '<link rel="stylesheet" href="/css/all.css">',
            '<link rel="stylesheet" href="/css/katana.css">',
            '<script src="/js/axios.min.js"></script>',
            '<script src="/js/katana.js"></script>'
        ]
        return ''.join(links)

    def render_actions_for_status(self, status, module, href=''):
        action_icons = []
        if href is None or len(href) == 0:
            params = f'this, \'{module}\''
        else:
            params = f'this, \'{module}\',\'{href}\''

        if status == 'not installed':
            action_icons.append(
                f'<a onclick="installModule({params})" style="margin-left: 5px;"><i class="fas fa-download fa-lg" title="install"></i></a>')
        if status == 'stopped':
            action_icons.append(
                f'<a onclick="startModule({params})" class="has-text-link" style="margin-left: 5px;"><i class="fas fa-running fa-lg" title="start"></i></a>')
        if status == 'running':
            action_icons.append(
                f'<a onclick="stopModule({params})" class="has-text-danger" style="margin-left: 5px;"><i class="fas fa-hand-paper fa-lg" title="stop"></i></a></span>')
        if status == 'installed' or status == 'stopped':
            action_icons.append(
                f'<a onclick="removeModule({params})" class="has-text-grey" style="margin-left: 5px;"><i class="fas fa-minus-circle fa-lg" title="uninstall"></i></a>')
        all_actions = ''.join(action_icons)
        return f'<p class="control">{all_actions}</p>'

    def render_status(self, status, module):
        if status == 'not installed':
            return f'<div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-light">{status} <a onclick="installModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-download" title="install"></i></a></span></div>'
        elif status == 'running':
            return f'<div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-success">{status}</span></i></a></span></div>'
        elif status == 'stopped':
            return f'<div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-danger">{status}<a class="has-text-light" onclick="startModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-running" title="run"></i></a></span></div>'
        else:
            return f'<div class="tags has-addons status-bar"><span class="tag is-dark">Status</span><span class="tag is-danger">{status}</span></div>'

    def render_target_name(self, status, module, href=None):
        name = "unknown"

        if href is None or len(href) == 0:
            name = module
        elif status == 'not installed':
            name = f'<button class="button is-link" title="{status}" disabled>Open {module}</button>'
        elif status == 'running':
            name = f'<a class="button is-link" href="{href}" target="_blank" title="{status}">Open {module}</a>'
        elif status == 'stopped':
            name = f'<button class="button is-link" title="{status}" disabled>Open {module}</button>'
        else:
            name = f'<button class="button is-link" title="{status}" disabled>Open {module}</button>'

        return f'{name} <br/> {self.render_status(status, module)}'


if __name__ == '__main__':
    PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
    cherrypy.config.update({'server.socket_port': 8087,
                            'server.socket_host': '127.0.0.1',
                            'engine.autoreload.on': len(sys.argv) > 1 and sys.argv[1] == 'dev'})
    conf = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': PATH
        }
    }

    cherrypy.quickstart(KatanaServer(), '/', conf)
