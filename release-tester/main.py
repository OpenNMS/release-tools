from library import Common, Docker, Log

from pathlib import Path
import argparse
import json
import re
import sys
import urllib.parse
import os
import tempfile

PRODUCT = ""
VERSION = ""

GENERIC_CONFIGURATIONS = Common.read_configurations("configurations")

LOGGER = Log.Log()


def main():
    parser = argparse.ArgumentParser("Release Tester")
    parser.add_argument(
        "--version",
        "-v",
        default="",
        help="Release version (e.g., 30.0.2 or 2024.0.1)",
    )
    parser.add_argument(
        "--product",
        "-p",
        default="",
        help="Product line (e.g., horizon or meridian)",
        required=True,
    )
    args = parser.parse_args()

    PRODUCT = args.product.casefold()
    VERSION = args.version if args.version else "latest"

    LOGGER.info("main", f"Product: {PRODUCT[0].upper()}{PRODUCT[1:]}")
    LOGGER.info("main", f"Version: {VERSION}")


    if not os.path.exists("workarea"):
        os.mkdir("workarea")

    if PRODUCT == "meridian":
        MERIDIAN_USERNAME = Common.getProperty("MERIDIAN_USERNAME")
        MERIDIAN_PASSWORD = urllib.parse.quote(Common.getProperty("MERIDIAN_PASSWORD"))

    productVersion, productConfiguration = Common.getProductConfiguration(
        PRODUCT, VERSION
    )
    LOGGER.info("main", f"VERSION: {productVersion}")
    OS_TYPE = productConfiguration.keys()
    for OS in OS_TYPE:
        LOGGER.info("main", f"OS_TYPE: {OS}")
        OS_VERSIONS = productConfiguration[OS]
        for VERSION in OS_VERSIONS:
            LOGGER.info("main", f" OS_VERSION: {VERSION}")
            REPOSITORY_URL = productConfiguration[OS][VERSION]
            REPOSITORY_URL = REPOSITORY_URL.replace(
                "REPO_USER", "$MERIDIAN_USERNAME"
            ).replace("REPO_PASS", "$MERIDIAN_PASSWORD")
            LOGGER.debug("main", f"  REPO: {REPOSITORY_URL}")
            OS_IMAGE = GENERIC_CONFIGURATIONS["Operating Systems"][OS][VERSION]

            if OS == "rpm":
                SCRIPT = "rpm.sh"
            elif OS == "deb":
                SCRIPT = "deb.sh"
            else:
                LOGGER.error("main", f"Not sure which script to use for {OS_TYPE}")
                sys.exit(1)

            if PRODUCT == "meridian":
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
                    tmp.write(
                        f"MERIDIAN_USERNAME={MERIDIAN_USERNAME}\nMERIDIAN_PASSWORD={MERIDIAN_PASSWORD}"
                    )
                    tmp_path = tmp.name
                try:
                    # Restrict permissions (owner read/write only)
                    os.chmod(tmp_path, 0o600)

                    for os_name_tag in OS_IMAGE:
                        LOGGER.info("main", f"   OS Image: {os_name_tag}")
                        os_name_tag_string=os_name_tag.split(":")[0].replace("/","_")
                        container = Docker.create_container(
                            image_name=os_name_tag,
                            container_name=f"{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}",
                            container_volumes={
                                os.path.abspath("./templates/rpm.sh"): {
                                    "bind": "/rpm.sh",
                                    "mode": "ro",  # read-only inside container
                                }
                            },
                            detach=True,
                            env_file_path=tmp_path,
                            container_command=f"/rpm.sh -p {PRODUCT} -v {VERSION} -r {REPOSITORY_URL} ",
                        )
                        container.start()
                        waiting = container.wait()
                        exit_code = waiting["StatusCode"]
                        output_logs = container.logs().decode("utf-8")
                        LOGGER.info("main", f"Container exited with code {exit_code}")

                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}.txt", "w"
                        ) as fp:
                            fp.write(output_logs)

                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}.txt", "r"
                        ) as fp:
                            output_logs = fp.readlines()

                        installed_versions = Common.parse_packages(output_logs)
                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}_installed_packages.json",
                            "w",
                        ) as fp:
                            json.dump(installed_versions, fp, indent=4)

                        container.stop()
                        container.remove(force=True)

                finally:
                    # Remove the temp file after use
                    os.remove(tmp_path)

            elif PRODUCT == "horizon":
                    for os_name_tag in OS_IMAGE:
                        LOGGER.info("main", f"   OS Image: {os_name_tag}")
                        os_name_tag_string=os_name_tag.split(":")[0].replace("/","_")
                        container = Docker.create_container(
                            image_name=os_name_tag,
                            container_name=f"{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}",
                            container_volumes={
                                os.path.abspath(f"./templates/{SCRIPT}"): {
                                    "bind": f"/{SCRIPT}",
                                    "mode": "ro",  # read-only inside container
                                }
                            },
                            detach=True,
                            container_command=f"/{SCRIPT} -p {PRODUCT} -v {VERSION} -r {REPOSITORY_URL} ",
                        )
                        container.start()
                        waiting = container.wait()
                        exit_code = waiting["StatusCode"]
                        output_logs = container.logs().decode("utf-8")
                        LOGGER.info("main", f"Container exited with code {exit_code}")

                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}.txt", "w"
                        ) as fp:
                            fp.write(output_logs)

                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}.txt", "r"
                        ) as fp:
                            output_logs = fp.readlines()

                        installed_versions = Common.parse_packages(output_logs)
                        with open(
                            f"workarea/{PRODUCT}_{productVersion}_{OS}_{VERSION}_{os_name_tag_string}_installed_packages.json",
                            "w",
                        ) as fp:
                            json.dump(installed_versions, fp, indent=4)

                        container.stop()
                        container.remove(force=True)


if __name__ == "__main__":
    main()
