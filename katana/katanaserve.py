import cherrypy
import os
import sys
import katanacore


class KatanaServer(object):

    @cherrypy.expose
    def index(self):
        modules = self.list_modules()
        columns = [
            f'<div class="column"><h2 class="subtitle is-2">Targets</h2>{self.build_targets_table(modules.get("targets", []))}</div>',
            f'<div class="column"><h2 class="subtitle is-2">Tools</h2>{self.build_tools_table(modules.get("tools", []))}</div>']

        all_columns = ''.join(columns)
        all_links = self.list_external_links()
        return f'<html><head>{all_links}</head>' \
               f'<body><section class="section"><div class="container">' \
               f'<h1 class="title is-1">Katana</h1><div class="columns">{all_columns}</div>' \
               f'</div></section></body></html>'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self, module):
        return {'name': module, 'status': katanacore.status_module(module)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def start(self, module):
        katanacore.start_module(module)
        return {'name': module}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stop(self, module):
        katanacore.stop_module(module)
        return {'name': module}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def install(self, module):
        katanacore.install_module(module)
        return {'name': module}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def remove(self, module):
        katanacore.remove_module(module)
        return {'name': module}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self):
        results = self.list_modules()
        return {'results': results}

    def build_targets_table(self, target_list):
        rows = []
        for module in target_list:
            status = self.list_icons_for_status(module.get('status', 'unknown'), module.get('name'))
            if module.get('href') is None or module.get('status', 'unknown') != "running":
                name = module["name"]
            else:
                name = f'<a href="{module["href"]}" target="_blank">{module["name"]}</a>'
            rows.append(
                f'<tr><td>{name}</td><td>{module["description"]}</td><td>{status}</td></tr>')
        all_rows = ''.join(rows)
        return f'<table class="table"><tr><th>Name</th><th>Description</th><th>Status</th></tr>{all_rows}</table>'

    def build_tools_table(self, tool_list):
        rows = []
        for module in tool_list:
            status = self.list_icons_for_status(module.get('status', 'unknown'), module.get('name'))
            name = module["name"]

            rows.append(
                f'<tr><td>{name}</td><td>{module["description"]}</td><td>{status}</td></tr>')
        all_rows = ''.join(rows)
        return f'<table class="table"><tr><th>Name</th><th>Description</th><th>Status</th></tr>{all_rows}</table>'

    def list_modules(self):
        module_list = katanacore.list_modules()
        results = {}
        for module in module_list:
            if module.get_category() not in results:
                results[module.get_category()] = []

            status = katanacore.status_module(module.get_name())
            results[module.get_category()].append(
                {'name': module.get_name(), 'description': module.get_description(), 'status': status, 'href': module.get_href()})
        for category in results:
            sorted_list = sorted(results[category], key=lambda i: i['name'])
            results[category] = sorted_list
        return results

    def list_external_links(self):
        links = [
            '<link rel="stylesheet" href="/css/bulma.min.css">',
            '<link rel="stylesheet" href="/css/all.css">',
            '<script src="/js/axios.min.js"></script>',
            '<script src="/js/katana.js"></script>'
        ]
        return ''.join(links)

    def list_icons_for_status(self, status, module):
        if status == 'installed':
            return f'<span class="icon has-text-success"><i class="fas fa-check-square" title="{status}"></i>' \
                   f'<a onclick="removeModule(this, \'{module}\')" style="margin-left: 5px;" class="delete" title="uninstall"></a></span>'
        elif status == 'not installed':
            return f'<span><a onclick="installModule(this, \'{module}\')" style="margin-left: 5px;"><i class="fas fa-download fa-border" title="install"></i></a></span>'
        elif status == 'stopped':
            return f'<span class="icon has-text-danger"><i class="fas fa-hand-paper" title="{status}"></i>' \
                   f'<a onclick="startModule(this, \'{module}\')" class="has-text-success" style="margin-left: 5px;"><i class="fas fa-play fa-border" title="start"></i></a>' \
                   f'<a onclick="removeModule(this, \'{module}\')" style="margin-left: 5px;" class="delete" title="uninstall"></a></span>'
        elif status == 'running':
            return f'<span class="icon has-text-success"><i class="fas fa-running" title="{status}"></i>' \
                   f'<a onclick="stopModule(this, \'{module}\')" class="has-text-danger" style="margin-left: 5px;"><i class="fas fa-stop fa-border" title="start"></i></a></span>'
        else:
            return status


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
