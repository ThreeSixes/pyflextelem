"""
This file is part of pyflextelem (https://github.com/ThreeSixes/pyflextelem).

pyflextelem is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyflextelem is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyflextelem.  If not, see <http://www.gnu.org/licenses/>. 
"""

import json
import urllib
import urllib2
import datetime
from pprint import pprint

class flextelem():
	def __init__(self, destination, token, appName):
		"""
		Notify API of events. Requires a destination URL and auth token.
		"""
		
		# Set token and destination host.
		self.__appName = appName
		self.__token = token
		self.__callDst = destination
	
	def goodDTS(self, dts):
		"""
		Generate a properly-formatted timestamp given a date time object.
		"""
		
		# Create a blank return value.
		retVal = ""
		
		try:
			# Convert the timestamp to a string.
			retVal = str(dts)
			
			# Check the length of the string since frames received on the second sometimes lack the %f portion of the data.
			if (len(retVal) == 19):
				retVal = retVal + ".000000"
		
		except:
			raise
		
		return retVal
	
	def send(self, payload):
		"""
		Send data to receiver. Requires JSON data as a string, returns a dict containing the response.
		"""
		# Set response data.
		respData = {}
		
		# Send this message.
		msg = {'pld': payload}
		
		# Set blank response body.
		respBody = "{}"
		
		# Send our metadata.
		msg.update({
			'meta': {
				'authToken': self.__token,
				'appName': self.__appName,
				'cDts': self.goodDTS(datetime.datetime.utcnow())
			}
		})
		
		try:
			# Set headers and perform request.
			headers = {'content-type': 'application/json'}    
			req = urllib2.Request(self.__callDst, json.dumps(msg), headers)
			
			# Make the request and wait for the body to come back.
			response = urllib2.urlopen(req)
			respBody = response.read()
		
		except urllib2.HTTPError as httpErr:
			# See if we can get the HTTP error string.
			respData.update({'error': True, 'message': str(httpErr)})
		
		except:
			raise
		
		finally:
			try:
				# Try to tack on response data.
				respData.update(json.loads(respBody))
			
			except:
				raise
		
		return respData
