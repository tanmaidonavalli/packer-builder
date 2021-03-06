"""packer_builder/specs/builders/distro.py"""

import os
import jinja2
from packer_builder.specs.builders.distros.alpine import alpine_spec
from packer_builder.specs.builders.distros.centos import centos_spec
from packer_builder.specs.builders.distros.debian import debian_spec
from packer_builder.specs.builders.distros.fedora import fedora_spec
from packer_builder.specs.builders.distros.freenas import freenas_spec
from packer_builder.specs.builders.distros.ubuntu import ubuntu_spec

# pylint: disable=too-many-locals


def distro_builder(**kwargs):
    """Distro specific builder specs."""

    # Setup vars from kwargs
    builder = kwargs['data']['builder']
    builder_spec = kwargs['data']['builder_spec']
    distro = kwargs['data']['distro']
    distro_spec = kwargs['data']['distro_spec']
    http_dir = kwargs['data']['http_dir']
    script_dir = kwargs['data']['script_dir']
    version = kwargs['data']['version']

    # Define username, password from distro spec
    username = distro_spec['username']
    password = distro_spec['password']

    # Check to ensure http_dir exists in build dir
    if not os.path.isdir(http_dir):
        os.makedirs(http_dir)

    # Define data to pass as kwargs to distro mapping function
    data = {'builder': builder, 'builder_spec': builder_spec, 'distro': distro,
            'version': version}

    # Define distro map to function
    distro_map = {'alpine': alpine_spec,
                  'centos': centos_spec, 'debian': debian_spec,
                  'fedora': fedora_spec, 'freenas': freenas_spec,
                  'ubuntu': ubuntu_spec}

    # Get distro mapping function
    distro_mapping = distro_map[distro]
    # Execute distro mapping function
    bootstrap_cfg, builder_spec = distro_mapping(data=data)

    # If bootstrap config is not none generate config from Jinja2 template
    if bootstrap_cfg is not None:
        # Define Jinja2 template directory
        j2_template_dir = os.path.join(
            script_dir, 'http', distro)
        # Define Jinja2 template
        j2_template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(j2_template_dir),
            trim_blocks=True)
        # Render Jinja2 template
        bootstrap_template = j2_template.get_template(
            bootstrap_cfg + '.j2').render(username=username,
                                          password=password)
        # Define bootstrap file
        bootstrap_file = os.path.join(
            http_dir,
            f'{distro}-{version}-{bootstrap_cfg}')

        # Remove existing bootstrap file if it exists
        if os.path.isfile(bootstrap_file):
            os.remove(bootstrap_file)

        # Write new bootstrap file
        with open(bootstrap_file, 'w') as bootstrap_cfg:
            bootstrap_cfg.write(bootstrap_template)
            bootstrap_cfg.close()
