# reIndexer

## Usage Instructions

1. Install the Technical Analysis Library ([TA-Lib](https://ta-lib.org/)) for your operating system. For macOS, this can be done with brew (see TA-Lib page for other install options).

```bash
$ brew install ta-lib
```

2. Load the appropriate conda environment from the `conda/` folder for your operating system.

```bash
$ conda env create -f conda/{environment/environment-windows}.yml
```

3. Decrypt the configuration file

```bash
$ make decrypt_conf
```

4. Load the configuration file

```bash
$ source config/main.conf
```

TODO: Add notes on how to download data bundles here

- That's it!
