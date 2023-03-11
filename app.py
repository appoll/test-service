# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
from types import FrameType

from flask import Flask

from utils.logging import logger
from google.cloud import pubsub_v1

app = Flask(__name__)


@app.route("/")
def hello() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # https://cloud.google.com/run/docs/logging#correlate-logs
    logger.info("Child logger with trace Id.")
    
    publisher = pubsub_v1.PublisherClient()
    staging_project = "ovy-staging"
    sub_notifications_topic_ios_staging = "sub-notifications-queue-ios-staging"

    topic_path_ios_staging = publisher.topic_path(staging_project, sub_notifications_topic_ios_staging)
    
        # Check Pub Sub permissions
    permissions_to_check = ["pubsub.topics.publish", "pubsub.topics.update"]
    allowed_permissions = publisher.test_iam_permissions(
        request={"resource": topic_path_ios_staging, "permissions": permissions_to_check}
    )

    print(
        "Allowed permissions for topic {}: {}".format(topic_path_ios_staging, allowed_permissions)
    )

    
    return "Hello, World!"


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
