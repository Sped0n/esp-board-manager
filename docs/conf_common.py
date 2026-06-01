# type: ignore
# -*- coding: utf-8 -*-

from esp_docs.conf_docs import *  # noqa: F403,F401

extensions += ['sphinx_copybutton',
               # Render Mermaid diagrams (client-side JS, no mmdc required).
               'sphinxcontrib.mermaid',
               'esp_docs.esp_extensions.dummy_build_system',
               'esp_docs.esp_extensions.run_doxygen',
               ]

languages = ['en', 'zh_CN']

# link roles config
project_homepage = 'https://github.com/espressif/esp-board-manager'
github_repo = 'espressif/esp-board-manager'

# context used by sphinx_idf_theme
html_context['github_user'] = 'espressif'
html_context['github_repo'] = 'esp-board-manager'

html_static_path = ['../_static']

# Extra options required by sphinx_idf_theme
project_slug = 'esp-board-manager'
pdf_file_prefix = u'esp-board-manager'

# Contains info used for constructing target and version selector
# Can also be hosted externally, see esp-idf for example
versions_url = './_static/docs_version.js'

# Enable API hover tooltips on :c:/:cpp: cross-reference links.
esp_hover_api_enable = True

# Mermaid: render diagrams client-side via the Mermaid JS library bundled by
# sphinxcontrib-mermaid. This avoids any dependency on the 'mmdc' CLI tool,
# which is not available in the CI environment. The 'raw' format keeps the
# directive content as-is in HTML so the browser-side mermaid.js can render it.
mermaid_output_format = 'raw'
