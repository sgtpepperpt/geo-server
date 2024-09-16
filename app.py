from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
import geoip2.database
import geoip2.errors
import logging


def get_client_ip():
    if request.headers.getlist('X-Forwarded-For'):
        return request.headers.getlist('X-Forwarded-For')[0].split(',')[0]
    else:
        return request.remote_addr


app = Flask(__name__)
cors = CORS(app)

GEOIP_DB_PATH = '/var/lib/GeoIP/GeoLite2-City.mmdb'
reader = geoip2.database.Reader(GEOIP_DB_PATH)

def get_geoip_data(ip):
    try:
        response = reader.city(ip)
        return {
            'browser': {
                'userAgent': str(request.user_agent)
            },
            'geoLocation': {
                'ipAddress': ip,
                'countryCode': response.country.iso_code,
                'countryName': response.country.name,
                'city': response.city.name,
                'state': response.subdivisions.most_specific.name,
                'stateCode': response.subdivisions.most_specific.iso_code,
                'continent': response.continent.name,
                'continentCode': response.continent.code,
                'timezone': response.location.time_zone,
                'latitude': response.location.latitude,
                'longitude': response.location.longitude
            }
        }
    except geoip2.errors.AddressNotFoundError:
        return {'error': 'Not found'}


@app.route('/api/ip')
@cross_origin()
def index():
    ip = get_client_ip()
    key = request.args.get('k')

    logging.info(f'Request from {ip}')

    if key != open('key').read():
        abort(404)

    geoip_data = get_geoip_data(ip)
    return jsonify(geoip_data)

if __name__ == '__main__':
    # logging.basicConfig(filename='geo-server.log', level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(debug=False, port=4000)
