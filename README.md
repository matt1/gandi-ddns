gandi-ddns
==========

Simple quick & dirty script to update DNS A record of your domain dynamically using gandi.net's API.  It is very similar to no-ip and dyndns et al where you can have a domain on the internet which points at your computer's IP address, except it is free (once you have registered the domain) and does not suffer from any forced refreshing etc.  

This was designed specifically with Raspberry Pi servers in mind, but could be used anywhere.  

Every time the script runs it will get the current domain config from gandi.net's API and look for the IP in the A record for the domain (default name for the record is '@' but you can change that if you want to).  It will then get your current external IP from a public "what is my ip" site.  Once it has both IPs it will compare what is in the DNS config vs what your IP is, and update the DNS config for the domain as appropriate so that it resolves to your current IP address.

The configuration is stored in the script directory under the file `config.txt`. The syntax is the standard Python configuration file, and the format is the following:
```
[local]
# gandi.net API (Production) key
apikey = <CHANGE ME>
# Domain
domain = <CHANGE ME>
# A-record name
a_name = @
# TTL (seconds = 5 mintes to 30 days)
ttl = 900
# Production API
api = https://rpc.gandi.net/xmlrpc/
# Host which IP should be changed
host = localhost
```

- Do not forget to replace the values marked with `<CHANGE ME>` with your API key and domain.
- You can have more than one config section (`[local]` above) if you need to update more than one domain/a_name.
- `host` is either `localhost` in which case the script will fetch the current external address, or any other public name. Using an other ddns account will allow you to sync it with Gandi (useful when you are not running on the same IP than the one you want to update).

Usage
-----
You will need to make sure that your domain is registered on gandi.net, and that you are using the gandi.net DNS servers (if you are using the default gandi.net zone for other domains you have on gandi.net, you might want to create a dedicated zone for the domain you will be using).  You'll also need to register for the API to get a key.  

Once you have the production key (not the test environment key) and your domain on gandi.net, edit the 'apikey' and 'domain' variables in the script appropriately.

Once you have done this you can then set up the script to run via crontab:

```
sudo crontab -e
```

Then add the following line so that the script is run after a reboot:

```
@reboot python /home/pi/gandi-ddns.py &
```

And then to make it check for a new IP every 15 mintes you can add:

```
*/15 * * * * python /home/pi/gandi-ddns.py
```
You can then start and/or reload the cron config:

```
sudo /etc/init.d/cron start
sudo /etc/init.d/cron reload

```

FAQ
---
**I am getting a python trace about ```Error on object : OBJECT_FQDN (CAUSE_BADPARAMETER) [string '<change me>' does not match '^(?:(?!-)[-a-zA-Z0-9]{1,63}(?<!-)(\\.|$)){2,}$']```?**

You need to make sure you set the ```domain``` variable to match your domain name (no www), e.g. 'example.com'.

**I am getting a python trace about ```Error on object : OBJECT_STRING (CAUSE_BADPARAMETER) [string 'OmQUMmhelfrbXQyA3R4I6Ma' does not match '^[a-z0-9]{24}$']```?**

You need to make sure you enter the correct gandi.net production API key.

**I am getting a python trace about ```'Error on object : OBJECT_ACCOUNT (CAUSE_NORIGHT) [Invalid API key]```?**

Double-check you got the right gandi.net API key.  Double-check that you are using a production key!
