"""Generate Packer templates for offline execution/review."""
import os
import logging
import shutil
from packer_builder.template import Template
from packer_builder.build import Build


# pylint: disable=too-few-public-methods
class Templates():
    """Generate Packer templates without building."""

    def __init__(self, args, distros):
        """Init a thing."""

        self.logger = logging.getLogger(__name__)
        self.distros = distros
        self.build_dir = args.outputdir
        self.password_override = args.password
        self.current_dir = os.getcwd()

    def generate(self):
        """Generate templates and rename them into the defined output dir."""

        # Iterate through defined distros
        for distro, distro_spec in self.distros.items():
            # Iterate through versions defined in distros
            for version, version_spec in distro_spec['versions'].items():
                version = str(version)

                # Define data to pass to class
                data = {'output_dir': self.build_dir,
                        'password_override': self.password_override,
                        'distro': distro, 'distro_spec': distro_spec,
                        'version': version, 'version_spec': version_spec}

                # Generate the template
                template = Template(data=data)
                # Save template for processing
                template.save_template()
                # Validate the generated template
                Build.validate(self)

                # Rename the generated template as distro and version
                generated_template = os.path.join(
                    self.build_dir, 'template.json')
                self.logger.info('Generated %s', generated_template)
                renamed_template = os.path.join(
                    self.build_dir, f'{distro}-{version}.json')  # noqa: E999
                shutil.move(generated_template, renamed_template)
