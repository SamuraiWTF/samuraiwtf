vars = ['wsdl', 'endpoint', 'namespace', 'target', 'res', 'host', 'uri',
        'xml', 'soapaction', 'dictionary', 'automate', 'idsevasion', 'config',
        'bauser', 'bapass', 'keyfile', 'certfile', 'proxy', 'proxyport',
        'simultaneous', 'endpoint', 'namespace', 'method', 'parameters',
        'wsdl', 'attacks', 'directory', 'idsevasionopt', 'alternatehost',
        'allparams', 'xmlDosFile', 'wsseuser', 'wssepass'
        ]

confvals = ['host', 'uri', 'xml', 'soapaction', 'dictionary',
            'automate', 'idsevasion', 'bauser', 'bapass', 'keyfile',
            'certfile', 'proxy', 'proxyport', 'simultaneous',
            'endpoint', 'namespace', 'method', 'parameters',
            'wsdl', 'attacks', 'directory', 'idsevasionopt',
            'alternatehost', 'allparams', 'wsseuser', 'wssepass'
            ]

confval = {}
confval['Mode'] = None

confvaloutput = {
                'bauser':'Basic Auth User',
                'bapass':'Basic Auth Password',
                'wsseuser':'WS-Security User',
                'wssepass':'WS-Security Password',
                'keyfile':'Key File',
                'certfile':'Certificate File',
                'proxy':'Proxy Server',
                'proxyport':'Proxy Server port',
                'wsdl':'WSDL URL',
                'simultaneous':'Simultaneous Mode',
                'alternatehost':'Alternate Host',
                'allparams':'Fuzz All Parameters',
                'directory':'Results Directory',
                'automate':'Automatic Fuzzing',
                'idsevasion':'IDS Evasion',
                'idsevasionopt':'IDS Evasion Option',
                'dictionary':'Dictionary from conf file',
                'attacks':'Attack Vector file',
                'soapaction':'Soap Action',
                'uri':'URI', 'host':'Host',
                'parameters':'Parameters',
                'endpoint':'Endpoint',
                'namespace':'Namespace',
                'method':'method',
                'xml':'XML Payload File'
                }

# create each var and set it to None
def initializeVars():
    for var in vars:
        globals()[var] = None
# EOF

# init the dict and create each key and set
# each one to None
def initializeDict():
    for var in vars:
        if var in confvals:
            confval[var] = globals()[var]
# EOF

# push a val on to a key in a dict
def setVar(var,val):
    globals()[var] = val
# EOF