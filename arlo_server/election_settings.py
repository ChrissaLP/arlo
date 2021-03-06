from flask import jsonify, request

from arlo_server import app, db
from arlo_server.auth import with_election_access
from arlo_server.models import Election, USState

from util.jsonschema import validate


GET_ELECTION_SETTINGS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "electionName": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "online": {"type": "boolean"},
        "randomSeed": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "riskLimit": {
            "anyOf": [
                {"type": "integer", "minimum": 1, "maximum": 20},
                {"type": "null"},
            ]
        },
        "state": {
            "anyOf": [
                {"type": "string", "enum": [state.value for state in USState]},
                {"type": "null"},
            ]
        },
    },
    "additionalProperties": False,
    "required": ["electionName", "online", "randomSeed", "riskLimit", "state"],
}


PUT_ELECTION_SETTINGS_REQUEST_SCHEMA = GET_ELECTION_SETTINGS_RESPONSE_SCHEMA


@app.route("/election/<election_id>/settings", methods=["GET"])
@with_election_access
def get_election_settings(election: Election):
    response_data = {
        "electionName": election.election_name,
        "online": election.online,
        "randomSeed": election.random_seed,
        "riskLimit": election.risk_limit,
        "state": election.state,
    }

    validate(schema=GET_ELECTION_SETTINGS_RESPONSE_SCHEMA, instance=response_data)

    return jsonify(response_data)


@app.route("/election/<election_id>/settings", methods=["PUT"])
@with_election_access
def put_election_settings(election: Election):
    settings = request.get_json()
    validate(schema=PUT_ELECTION_SETTINGS_REQUEST_SCHEMA, instance=settings)

    election.election_name = settings["electionName"]
    election.online = settings["online"]
    election.random_seed = settings["randomSeed"]
    election.risk_limit = settings["riskLimit"]
    election.state = settings["state"]

    db.session.add(election)
    db.session.commit()

    return jsonify(status="ok")
