# Python with GOST Cryptographic Engine

Docker image with Python built against OpenSSL with GOST cryptographic algorithms support.

## Overview

This project provides a Python environment with full support for Russian GOST cryptographic standards (GOST R 34.10-2012, GOST R 34.11-2012) through OpenSSL GOST engine integration.

## Sources

- **GOST Engine**: [gost-engine](https://github.com/gost-engine/engine) - Reference implementation of GOST cryptographic algorithms for OpenSSL
- **Python**: [CPython 3.12.0](https://www.python.org/downloads/release/python-3120/) - Official Python distribution
- **Base Image**: Alpine Linux (optimized GOST engine build)

## Features

- ✅ Python 3.12.0 compiled with OpenSSL 3.5.4
- ✅ Full GOST cryptographic support
- ✅ Pre-installed packages: `requests`, `urllib3`
- ✅ Utilities: `curl`, `gostsum`, `gost12sum`
- ✅ Optimized multi-stage build
- ✅ Small image size: ~312MB

## Supported GOST Algorithms

- **Signature**: GOST R 34.10-2012 (256/512 bit)
- **Hash**: GOST R 34.11-2012 (Streebog 256/512 bit)
- **Encryption**: GOST 28147-89, Kuznyechik, Magma
- **Key Exchange**: VKO GOST R 34.10-2012

## Building

### Prerequisites

1. Build the base GOST engine image:
```bash
cd ../engine
docker build -f docker/Dockerfile.alpine -t engine:alpine-optimized .
```

2. Build Python image:
```bash
cd python-gost-engine
docker build -t python-gost-engine:latest .
```

### Build Arguments

- `PYTHON_VERSION` - Python version to build (default: 3.12.0)
- `GOST_ENGINE_REPO` - GOST engine repository URL (default: https://github.com/gost-engine/engine)
- `GOST_ENGINE_BRANCH` - GOST engine branch or tag (default: master)

Example:
```bash
docker build --build-arg PYTHON_VERSION=3.11.10 -t python-gost-engine:3.11 .
docker build --build-arg GOST_ENGINE_BRANCH=v3.0.0 -t python-gost-engine:latest .
```

## Usage

### Basic Python Usage

```bash
# Run Python interpreter
docker run --rm -it python-gost-engine python3

# Check Python version
docker run --rm python-gost-engine python3 --version

# Check OpenSSL version
docker run --rm python-gost-engine python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### Running Scripts

```bash
# Run a Python script
docker run --rm -v $(pwd):/app python-gost-engine python3 script.py

# Interactive mode with volume mount
docker run --rm -it -v $(pwd):/app python-gost-engine bash
```

### Accessing GOST-Protected Websites

Due to Python's SSL module limitations with GOST, use `curl` via subprocess:

```python
import subprocess
import html

# Access GOST-protected site
result = subprocess.run(
    ["curl", "-k", "-L", "-s", "https://example-gost-site.ru/"],
    capture_output=True,
    text=True
)

content = html.unescape(result.stdout)
print(content)
```

See `examples/` directory for more examples.

## Testing

Run the test suite:

```bash
# Run all tests
docker run --rm -v $(pwd)/tests:/tests python-gost-engine python3 -m pytest /tests

# Run specific test
docker run --rm python-gost-engine python3 tests/test_gost.py
```

## Architecture

### Multi-Stage Build

1. **Builder Stage**: 
   - Installs build dependencies
   - Compiles Python from source with OpenSSL GOST support
   - Installs Python packages

2. **Final Stage**:
   - Minimal runtime dependencies
   - Copies compiled Python and libraries
   - Configured GOST engine

### Directory Structure

```
python-gost-engine/
├── Dockerfile           # Multi-stage build definition
├── README.md           # This file
├── tests/              # Test suite
│   ├── test_gost.py   # GOST functionality tests
│   └── test_ssl.py    # SSL/TLS tests
└── examples/          # Usage examples
    ├── basic_usage.py
    ├── gost_site.py
    └── certificate_check.py
```

## Environment Variables

- `LD_LIBRARY_PATH=/usr/local/lib` - Python shared library path
- `OPENSSL_CONF=/etc/ssl/openssl.cnf` - OpenSSL configuration with GOST engine

## Limitations

- Direct HTTPS requests via Python's `ssl` module to GOST-only sites require additional SSL context configuration
- Recommended approach: Use `subprocess` with `curl` for GOST sites
- Some Python packages may not work with GOST certificates without custom adapters

## Performance

- **Build time**: ~6 minutes (with optimizations)
- **Image size**: 312 MB
- **Base image**: 12.8 MB (optimized GOST engine)

## Security Considerations

- Built with `--enable-optimizations` for production use
- Uses official Python sources with checksum verification
- GOST engine from official repository
- Regular security updates recommended

## Troubleshooting

### Python SSL Module Issues

If you encounter SSL errors with GOST sites:
```python
# Use subprocess with curl instead
import subprocess
result = subprocess.run(['curl', '-k', 'https://site.ru'], capture_output=True)
```

### Module Not Found Errors

Ensure `LD_LIBRARY_PATH` is set:
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project follows the licensing of its components:
- GOST Engine: Apache 2.0 / OpenSSL License
- Python: PSF License
- Alpine Linux: Various open-source licenses

## References

- [GOST Engine Documentation](https://github.com/gost-engine/engine)
- [Russian Cryptographic Standards](https://tc26.ru/)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [Python SSL Module](https://docs.python.org/3/library/ssl.html)
- [TK26 TLS Recommendations](https://cryptopro.ru/sites/default/files/products/tls/tk26tls.pdf) - Recommendations for using GOST 28147-89 encryption algorithms in TLS protocol
- [TLS 1.2 and New GOST (Habr)](https://habr.com/ru/articles/339978/) - Overview of GOST cryptographic algorithms in TLS 1.2 protocol

## Version History

- **1.0.0** - Initial release with Python 3.12.0 and OpenSSL 3.5.4




