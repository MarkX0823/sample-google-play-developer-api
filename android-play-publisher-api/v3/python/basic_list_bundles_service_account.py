#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Lists all the bundles for a given app."""

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')

def main():
  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with the Credentials. Note that the first parameter, service_account_name,
  # is the Email address created for the Service account. It must be the email
  # address associated with the key that was created.
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      filename='key.json',
      scopes='https://www.googleapis.com/auth/androidpublisher')
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v3', http=http)

  # Process flags and read their values.
  flags = argparser.parse_args()

  package_name = flags.package_name

  try:

    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    bundles_result = service.edits().bundles().list(
        editId=edit_id, packageName=package_name).execute()

    for bundle in bundles_result['bundles']:
      print ('versionCode: {0}, sha1: {1}, sha256: {2}'.format(
        bundle['versionCode'], bundle['sha1'], bundle['sha256']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main()
