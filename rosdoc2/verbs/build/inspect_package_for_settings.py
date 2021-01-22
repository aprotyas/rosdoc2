# Copyright 2020 Open Source Robotics Foundation, Inc.
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

import os

from .build_context import BuildContext
from .create_format_map_from_package import create_format_map_from_package
from .parse_rosdoc2_yaml import parse_rosdoc2_yaml

DEFAULT_ROSDOC_CONFIG_FILE = """\
## Default configuration, generated by rosdoc2.

## This 'attic section' self-documents this file's type and version.
type: 'rosdoc2 config'
version: 1

---

settings:
    ## If this is true, a standard index page is generated in the output directory.
    ## It uses the package information from the 'package.xml' to show details
    ## about the package, creates a table of contents for the various builders
    ## that were run, and may contain links to things like build farm jobs for
    ## this package or links to other versions of this package.

    ## If false, you can still include content that would have been in the index
    ## into one of your '.rst' files from your Sphinx project, using the
    ## '.. include::' directive in Sphinx.
    ## For example, you could include it in a custom 'index.rst' so you can have
    ## the standard information followed by custom content.

    ## TODO(wjwwood): provide a concrete example of this (relative path?)

    ## If this is not specified explicitly, it defaults to 'true'.
    generate_package_index: true
builders:
    ## Each stanza represents a separate build step, performed by a specific 'builder'.
    ## The key of each stanza the output subdirectory for that builder instance,
    ## and is relative to the '--output-directory' specified to the tool.
    ## The value of each stanza is a dictionary of settings for the builder that
    ## outputs to that directory.
    ## Required keys in the settings dictionary are 'builder' which determines the
    ## builder executed there, and 'name' which is used when referencing the built
    ## docs from the index.
    'generated/doxygen':
        builder: doxygen
        name: '{package_name} Public C/C++ API'
    '':
        builder: sphinx
        name: '{package_name}'
        ## This path is relative to output stagging.
        doxygen_xml_directory: 'generated/doxygen/xml'
"""


def inspect_package_for_settings(package, tool_options):
    f"""
    Inspect the given package for additional documentation build settings.

    Uses default settings if not otherwise specified by the package.

    If there is a configuration file, then it is used, but if no configuration
    file then a default file is used.

    The default file would look like this:

    {DEFAULT_ROSDOC_CONFIG_FILE}

    :return: dictionary of documentation build settings
    """
    rosdoc_config_file = None
    rosdoc_config_file_name = None
    # Check if the package.xml exports a settings file.
    for export_statement in package.exports:
        if export_statement.tagname == 'rosdoc2':
            config_file_name = export_statement.content
            full_config_file_name = \
                os.path.join(os.path.dirname(package.filename), config_file_name)
            if not os.path.exists(full_config_file_name):
                raise RuntimeError(
                    f"Error rosdoc2 config file '{config_file_name}', "
                    f"from '{package.filename}', does not exist")
            with open(full_config_file_name, 'r') as f:
                # Replace default with user supplied config file.
                rosdoc_config_file = f.read()
            rosdoc_config_file_name = full_config_file_name

    # If not supplied by the user, use default.
    if rosdoc_config_file is None:
        package_map = create_format_map_from_package(package)
        rosdoc_config_file = DEFAULT_ROSDOC_CONFIG_FILE.format_map(package_map)
        rosdoc_config_file_name = '<default config>'

    # Parse config file
    build_context = BuildContext(
        configuration_file_path=rosdoc_config_file_name,
        package_object=package,
        tool_options=tool_options,
    )
    return parse_rosdoc2_yaml(rosdoc_config_file, build_context)
