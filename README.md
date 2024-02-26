# Custom docker image for building Pandoc-based PDFs

## Building the image

```
docker build -t custom_pandoc:latest .
```

## Using the image

```
docker run --rm --volume ".:/data" custom_pandoc:latest document.md -o document.pdf
```
