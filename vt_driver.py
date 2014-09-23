#!/usr/bin/python
""" Simple command-line script to interact with the virustotal-api
(https://github.com/blacktop/virustotal-api). Only the main functionality of
the VirusTotal private API has been implemented.

It doesn't really do anything fancy with the JSON response other than
pretty-printing it to the screen.
"""

from __future__ import print_function

__author__ = 'Adrian Herrera'
__email__ = 'adrian.herrera02@gmail.com'

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    import simplejson as json
except ImportError:
    import json

import argparse
import os
import sys
from virus_total_apis import PrivateApi as VTPrivateAPI

def error(*args):
    """ Prints an error message to stderr and terminates.

    Args:
        args: Variable-length arguments to print in the error message.
    """
    print('ERROR:', *args, file=sys.stderr)
    sys.exit(1)

def parse_args():
    """ Parse the command-line arguments.

    Return:
        The parsed command-line arguments.
    """
    # Construct the main parser
    parser = argparse.ArgumentParser(description=('Interact with the '
                                                  'VirusTotal API.'))
    parser.add_argument('-c', '--config', action='store', default='~/.vtapi',
                        help='Path to the configuration file')
    subparsers = parser.add_subparsers(dest='command')

    # File scan subparser
    file_scan_parser = subparsers.add_parser('file-scan',
        help='Submit a file to be scanned')
    file_scan_parser.add_argument('file', action='store', help='File path')

    # Rescan subparser
    rescan_parser = subparsers.add_parser('rescan',
        help=('Rescan a previously submitted file without having to resubmit, '
              'thus saving bandwidth'))
    rescan_parser.add_argument('hash', nargs='+', action='store',
                               help='List of MD5/SHA1/SHA256 hashes')

    # File report subparser
    file_report_parser = subparsers.add_parser('file-report',
        help='Get file scan results')
    file_report_parser.add_argument('hash', nargs='+', action='store',
                                    help='List of MD5/SHA1/SHA256 hashes')

    # Behaviour subparser
    behaviour_parser = subparsers.add_parser('behaviour',
        help=('Get a report on the behaviour of a file in a sandbox '
              'environment'))
    behaviour_parser.add_argument('hash', action='store',
                                  help='An MD5/SHA1/SHA256 hash')

    # Pcap subparser
    pcap_parser = subparsers.add_parser('pcap',
        help='Get a dump of the network traffic generated by a file')
    pcap_parser.add_argument('hash', action='store',
                             help='An MD5/SHA1/SHA256 hash')
    pcap_parser.add_argument('-o', '--output-dir', action='store',
                             default=os.getcwd(),
                             help=('Output directory to write downloaded pcap '
                                   'file to'))

    # Search subparser
    search_parser = subparsers.add_parser('search',
        help='Search for files')
    search_parser.add_argument('query', action='store',
                               help=('The search query in accordance with'
                                     'https://www.virustotal.com/intelligence/'
                                     'help/file-search'))

    # File download subparser
    download_parser = subparsers.add_parser('download',
        help='Download a file')
    download_parser.add_argument('hash', action='store',
                                 help='An MD5/SHA1/SHA256 hash')
    download_parser.add_argument('-o', '--output-dir', action='store',
                                 default=os.getcwd(),
                                 help=('Output directory to write downloaded '
                                       'file to'))

    # URL scan subparser
    url_scan_parser = subparsers.add_parser('url-scan',
        help='Submit a URL to be scanned')
    url_scan_parser.add_argument('url', nargs='+', help='URL(s)')

    # URL report subparser
    url_report_parser = subparsers.add_parser('url-report',
        help='Get URL scan results')
    url_report_parser.add_argument('url', nargs='+', help='URL(s)')

    # IP report subparser
    ip_report_parser = subparsers.add_parser('ip-report',
        help='Get information about an IP address')
    ip_report_parser.add_argument('ip', action='store', help='A IPv4 address')

    # Domain report subparser
    domain_report_parser = subparsers.add_parser('domain-report',
        help='Get information about a domain')
    domain_report_parser.add_argument('domain', action='store',
                                      help='A domain name')

    return parser.parse_args()

def parse_config(conf_file):
    """ Parse the config file.

    Args:
        conf_file: Path to the config file to parse.

    Return:
        The API key as recorded in the configuration file.
    """
    if os.path.exists(conf_file):
        config = configparser.SafeConfigParser()
        config.read(conf_file)

        return config.get('vt', 'apikey')
    else:
        error('Config file \'{}\' does not exist'.format(conf_file))

    return None

def pretty_print_json(json_data, output=sys.stdout):
    """ Pretty-print JSON data.

    Args:
        json_data: The JSON data to pretty-print.
        output: A file-like object (stream) to pretty-print the JSON data to.
    """
    print(json.dumps(json_data, sort_keys=True, indent=4), file=output)

def check_num_args(args):
    """ Checks the number of arguments does not exceed the maximum
    allowed by the VirusTotal private API.

    Args:
        hash_list: A list of arguments.
    """
    if len(args) > 25:
        error(('The VT Private API only allows a maximum of 25 arguments to '
               'be specified in a single query'))

def file_scan(virus_total, file_to_scan):
    """ Submit a single file to be scanned by VirusTotal.

    Args:
        virus_total: VirusTotal API object.
        file_to_scan: The file path of a file to scan.
    """
    response = virus_total.scan_file(file_to_scan)
    pretty_print_json(response)

def file_rescan(virus_total, hash_list):
    """ Rescan a file (designated by an MD5/SHA1/SHA256 hash) already uploaded
    to VirusTotal.

    Args:
        virus_total: VirusTotal API object.
        hash_list: A list of MD5/SHA1/SHA256 hashes to be rescanned.
    """
    check_num_args(hash_list)
    response = virus_total.rescan_file(','.join(hash_list))
    pretty_print_json(response)

def file_report(virus_total, hash_list):
    """ Retrieves a concluded scan report for a given file (designated by an
    MD5/SHA1/SHA256 hash).

    Args:
        virus_total: VirusTotal API object.
        hash_list: A list of MD5/SHA1/SHA245 hashes to retrieve scan reports
        for.
    """
    check_num_args(hash_list)
    response = virus_total.get_file_report(','.join(hash_list))
    pretty_print_json(response)

def file_behaviour(virus_total, hash_):
    """ Get the behaviour for a given file (designated by an MD5/SHA1/SHA256
    hash) as it executes in a sandbox.

    Args:
        virus_total: VirusTotal API objet.
        hash_: An MD5/SHA1/SHA256 hash to retrieve a behaviour report for.
    """
    response = virus_total.get_file_behaviour(hash_)
    pretty_print_json(response)

def network_traffic(virus_total, hash_, output_dir):
    """ Get the network traffic for a given file (designated by an MD5/SHA1/
    SHA256 hash) as it executes in a sandbox.

    Args:
        virus_total: VirusTotal API object.
        hash_: An MD5/SHA1/SHA256 hash to retrieve a pcap file for.
        output_dir: The directory to write the downloaded pcap file to.
    """
    if not os.path.isdir(output_dir):
        error('\'{}\' is not a valid output directory'.format(output_dir))

    response = virus_total.get_network_traffic(hash_)

    # Will return a dict on failure
    if type(response) is dict:
        pretty_print_json(response)
        return

    # Otherwise write the downloaded pcap to disk
    with open(os.path.join(output_dir, hash_ + '.pcap'), 'wb') as out_file:
        out_file.write(response)

def search(virus_total, query):
    """ Search for files.

    Args:
        virus_total: VirusTotal API object.
        query: Search query. The valid search modifiers are described at
        https://www.virustotal.com/intelligence/help/file-search
    """
    response = virus_total.file_search(query)
    pretty_print_json(response)

    # TODO - implement pagenation

def file_download(virus_total, hash_, output_dir):
    """ Download a file designated by an MD5/SHA1/SHA256 hash. Also displays
    the report for the downloaded file.

    Args:
        virus_total: VirusTotal API object.
        hash_: The MD5/SHA1/SHA256 hash of the file to download.
        output_dir: The directory to write the downloaded file to.
    """
    if not os.path.isdir(output_dir):
        error('\'{}\' is not a valid output directory'.format(output_dir))

    response = virus_total.get_file(hash_)

    # Will return a dict on failure
    if type(response) is dict:
        pretty_print_json(response)
        return

    # Otherwise write the downloaded content to disk
    with open(os.path.join(output_dir, hash_), 'wb') as out_file:
        out_file.write(response)

    # Get the report for this sample as well
    file_report(virus_total, [hash_])

def url_scan(virus_total, url_list):
    """ Submit a list of URLs to scan.

    Args:
        virus_total: VirusTotal API object.
        url_list: A list of URLs to scan.
    """
    check_num_args(url_list)
    response = virus_total.scan_url('\n'.join(url_list))
    pretty_print_json(response)

def url_report(virus_total, url_list):
    """ Retrieves a scan report for a given URL.

    Args:
        virus_total: VirusTotal API object.
        hash_list: A list of URLs to retrieve scan reports for.
    """
    check_num_args(url_list)
    response = virus_total.get_url_report('\n'.join(url_list))
    pretty_print_json(response)

def ip_report(virus_total, ip_address):
    """ Retrieves a scan report for a given IP address.

    Args:
        virus_total: VirusTotal API object.
        ip_address: IPv4 address.
    """
    response = virus_total.get_ip_report(ip_address)
    pretty_print_json(response)

def domain_report(virus_total, domain_name):
    """ Retrieves a scan report for a given domain name.

    Args:
        virus_total: VirusTotal API object.
        domain_name: Domain name.
    """
    response = virus_total.get_domain_report(domain_name)
    pretty_print_json(response)

def main():
    """ The main function.

    Parse the command-line arguments and take appropriate action.
    """
    args = parse_args()

    config_file = os.path.expanduser(args.config)
    command = args.command
    api_key = parse_config(config_file)

    if api_key is None:
        error('An API key must be specified in \'{}\''.format(config_file))

    virus_total = VTPrivateAPI(api_key)

    if command == 'file-scan':
        file_scan(virus_total, args.file)
    elif command == 'rescan':
        file_rescan(virus_total, args.hash)
    elif command == 'file-report':
        file_report(virus_total, args.hash)
    elif command == 'behaviour':
        file_behaviour(virus_total, args.hash)
    elif command == 'pcap':
        network_traffic(virus_total, args.hash, args.output_dir)
    elif command == 'search':
        search(virus_total, args.query)
    elif command == 'download':
        file_download(virus_total, args.hash, args.output_dir)
    elif command == 'url-scan':
        url_scan(virus_total, args.url)
    elif command == 'url-report':
        url_report(virus_total, args.url)
    elif command == 'ip-report':
        ip_report(virus_total, args.ip)
    elif command == 'domain-report':
        domain_report(virus_total, args.domain)

if __name__ == '__main__':
    main()
