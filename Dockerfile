FROM pandoc/extra

RUN apk update && apk add texlive-full texlive-xetex texlive-luatex
# Installing patch to fix the current version of the pandoc_fignos library
RUN apk add --update --no-cache python3 py3-psutil plantuml graphviz ttf-dejavu patch
# Alias needed by pandoc
RUN ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
# Install Python packages for pandoc
RUN pip3 install --no-cache --upgrade pip setuptools fontawesome pandocfilters pandoc-fignos pandoc-plantuml-filter
# Patch pandoc_fignos
COPY ./core.patch /usr/lib/python3.10/site-packages/pandocxnos
RUN cd /usr/lib/python3.10/site-packages/pandocxnos && patch -p0 < core.patch
