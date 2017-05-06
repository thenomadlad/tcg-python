# -*- coding: utf-8 -*-

import json

import networkx as nx
from flask import Flask, jsonify, request

from api.forms import ParseForm
from core.chinese_postman_path import ChinesePostmanPath


app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False


@app.route('/parse', methods=['POST'])
def parse():
    """Takes data from form and returns a parsed set of testcases
    :returns: Response
    """
    form = ParseForm.from_json(request.get_json())
    resp = {}
    if form.validate_on_submit():
        mdg = nx.MultiDiGraph()
        data = form.data
        try:
            # add all edges
            for idx, edge in enumerate(data['edges']):
                mdg.add_edge(edge['from_node'], edge['to_node'], key=idx)

            # also add end->start as an edge because we can always start over
            mdg.add_edge(data['end'], data['start'])

            # get the shortest tour and break it up by end->start edges
            sp = ChinesePostmanPath(mdg, data['start'], data['end'])
            paths = [[]]
            for item in sp.shortest_tour:
                if item[0] == data['end'] and item[1] == data['start']:
                    paths.append([])
                else:
                    paths[-1].append([item[0], item[1]])

            resp = {
                'success': True,
                'paths': paths
            }
        except Exception as e:
            error = "Unable to complete request: {}".format(str(e))
            app.logger.error(error, exc_info=e)
            resp = {
                'success': False,
                'error': error
            }

        # verbose gives more info
        if data['verbose']:
            resp['form'] = data
            resp['graph'] = mdg.edges()

    else:
        resp = {
            'success': False,
            'errors': {
                'invalid fields': form.errors
            }
        }

    return jsonify(resp)

if __name__ == "__main__":
    app.run(debug=True)
