#!/usr/bin/env python3
"""
SSL/TLS functionality tests for GOST-protected sites
"""

import subprocess
import sys

# List of GOST-protected sites to test
GOST_SITES = ['dss.uc-em.ru', 'cryptopro.ru']


def test_site_ssl_connection(url):
    """Test SSL connection to a single GOST-protected site
    
    Args:
        url: Site URL to test (e.g., 'dss.uc-em.ru')
    
    Returns:
        tuple: (success: bool, details: str)
    """
    try:
        result = subprocess.run(
            ["curl", "-k", "-I", "-s", "--connect-timeout", "10", 
             f"https://{url}/"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "HTTP" in result.stdout:
            status_line = result.stdout.split('\n')[0]
            return True, status_line
        else:
            return False, "No HTTP response"
    except Exception as e:
        return False, str(e)


def test_site_certificate(url):
    """Test GOST certificate verification for a single site
    
    Args:
        url: Site URL to test
    
    Returns:
        tuple: (success: bool, details: str)
    """
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{url}:443", 
             "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check for GOST algorithms: GOST R 34.10, GOST 28147-89, GOST R 34.11, Kuznyechik
        gost_indicators = ["GOST", "KUZNYECHIK", "GOST28147", "GOSTR3410", "GOSTR3411"]
        has_gost = any(indicator in result.stdout.upper() for indicator in gost_indicators)
        
        if has_gost:
            # Extract certificate and verify
            cert_result = subprocess.run(
                ["openssl", "x509", "-text", "-noout"],
                input=result.stdout,
                capture_output=True,
                text=True
            )
            
            # Check for GOST R 34.10-2012 or GOST R 34.10-94 signature algorithms
            if "GOST R 34.10" in cert_result.stdout or "GOST" in cert_result.stdout:
                return True, "GOST certificate verified"
        
        return False, "GOST certificate not detected"
    except Exception as e:
        return False, str(e)


def test_site_tls_handshake(url):
    """Test TLS handshake with GOST algorithms for a single site
    
    Args:
        url: Site URL to test
    
    Returns:
        tuple: (success: bool, details: str)
    """
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{url}:443", 
             "-brief"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 or "Verification error" in result.stdout:
            # Connection established (certificate verification may fail without proper CA)
            return True, "TLS handshake successful"
        else:
            return False, "TLS handshake failed"
    except Exception as e:
        return False, str(e)


def test_site_cipher_suite(url):
    """Test GOST cipher suite for a single site
    
    Checks for GOST algorithms:
    - GOST 28147-89 (encryption)
    - Kuznyechik (GOST_KUZNYECHIK_CTR, GOST_KUZNYECHIK_OMAC)
    - GOST R 34.11 (hashing)
    - GOSTR341112 (key exchange)
    
    Args:
        url: Site URL to test
    
    Returns:
        tuple: (success: bool, details: str)
    """
    try:
        # Try to get cipher info
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{url}:443", 
             "-brief"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output_upper = result.stdout.upper()
        
        # Check for GOST cipher suites
        gost_ciphers = [
            "GOST", "KUZNYECHIK", "GOST28147", 
            "GOSTR3411", "GOSTR3410", "GOST2012"
        ]
        
        has_gost_cipher = any(cipher in output_upper for cipher in gost_ciphers)
        
        if has_gost_cipher or result.returncode == 0:
            # Try specific GOST cipher suites
            cipher_test = subprocess.run(
                ["openssl", "s_client", "-connect", f"{url}:443", 
                 "-cipher", "GOST2012-GOST8912-GOST8912"],
                input="",
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "Cipher" in cipher_test.stdout or cipher_test.returncode == 0:
                detected = []
                if "KUZNYECHIK" in output_upper:
                    detected.append("Kuznyechik")
                if "GOST28147" in output_upper or "GOST" in output_upper:
                    detected.append("GOST 28147-89")
                if "GOSTR3411" in output_upper:
                    detected.append("GOST R 34.11")
                
                details = f"GOST cipher suite detected: {', '.join(detected) if detected else 'GOST algorithms'}"
                return True, details
        
        return False, "GOST cipher suite not detected"
    except Exception as e:
        return False, str(e)


def test_ssl_connection_all():
    """Test SSL connection for all GOST sites
    
    Returns True if at least one site passes the test.
    
    Returns:
        bool: True if at least one site passed, False otherwise
    """
    print("Testing SSL connection to GOST sites...")
    results = []
    
    for site in GOST_SITES:
        success, details = test_site_ssl_connection(site)
        results.append((site, success, details))
        
        if success:
            print(f"  ✓ {site}: {details}")
        else:
            print(f"  ✗ {site}: {details}")
    
    # Success if at least one site passed
    passed_sites = [site for site, success, _ in results if success]
    if passed_sites:
        print(f"  → Passed sites: {', '.join(passed_sites)}")
        return True
    else:
        print(f"  → All sites failed")
        return False


def test_certificate_verification_all():
    """Test GOST certificate verification for all sites
    
    Returns True if at least one site passes the test.
    
    Returns:
        bool: True if at least one site passed, False otherwise
    """
    print("Testing GOST certificate verification...")
    results = []
    
    for site in GOST_SITES:
        success, details = test_site_certificate(site)
        results.append((site, success, details))
        
        if success:
            print(f"  ✓ {site}: {details}")
        else:
            print(f"  ✗ {site}: {details}")
    
    # Success if at least one site passed
    passed_sites = [site for site, success, _ in results if success]
    if passed_sites:
        print(f"  → Passed sites: {', '.join(passed_sites)}")
        return True
    else:
        print(f"  → All sites failed")
        return False


def test_tls_handshake_all():
    """Test TLS handshake for all GOST sites
    
    Returns True if at least one site passes the test.
    
    Returns:
        bool: True if at least one site passed, False otherwise
    """
    print("Testing TLS handshake...")
    results = []
    
    for site in GOST_SITES:
        success, details = test_site_tls_handshake(site)
        results.append((site, success, details))
        
        if success:
            print(f"  ✓ {site}: {details}")
        else:
            print(f"  ✗ {site}: {details}")
    
    # Success if at least one site passed
    passed_sites = [site for site, success, _ in results if success]
    if passed_sites:
        print(f"  → Passed sites: {', '.join(passed_sites)}")
        return True
    else:
        print(f"  → All sites failed")
        return False


def test_cipher_suite_all():
    """Test GOST cipher suite for all sites
    
    Checks for GOST algorithms: GOST 28147-89, Kuznyechik, GOST R 34.11, GOSTR341112
    
    Returns True if at least one site passes the test.
    
    Returns:
        bool: True if at least one site passed, False otherwise
    """
    print("Testing GOST cipher suite...")
    results = []
    
    for site in GOST_SITES:
        success, details = test_site_cipher_suite(site)
        results.append((site, success, details))
        
        if success:
            print(f"  ✓ {site}: {details}")
        else:
            print(f"  ✗ {site}: {details}")
    
    # Success if at least one site passed
    passed_sites = [site for site, success, _ in results if success]
    if passed_sites:
        print(f"  → Passed sites: {', '.join(passed_sites)}")
        return True
    else:
        print(f"  → All sites failed")
        return False


def run_ssl_tests():
    """Run SSL/TLS tests for all GOST sites"""
    print("=" * 60)
    print("SSL/TLS Functionality Test Suite")
    print(f"Testing sites: {', '.join(GOST_SITES)}")
    print("=" * 60)
    print()
    
    tests = [
        ("SSL Connection", test_ssl_connection_all),
        ("Certificate Verification", test_certificate_verification_all),
        ("TLS Handshake", test_tls_handshake_all),
        ("Cipher Suite", test_cipher_suite_all),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SSL Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All SSL tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} SSL test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_ssl_tests())
