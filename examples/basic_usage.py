#!/usr/bin/env python3
"""
Basic usage examples for Python with GOST support
"""

import ssl
import sys


def check_openssl_version():
    """Check OpenSSL version"""
    print("OpenSSL Version Information")
    print("-" * 40)
    print(f"Version String: {ssl.OPENSSL_VERSION}")
    print(f"Version Info: {ssl.OPENSSL_VERSION_INFO}")
    print(f"SNI Support: {ssl.HAS_SNI}")
    print(f"ALPN Support: {ssl.HAS_ALPN}")
    print()


def list_available_ciphers():
    """List available cipher suites"""
    print("Available Cipher Suites")
    print("-" * 40)
    context = ssl.create_default_context()
    ciphers = context.get_ciphers()
    print(f"Total ciphers: {len(ciphers)}")
    print(f"First 5 ciphers:")
    for cipher in ciphers[:5]:
        print(f"  - {cipher['name']}")
    print()


def check_python_version():
    """Check Python version"""
    print("Python Version Information")
    print("-" * 40)
    print(f"Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print()


def main():
    print("=" * 60)
    print("Python with GOST Support - Basic Information")
    print("=" * 60)
    print()
    
    check_python_version()
    check_openssl_version()
    list_available_ciphers()
    
    print("=" * 60)
    print("For GOST-specific functionality, see gost_site.py")
    print("=" * 60)


if __name__ == "__main__":
    main()




