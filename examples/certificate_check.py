#!/usr/bin/env python3
"""
Example: Checking GOST certificate properties
"""

import subprocess
import sys


def check_certificate(hostname, port=443):
    """
    Check certificate properties for a GOST site
    
    Args:
        hostname: Hostname to check
        port: Port number (default: 443)
    """
    print(f"Checking certificate for {hostname}:{port}")
    print("-" * 60)
    
    try:
        # Get certificate
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{hostname}:{port}", 
             "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse certificate
        cert_result = subprocess.run(
            ["openssl", "x509", "-text", "-noout"],
            input=result.stdout,
            capture_output=True,
            text=True
        )
        
        if cert_result.returncode == 0:
            parse_certificate_info(cert_result.stdout)
        else:
            print("Failed to parse certificate")
            
    except Exception as e:
        print(f"Error: {e}")


def parse_certificate_info(cert_text):
    """Parse and display certificate information"""
    
    info = {
        'subject': None,
        'issuer': None,
        'not_before': None,
        'not_after': None,
        'signature_algorithm': None,
        'public_key_algorithm': None,
    }
    
    for line in cert_text.split('\n'):
        line = line.strip()
        
        if line.startswith('Subject:'):
            info['subject'] = line.replace('Subject:', '').strip()
        elif line.startswith('Issuer:'):
            info['issuer'] = line.replace('Issuer:', '').strip()
        elif 'Not Before:' in line:
            info['not_before'] = line.split('Not Before:')[1].strip()
        elif 'Not After' in line and ':' in line:
            parts = line.split(':')
            if len(parts) > 1:
                info['not_after'] = ':'.join(parts[1:]).strip()
        elif line.startswith('Signature Algorithm:'):
            info['signature_algorithm'] = line.replace('Signature Algorithm:', '').strip()
        elif 'Public Key Algorithm:' in line:
            info['public_key_algorithm'] = line.split(':')[1].strip()
    
    # Display
    print(f"Subject: {info['subject']}")
    print(f"Issuer: {info['issuer']}")
    print(f"Valid From: {info['not_before']}")
    print(f"Valid Until: {info['not_after']}")
    print(f"Signature Algorithm: {info['signature_algorithm']}")
    print(f"Public Key Algorithm: {info['public_key_algorithm']}")
    
    # Check if GOST
    is_gost = False
    if info['signature_algorithm'] and 'GOST' in info['signature_algorithm']:
        is_gost = True
        print("\n✓ This is a GOST certificate")
    else:
        print("\n✗ This is not a GOST certificate")
    
    return is_gost


def main():
    """Example usage"""
    print("=" * 60)
    print("GOST Certificate Checker")
    print("=" * 60)
    print()
    
    # Example GOST sites
    sites = [
        "dss.uc-em.ru",
    ]
    
    for site in sites:
        check_certificate(site)
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()




