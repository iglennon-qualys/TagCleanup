import argparse
import requests
import json

pods = {'US01': 'https://qualysapi.qualys.com',
        'US02': 'https://qualysapi.qg2.apps.qualys.com',
        'US03': 'https://qualysapi.qg3.apps.qualys.com',
        'US04': 'https://qualysapi.qg4.apps.qualys.com',
        'EU01': 'https://qualysapi.qualys.eu',
        'EU02': 'https://qualysapi.qg2.apps.qualys.eu',
        'EU03': 'https://qualysapi.qg3.apps.qualys.eu',
        'UK01': 'https://qualysapi.qg1.apps.qualys.com',
        'IN01': 'https://qualysapi.qg1.apps.qualys.in',
        'CA01': 'https://qualysapi.qg1.apps.qualys.ca',
        'AE01': 'https://qualysapi.qg1.apps.qualys.ae',
        'AU01': 'https://qualysapi.qg1.apps.qualys.au',
        'KSA1': 'https://qualysapi.qg1.apps.qualysksa.com',
        'PRIVATE': ''}

def get_tags(user: str, password: str, base_url: str):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Requested-With': 'Python/requests'}
    auth = (user, password)
    request_url = f'{base_url}/qps/rest/2.0/search/am/tag'
    payload = {
        "ServiceRequest": {
            "filters": {
                "Criteria": [
                    {
                        "field": "ruleType",
                        "operator": "EQUALS",
                        "value": "BUSINESS_INFORMATION"
                    }
                ]
            }
        }
    }
    response = requests.request("POST", request_url, auth=auth, headers=headers, data=json.dumps(payload),
                                verify=False)
    if response.status_code == 200:
        return response['ServiceResponse']['data']
    else:
        print('ERROR: Could not get tags')
        print(f'request URL: {request_url}')
        print(f'response code: {response.status_code}')
        print(f'response text: {response.text}')
        return []

def save_tags(tags: dict, output_filename: str):
    print(f'Writing {output_filename}.json and {output_filename}.txt')
    with open(f'{output_filename}.json', 'w') as f:
        json.dump(tags, f)

    with open(f'{output_filename}.txt', 'w') as f:
        for tag in tags:
            print(f'{tag["Tag"]["id"]}: {tag["Tag"]["name"]}')
            f.write(f'{tag["Tag"]["id"]}: {tag["Tag"]["name"]}\n')
    return

def load_tags(input_filename: str):
    with open(input_filename, 'r') as f:
        tags = json.load(f)
    return tags

def delete_tags(tags: list, output_filename: str, user: str, password: str, pod_url: str):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Requested-With': 'Python/requests'}
    auth = (user, password)

    with open(f'{output_filename}.log', 'w') as f:
        # Build list of Tag IDs
        tag_ids = []
        for tag in tags:
            tag_ids.append(tag['Tag']['id'])

        # build a payload containing the tag IDs, and a filter to use it
        payload = {
            "ServiceRequest": {
                "filters": {
                    "Criteria": [
                        {
                            "field": "id",
                            "operator": "IN",
                            "values": ','.join(tag_ids)
                        }
                    ]
                }
            }
        }
        request_url = f'{pod_url}/qps/rest/2.0/delete/am/tag'
        response = requests.request("POST", request_url, auth=auth, headers=headers, data=json.dumps(payload),
                                    verify=False)
        if response.status_code == 200:
            print("Operation completed successfully")
            return
        else:
            print('ERROR: Error while deleting tags')
            print(f'request payload: {payload}')
            print(f'response code: {response.status_code}')
            print(f'response text: {response.text}')

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-u', '--user', help='user name', required=True)
    args.add_argument('-p', '--password', help='password', required=True)
    args.add_argument('-pod', '--pod_name', help=f'pod url, one of {",".join(pods.keys())}', required=True)
    args.add_argument('-f', '--filename', help='filename for writing/reading (do not include extension)',
                      required=True)
    args.add_argument('-d', '--delete', help='delete tags', action='store_true', default=False)
    args = args.parse_args()
    if args.pod_name and args.pod_name not in pods:
        print('ERROR: pod name does not exist, select from :')
        print(f'[{" | ".join(pods.keys())}]')
        exit(1)
    elif args.pod_name == 'PRIVATE':
        pod_url = input('Please enter the full API Base URL for your private cloud platform: \n')
        if pod_url == '':
            print('ERROR: No URL entered')
            exit(2)
    else:
        pod_url = pods[args.pod_name]

    if args.delete:
        delete_tags(tags=load_tags(input_filename=args.filename), output_filename=args.filename,
                    user=args.user, password=args.password, pod_url=pod_url)
    else:
        tags = get_tags(user=args.user, password=args.password, base_url=pod_url)
        if len(tags) == 0:
            exit(2)
        save_tags(tags=tags, output_filename=args.filename)
    exit(0)
