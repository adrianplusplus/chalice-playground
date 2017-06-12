from chalice import Chalice, CognitoUserPoolAuthorizer
from chalice import NotFoundError
from sqlalchemy import *
import json

class AlchemyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj.__class__, DeclarativeMeta):
			# an SQLAlchemy class
			fields = {}
			for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
				data = obj.__getattribute__(field)
				try:
					json.dumps(data) # this will fail on non-encodable values, like other classes
					fields[field] = data
				except TypeError:
					fields[field] = None
			# a json-encodable dict
			return fields
 
connection_string = "mysql://root:@172.31.8.25:3306/the_mec_group"
get_next_line_number_query = '''
                    select * from cd
                    '''
 
db = create_engine(connection_string)
db.echo = False
 


app = Chalice(app_name='helloworld')
app.debug = True

CITIES_TO_STATE = {
    "seattle":"wa",
    "portland":"OR"
    }

OBJECTS = {}

authorizer = CognitoUserPoolAuthorizer(
    'ArgusAviation', header='Authorization',
    provider_arns=['arn:aws:cognito-idp:us-east-2:415718553612:userpool/us-east-2_H8klEUvPX'])


@app.route('/', cors=True)
def index():
    result = db.engine.execute(get_next_line_number_query)
    result2 = [row['description'] for row in result]
    for row in result:
		print("description:", row['description'])
    return result2

@app.route('/cities/{city}', cors=True, authorizer=authorizer)
def state_of_city(city):
    return {'state':CITIES_TO_STATE[city]}

@app.route('/objects/{key}', methods=['GET', 'PUT'], cors=True)
def myobject(key):
    request = app.current_request
    if request.method == 'PUT':
        OBJECTS[key] = request.json_body
    elif request.method == 'GET':
        try:
            return {'key': OBJECTS[key]}
        except KeyError:
            raise NotFoundError(key)
