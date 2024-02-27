# Custom docker image for building Pandoc-based PDFs

This docker image is built for some extended use-cases in building Pandoc-based
PDFs. The following features are integrated in this image:

  * PlantUML filter from https://github.com/timofurrer/pandoc-plantuml-filter
    and all tools for running PlantUML
  * Pandoc filter for the wrapfig LaTeX package from
    https://github.com/scotthartley/pandoc-wrapfig
  * The Pandoc include filter from
    https://github.com/DCsunset/pandoc-include
  * The pandoc-fignos package with a patch for Pandoc >= 3.x
  * A self implemented admonition filter to support block-based admonitions

## Building the image

```
docker build -t custom_pandoc:latest .
```

## Using the image

To build a PDF from your markdown document named `document.md`, you can run the
following docker command:

```
docker run --rm --volume ".:/data" custom_pandoc:latest document.md -o document.pdf
```

The `custom_pandoc` image is based on the `pandoc/extra` image and any options
or any functionality of that image is also available in `custom_pandoc`.
