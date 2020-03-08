from os import environ
import json
import ast
import redis
import flask
from flask import Flask, Response, request, abort
from flask_cors import CORS, cross_origin


# App configs
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
redis_handle = redis.Redis(host='localhost', port=6379,
                           db=0, charset="utf-8", decode_responses=True)

# Welcome


@app.route('/')
@cross_origin()
def hello():
    return 'Datacenter Manager API'


# List all the Datacenters in your Infrastructure

@app.route('/configs', methods=['GET'])
@cross_origin()
def list():

    # get all data
    datacenter = []
    keys = redis_handle.keys()
    for i in keys:
        datacenter.append(redis_handle.hgetall(i))
    return(json.dumps(datacenter))


# Add new Dataceneter to your cluster

@app.route('/configs', methods=['POST'])
@cross_origin()
def create():

    data = request.get_json(force=True)
    name = data.get("name")
    metadata = data.get("metadata")
    response = {}
    if name and metadata:
        config = {'name': name, 'metadata': metadata}

        redis_handle.hmset(str(name), config)
        return Response(json.dumps(data))
    else:
        response["msg"] = "required configs id not found"
        return Response(json.dumps(response), status=400)


# Query the Datecenter list by name

@app.route('/configs/<name>', methods=['GET'])
@cross_origin()
def get(name):

    response = {}
    datacenter = {}
    keys = redis_handle.keys()
    if str(name) in keys:
        datacenter = redis_handle.hgetall(name)
        return(json.dumps(datacenter))
    else:
        response["msg"] = "required configs id not found"
        return Response(json.dumps(response), status=404)


# Delete a Datacenter from the Infrastructure by name

@app.route('/configs/<name>', methods=['DELETE'])
@cross_origin()
def delete(name):

    response = {}
    keys = redis_handle.keys()
    if str(name) in keys:
        redis_handle.delete(name)
        response["msg"] = "Datacenter deleted"
        return Response(json.dumps(response), status=204)

    else:
        response["msg"] = "required configs not found"
        return Response(json.dumps(response), status=404)

# Patch your Datacenter


@app.route('/configs/<name>', methods=['PATCH'])
@cross_origin()
def update(name):

    response = {}
    data = request.get_json(force=True)
    new_name = data.get("name")
    keys = redis_handle.keys()
    if str(name) in keys:
        datacenter = redis_handle.hgetall(name)
        datacenter['name'] = new_name
        redis_handle.hmset(str(new_name), datacenter)
        return Response(json.dumps(datacenter))

    else:
        response["msg"] = "required config not found"
        return Response(json.dumps(response), status=400)


# Query Datacenter configs by config maps
@app.route('/search', methods=['GET'])
@cross_origin()
def query():

    response = {}
    args = request.args.to_dict(flat=False)

    # parse and validate the query

    for k, v in args.items():
        key = str(k)
        value = str(v)

    value = ast.literal_eval(value)

    if key.split(".")[0] != "metadata":
        response["msg"] = "Bad query"
        return Response(json.dumps(response), status=400)

    if key.split(".")[1] == "monitoring" and key.split(".")[2] != "enabled":
        response["msg"] = "Bad query"
        return Response(json.dumps(response), status=400)

    if key.split(".")[1] == "limits" and key.split(".")[2] != "cpu":
        response["msg"] = "Bad query"
        return Response(json.dumps(response), status=400)

    if len([key.split(".")]) == 3:
        if key.split(".")[3] not in ["enabled", "value"]:
            response["msg"] = "Bad query"
            return Response(json.dumps(response), status=400)

    datacenters = []
    datacenters_match_list = []

    # get all datacenters in the Infrastructure
    for i in redis_handle.keys():
        datacenters.append(redis_handle.hgetall(i))

    # Get the all the matchs
    for config in datacenters:
        metadata = ast.literal_eval(config.get("metadata"))
        monitoring = metadata.get("monitoring")
        limits = metadata.get("limits")
        monitoring_enabled = monitoring.get("enabled")
        cpu = limits.get("cpu")
        cpu_enabled = cpu.get("enabled")
        cpu_value = cpu.get("value")

        # v {'monitoring': {'enabled': 'true'}, 'limits': {'cpu': {'enabled': 'false', 'value': '300m'}}}

        if key.split(".")[1] == "monitoring" and monitoring_enabled == value[0]:

            datacenters_match_list.append(config)

        if key.split(".")[1] == "limits" and key.split(".")[3] == "value" and cpu_value == value[0]:

            datacenters_match_list.append(config)
        if key.split(".")[1] == "limits" and key.split(".")[3] == "enabled" and cpu_enabled == value[0]:
            datacenters_match_list.append(config)

    return(json.dumps(datacenters_match_list))


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5050, debug=True)
