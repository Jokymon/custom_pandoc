FROM pandoc/extra

RUN apk update && apk add texlive-full texlive-xetex texlive-luatex
# Installing patch to fix the current version of the pandoc_fignos library
RUN apk add --update --no-cache python3 py3-psutil plantuml graphviz ttf-dejavu patch
# Alias needed by pandoc
RUN ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
# Install Python packages for pandoc
RUN pip3 install --no-cache --upgrade pip setuptools fontawesome pandocfilters pandoc-fignos pandoc-include pandoc-plantuml-filter
# Patch pandoc_fignos
COPY ./core.patch /usr/lib/python3.10/site-packages/pandocxnos
RUN cd /usr/lib/python3.10/site-packages/pandocxnos && patch -p0 < core.patch
# Add additional filters
COPY ./pandoc-wrapfig.py /usr/local/lib/pandoc/filters/
COPY ./pandoc_admon_filter2.py /usr/local/lib/pandoc/filters/
COPY ./parse-html.lua /usr/local/lib/pandoc/filters/

# Add the new pandoc filter directory as parameter to pandoc
ENTRYPOINT ["/usr/local/bin/pandoc", "--data-dir=/usr/local/lib/pandoc/"]
