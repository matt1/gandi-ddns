from __future__ import print_function
try:
  from xmlrpc import client as xmlrpclient
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen
  import xmlrpclib as xmlrpclient
import sys

# gandi.net API (Production) key
apikey = '<CHANGE ME>'
# Domain
domain = '<CHANGE ME>'
# A-record name
a_name = '@'
# TTL (seconds = 5 mintes to 30 days)
ttl = 900
# Production API
api = xmlrpclient.ServerProxy('https://rpc.gandi.net/xmlrpc/', verbose=False)
# Used to cache the zone_id for future calls
zone_id = None

def get_zone_id():
	""" Get the gandi.net ID for the current zone version"""
	
	global zone_id
	
	# If we've not already got the zone ID, get it
	if zone_id is None:
		# Get domain info then check for a zone
		domain_info = api.domain.info(apikey,domain)
		current_zone_id = domain_info['zone_id']

		if current_zone_id == 'None':
		  print('No zone - make sure domain is set to use gandi.net name servers.')
		  sys.exit(1)
		
		zone_id = current_zone_id
	
	return zone_id

def get_zone_ip():
	"""Get the current IP from the A record in the DNS zone """

	current_zone = api.domain.zone.record.list(apikey, get_zone_id(), 0)
	ip = '0.0.0.0'
	# There may be more than one A record - we're interested in one with 
	# the specific name (typically @ but could be sub domain)
	for d in current_zone:
	  if d['type'] == 'A'and d['name'] == a_name:
	    ip = d['value']
	  
	return ip

def get_ip():
	""" Get external IP """
	
	try:
	  # Could be any service that just gives us a simple raw ASCII IP address (not HTML etc)
	  result = urlopen("http://ipv4.myexternalip.com/raw", timeout=3).read()
	except Exception:
	  print('Unable to external IP address.')
	  sys.exit(2);
	
	return result.decode()

def change_zone_ip(new_ip):
  """ Change the zone record to the new IP """
  
  zone_record ={'name': a_name, 'value': new_ip, 'ttl':ttl, 'type': 'A'}
  
  new_zone_ver = api.domain.zone.version.new(apikey, get_zone_id())
  
  # clear old A record (defaults to previous verison's
  api.domain.zone.record.delete(apikey, get_zone_id(), new_zone_ver,{'type':'A', 'name': a_name})
  
  # Add in new A record
  api.domain.zone.record.add(apikey, get_zone_id(), new_zone_ver, zone_record)
  
  # Set new zone version as the active zone
  api.domain.zone.version.set(apikey, get_zone_id(), new_zone_ver)


def main():
  zone_ip = get_zone_ip()
  current_ip = get_ip()

  if (zone_ip.strip() == current_ip.strip()):
    sys.exit();
  else:
    print('DNS Mistmatch detected: A-record: ', zone_ip, ' WAN IP: ', current_ip)
    change_zone_ip(current_ip)
    zone_id = None
    zone_ip = get_zone_ip();
    print('DNS A record update complete - set to ', zone_ip)

if __name__ == "__main__":
  main()
