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

    ## This setting is relevant mostly if the standard Python package layout cannot
    ## be assumed for 'sphinx-apidoc' invocation. The user can provide the path
    ## (relative to the 'package.xml' file) where the Python modules defined by this
    ## package are located.
    python_source: '{package_name}'

    ## This setting, if true, attempts to run `doxygen` and the `breathe`/`exhale`
    ## extensions to `sphinx` regardless of build type. This is most useful if the
    ## user would like to generate C/C++ API documentation for a package that is not
    ## of the `ament_cmake/cmake` build type.
    run_doxygen: false

    ## This setting, if true, attempts to run `sphinx-apidoc` regardless of build
    ## type. This is most useful if the user would like to generate Python API
    ## documentation for a package that is not of the `ament_python` build type.
    run_sphinx_apidoc: false
builders:
    ## Each stanza represents a separate build step, performed by a specific 'builder'.
    ## The key of each stanza is the builder to use; this must be one of the
    ## available builders.
    ## The value of each stanza is a dictionary of settings for the builder that
    ## outputs to that directory.
    ## Required keys in the settings dictionary are:
    ##  * 'output_dir' - determines the output subdirectory for that builder instance relative to --output-directory
    ##  * 'name' - used when referencing the built docs from the index.

    - doxygen: {{
        name: '{package_name} Public C/C++ API',
        output_dir: 'generated/doxygen'
    }}
    - sphinx: {{
        name: '{package_name}',
        ## This path is relative to output staging.
        doxygen_xml_directory: 'generated/doxygen/xml',
        output_dir: ''
    }}
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
