#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
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

"""Uploads a bundle to the alpha track."""

import argparse
import sys
import mimetypes
import httplib2

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

TRACK = 'alpha'  # Can be 'alpha', beta', 'production' or 'rollout'

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')
argparser.add_argument('bundle_file',
                       nargs='?',
                       default='test.aab',
                       help='The path to the bundle file to upload.')


def main(argv):
  # Authenticate and construct service.
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      filename='key.json',
      scopes='https://www.googleapis.com/auth/androidpublisher')
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v3', http=http)

  # Process flags and read their values.
  flags = argparser.parse_args()
  package_name = flags.package_name
  bundle_file = flags.bundle_file

  try:
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    mimetypes.add_type('application/octet-stream', '.aab')

    bundle_response = service.edits().bundles().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=bundle_file).execute()

    print ('Version code {0} has been uploaded'.format(bundle_response['versionCode']))

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=TRACK,
        packageName=package_name,
        body={u'releases': [{
            u'name': u'My first API release',
            u'versionCodes': [bundle_response['versionCode']],
            u'status': u'completed',
        }]}).execute()

    print ('Track {0} is set with releases: {1}'.format(
        track_response['track'], str(track_response['releases'])))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print ('Edit {0} has been committed'.format(commit_request['id']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
