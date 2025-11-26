#!/usr/bin/env python3
"""
Example: Accessing GOST-protected websites using curl subprocess
"""

import subprocess
import html
import sys


def fetch_gost_site(url):
    """
    Fetch content from a GOST-protected website
    
    Args:
        url: URL of the GOST-protected site
        
    Returns:
        tuple: (success, content)
    """
    try:
        result = subprocess.run(
            ["curl", "-k", "-L", "-s", "--connect-timeout", "10", url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            # Decode HTML entities
            content = html.unescape(result.stdout)
            return True, content
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Request timed out"
    except Exception as e:
        return False, str(e)


def get_certificate_info(hostname):
    """
    Get certificate information from a GOST site
    
    Args:
        hostname: Hostname of the site (without https://)
        
    Returns:
        tuple: (success, certificate_info)
    """
    try:
        # Get certificate
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{hostname}:443", 
             "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0 and "Verification error" not in result.stdout:
            return False, "Failed to connect"
        
        # Parse certificate
        cert_result = subprocess.run(
            ["openssl", "x509", "-text", "-noout"],
            input=result.stdout,
            capture_output=True,
            text=True
        )
        
        return True, cert_result.stdout
        
    except Exception as e:
        return False, str(e)


def search_in_content(content, search_term):
    """
    Search for a term in the content
    
    Args:
        content: Content to search in
        search_term: Term to search for
        
    Returns:
        bool: True if found, False otherwise
    """
    return search_term in content


def main():
    """Example usage"""
    print("=" * 60)
    print("Accessing GOST-Protected Website Example")
    print("=" * 60)
    print()
    
    # Example GOST site
    url = "https://dss.uc-em.ru/"
    hostname = "dss.uc-em.ru"
    
    # Fetch content
    print(f"1. Fetching content from {url}")
    success, content = fetch_gost_site(url)
    
    if success:
        print(f"   ✓ Content fetched successfully ({len(content)} bytes)")
        
        # Search for specific text
        search_term = "КРИПТО-ПРО"
        if search_in_content(content, search_term):
            print(f"   ✓ Found '{search_term}' in content")
        else:
            print(f"   ✗ '{search_term}' not found")
    else:
        print(f"   ✗ Failed to fetch: {content}")
    
    print()
    
    # Get certificate info
    print(f"2. Getting certificate info from {hostname}")
    success, cert_info = get_certificate_info(hostname)
    
    if success:
        print(f"   ✓ Certificate retrieved")
        
        # Extract key information
        for line in cert_info.split('\n'):
            if 'Signature Algorithm' in line and 'GOST' in line:
                print(f"   {line.strip()}")
            elif 'Subject:' in line and 'CN=' in line:
                print(f"   {line.strip()}")
            elif 'Not After' in line:
                print(f"   {line.strip()}")
    else:
        print(f"   ✗ Failed to get certificate: {cert_info}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()




